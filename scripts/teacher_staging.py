"""Bounded private-checkpoint staging probe; no changes to model computations."""
import argparse,gc,hashlib,json,os,shutil,tempfile,time
from pathlib import Path
import h5py,numpy as np,torch
from context_flow_generation import audit_worker,identity
from local_checkpoint import copy_verified
from prepare_overfit import sha


def audit(c,full=False):
    audit_worker(c)
    if full:
        for r in c['sources']:
            if sha(r['path'])!=r['sha256']:raise ValueError('Changed staging source')
    spec=json.loads(Path(c['protocol']).read_text());m=json.loads(Path(c['reference_manifest']).read_text());d=json.loads(Path(c['reference_report']).read_text())
    if (not c.get('teacher_staging') or c['spec']!=spec or spec['modes']!=['shared_initial','local_staged','shared_warm']
            or spec['allocation_minutes']!=15 or spec['work_cap_seconds']!=810 or spec['max_atom_difference']!=1e-5
            or m['status']!='complete' or d['status']!='complete' or not d['numerical_parity'] or c['original']!=m['config']
            or Path(c['reference_manifest']).parent.name!=spec['reference_run']
            or d['manifest_sha256']!=sha(c['reference_manifest']) or d['coordinates_sha256']!=sha(c['reference_coordinates'])):
        raise ValueError('Changed archived teacher recipe')
    return spec


def prepare(output):
    root=Path(__file__).resolve().parents[1];base=root/'runs/teacher_coordinates_profile_50324704'
    c=dict(teacher_staging=True,original=json.loads((base/'manifest.json').read_text())['config'],sources=[])
    for k,p in [('protocol',root/'configs/teacher_staging_protocol.json'),('reference_manifest',base/'manifest.json'),
                ('reference_report',root/'reports/teacher_coordinates_profile_50324704.json'),('reference_coordinates',base/'coordinates.h5')]:
        c[k]=str(p);c['sources'].append(dict(path=str(p),sha256=sha(p)))
    c['spec']=json.loads(Path(c['protocol']).read_text())
    c['sources']+=c['original']['teacher_artifacts']+c['original']['external_sources']
    before=[identity(r['path']) for r in c['sources']]
    for r in c['sources']:
        if sha(r['path'])!=r['sha256']:raise ValueError('Changed input during CPU verification')
    if before!=[identity(r['path']) for r in c['sources']]:raise ValueError('Changed input identity')
    c['file_identity']=before;c['config_sha256']=hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest();audit(c)
    with output.open('x') as f:json.dump(c,f,indent=2)
    print('CPU input audit complete',flush=True)


def stage(artifacts,directory):
    directory=Path(directory);directory.mkdir(exist_ok=False)
    if len({Path(r['path']).name for r in artifacts})!=len(artifacts):raise ValueError('Duplicate local artifact name')
    required=sum(Path(r['path']).stat().st_size for r in artifacts)
    if shutil.disk_usage(directory).free<required+2**30:raise ValueError('Insufficient node-local space')
    for r in artifacts:copy_verified(r['path'],directory/Path(r['path']).name,r['sha256'])
    return directory


def run(config,output):
    from profile_gpu import Telemetry,atomic_json
    from latentfold.precision import inference_precision
    from latentfold.teacher import fast_features,load_fast_model
    c=json.loads(config.read_text());spec=audit(c);output.mkdir(exist_ok=False)
    m=dict(status='running',teacher_staging=True,config=c,records=[],loads=[],new_design_attempts=0);start=time.monotonic();telemetry=None
    try:
        torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);torch.use_deterministic_algorithms(True)
        telemetry=Telemetry(output,True);atomic_json(output/'manifest.json',m)
        with tempfile.TemporaryDirectory(prefix='esm-proae-teacher-',dir=os.environ.get('SLURM_TMPDIR') or '/tmp') as local,h5py.File(output/'coordinates.h5','x') as f:
            shared=Path(c['original']['teacher_artifacts'][0]['path']).parent
            for mode in spec['modes']:
                if time.monotonic()-start>spec['work_cap_seconds']:raise TimeoutError('Staging profile cap')
                tick=time.monotonic();copy_seconds=0.;path=shared
                if mode=='local_staged':
                    path=stage(c['original']['teacher_artifacts'],Path(local)/'checkpoint');copy_seconds=time.monotonic()-tick
                load=time.monotonic();model,adapter=load_fast_model(path);torch.cuda.synchronize();load_seconds=time.monotonic()-load
                m['loads'].append(dict(mode=mode,copy_seconds=copy_seconds,load_seconds=load_seconds,total_seconds=copy_seconds+load_seconds,adapter=adapter));atomic_json(output/'manifest.json',m)
                versions=[(n,id(p),p._version) for n,p in model.named_parameters()]
                with torch.no_grad(),inference_precision('fp32'):
                    for i,entry in enumerate(c['original']['entries']):
                        if time.monotonic()-start>spec['work_cap_seconds']:raise TimeoutError('Staging profile cap')
                        torch.manual_seed(entry['seed']);torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic()
                        features=fast_features(entry['sequence']);out=model.fold(**features,num_loops=3,num_sampling_steps=50,num_diffusion_samples=1)
                        value=out.sample_atom_coords.float().cpu().numpy();del out;torch.cuda.synchronize()
                        if versions!=[(n,id(p),p._version) for n,p in model.named_parameters()]:raise ValueError('Teacher weights changed')
                        f[f'{mode}/{i}']=value
                        m['records'].append(dict(mode=mode,index=i,seconds=time.monotonic()-tick,parameters_unchanged=True,
                            rng_after=hashlib.sha256(torch.cuda.get_rng_state().cpu().numpy().tobytes()).hexdigest(),peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                del model,features;gc.collect();torch.cuda.empty_cache();torch.cuda.synchronize();atomic_json(output/'manifest.json',m)
                print(mode,round(copy_seconds+load_seconds,3),flush=True)
        audit(c);m.update(status='complete',coordinates_sha256=sha(output/'coordinates.h5'))
    except BaseException as e:
        m.update(status='failed',error=f'{type(e).__name__}: {e}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(output/'manifest.json',m)


def analyze(run):
    m=json.loads((run/'manifest.json').read_text());c=m['config'];spec=audit(c,full=True)
    if m['status']!='complete':return dict(status='failed',qualified=False,error=m.get('error'))
    modes=spec['modes'];ref=json.loads(Path(c['reference_manifest']).read_text());rng={r['entry_index']:r['rng_after'] for r in ref['records'] if r['arm']=='full' and r['repeat']==0}
    if (len(m['records'])!=24 or {(r['mode'],r['index']) for r in m['records']}!={(s,i) for s in modes for i in range(8)}
            or [r['mode'] for r in m['loads']]!=modes or m['new_design_attempts'] or m['coordinates_sha256']!=sha(run/'coordinates.h5')):
        raise ValueError('Incomplete staging profile')
    parity=[]
    with h5py.File(run/'coordinates.h5',locking=False) as f,h5py.File(c['reference_coordinates'],locking=False) as old:
        if set(f)!=set(modes) or any(set(f[s])!={str(i) for i in range(8)} for s in modes):raise ValueError('Changed output inventory')
        for r in m['records']:
            a,b=f[f"{r['mode']}/{r['index']}"][:],old[f"{r['index']}/full_0"][:]
            if a.shape!=b.shape or not np.isfinite(a).all() or not r['parameters_unchanged']:raise ValueError('Invalid prediction')
            parity.append(dict(mode=r['mode'],index=r['index'],max_atom_difference=float(np.max(np.abs(a-b))),rng_equal=r['rng_after']==rng[r['index']]))
    numerical=all(r['max_atom_difference']<=spec['max_atom_difference'] and r['rng_equal'] for r in parity)
    loads={r['mode']:r['total_seconds'] for r in m['loads']};reduction=1-loads['local_staged']/loads['shared_initial']
    return dict(status='complete',teacher_staging=True,qualified=numerical and reduction>=spec['minimum_initial_load_reduction'],numerical_parity=numerical,
        manifest_sha256=sha(run/'manifest.json'),coordinates_sha256=sha(run/'coordinates.h5'),loads=m['loads'],parity=parity,
        initial_load_reduction=reduction,elapsed_seconds=m['elapsed_seconds'],peak_reserved_GiB=max(r['peak_reserved_bytes'] for r in m['records'])/2**30,
        scope='24 archival folds, one assigned RTX, no new sequence designs. Original scientific precision and sampler. Copy cost included. Load order/cache state confounded; shared_warm is a descriptive control, never a cold-cache claim. A pass licenses an end-to-end replication only.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--prepare',type=Path);p.add_argument('--config',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.prepare:prepare(a.prepare)
    else:run(a.config,a.output)


if __name__=='__main__':main()
