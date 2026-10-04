"""Two private FP32/RNG workers, sequential versus concurrent on one own GPU."""
import argparse
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import time
import h5py
import torch
from latentfold.precision import inference_precision
from latentfold.teacher import fast_features, load_fast_model
from profile_gpu import Telemetry, atomic_json
from teacher_concurrency_core import audit, sha


def worker(conn, original, fraction):
    try:
        torch.set_num_threads(2); torch.cuda.set_device(0)
        torch.cuda.set_per_process_memory_fraction(fraction)
        torch.use_deterministic_algorithms(True)
        model, adapter = load_fast_model(Path(original['teacher_artifacts'][0]['path']).parent)
        before=[(n,id(v),v._version) for n,v in model.named_parameters()]
        conn.send(dict(ready=True, adapter=adapter))
        while True:
            entry=conn.recv()
            if entry is None: break
            with torch.no_grad(), inference_precision('fp32'):
                torch.manual_seed(entry['seed']); torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats()
                tick=time.monotonic(); features=fast_features(entry['sequence'])
                out=model.fold(**features,num_loops=3,num_sampling_steps=50,num_diffusion_samples=1)
                coords=out.sample_atom_coords.float().cpu().numpy(); del out
                torch.cuda.synchronize()
                if before!=[(n,id(v),v._version) for n,v in model.named_parameters()]:
                    raise ValueError('Teacher parameters changed')
                conn.send(dict(coordinates=coords, seconds=time.monotonic()-tick,
                    peak_allocated_bytes=torch.cuda.max_memory_allocated(), peak_reserved_bytes=torch.cuda.max_memory_reserved(),
                    rng_after=hashlib.sha256(torch.cuda.get_rng_state().cpu().numpy().tobytes()).hexdigest(), parameters_unchanged=True))
    except BaseException as e:
        conn.send(dict(error=f'{type(e).__name__}: {e}'))
    finally:
        conn.close()


def receive(conn, process, deadline):
    while time.monotonic()<deadline:
        if conn.poll(.2):
            result=conn.recv()
            if 'error' in result: raise RuntimeError(result['error'])
            return result
        if not process.is_alive(): raise RuntimeError('Own profile worker exited unexpectedly')
    raise TimeoutError('Bounded concurrency profile exhausted')


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    # CPU preparation and independent completion audit hash every large weight.
    # Avoid another24GiB hash scan while holding a GPU; require unchanged exact
    # file metadata captured both before and after the CPU content verification.
    c=json.loads(a.config.read_text()); spec=audit(c,verify_weights=False); a.output.mkdir(exist_ok=False)
    tick=time.monotonic(); deadline=tick+spec['work_cap_seconds']; telemetry=None; children=[]; connections=[]
    m=dict(status='running',config=c,records=[],pairs=[],training_updates_executed=0,new_design_attempts=0)
    atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(1);torch.cuda.set_device(0)
        telemetry=Telemetry(a.output)
        context=mp.get_context('spawn')
        for _ in range(2):
            parent,child=context.Pipe();process=context.Process(target=worker,args=(child,c['original'],spec['memory_fraction_per_worker']))
            process.start();child.close();children.append(process);connections.append(parent)
        m['worker_adapters']=[receive(conn,child,deadline) for conn,child in zip(connections,children)]
        entries=c['original']['entries']
        with h5py.File(a.output/'coordinates.h5','x') as f:
            for pair in range(4):
                for repeat in range(4):
                    modes=('sequential','concurrent') if (pair+repeat)%2==0 else ('concurrent','sequential')
                    for mode in modes:
                        started=time.monotonic()
                        if mode=='concurrent':
                            for k,conn in enumerate(connections):conn.send(entries[2*pair+k])
                            results=[receive(conn,child,deadline) for conn,child in zip(connections,children)]
                        else:
                            results=[]
                            for k,(conn,child) in enumerate(zip(connections,children)):
                                conn.send(entries[2*pair+k]);results.append(receive(conn,child,deadline))
                        seconds=time.monotonic()-started
                        m['pairs'].append(dict(pair=pair,bucket=entries[2*pair]['bucket'],repeat=repeat,mode=mode,seconds=seconds))
                        for k,result in enumerate(results):
                            index=2*pair+k;key=f'{index}/{mode}_{repeat}'
                            f[key]=result.pop('coordinates')
                            m['records'].append(dict(entry_index=index,repeat=repeat,mode=mode,dataset=key,**result))
                        atomic_json(a.output/'manifest.json',m)
                print('profiled',entries[2*pair]['bucket'],flush=True)
        for conn in connections:conn.send(None)
        for child in children:
            child.join(timeout=10)
            if child.is_alive() or child.exitcode!=0:raise RuntimeError('Own worker did not shut down cleanly')
        m.update(status='complete',coordinates_sha256=sha(a.output/'coordinates.h5'))
    except BaseException as e:
        m.update(status='failed',error=f'{type(e).__name__}: {e}');raise
    finally:
        for child in children:
            if child.is_alive():child.terminate()
            child.join(timeout=5)
        for conn in connections:conn.close()
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-tick;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
