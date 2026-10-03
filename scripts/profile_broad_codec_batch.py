import argparse,json,time
from pathlib import Path
import h5py,torch
from latentfold.decoder import load_proteinae
from latentfold.precision import inference_precision
from latentfold.fragment_codec_batch import run_codec_batches
from broad_codec_batch_core import items
from prepare_overfit import sha
from profile_gpu import atomic_json


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());data=items(c);a.output.mkdir(exist_ok=False);tick=time.monotonic();m=dict(status='running',config=c,training_updates_executed=0);atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(2);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False)
        with torch.no_grad(),inference_precision('fp32'):results,batches=run_codec_batches(decoder,data,batch_size=c['spec']['batch_size'],seed=c['spec']['seed'],length_multiple=c['spec']['length_multiple'])
        with h5py.File(a.output/'outputs.h5','x') as out:
            for key,value in results.items():
                g=out.create_group(key)
                for name,array in value.items():g.create_dataset(name,data=array)
        if time.monotonic()-tick>c['spec']['work_cap_seconds'] or max(r['peak_reserved_GiB'] for r in batches)>c['spec']['max_reserved_GiB']:raise ValueError('Codec batch resource cap')
        m.update(status='complete',batches=batches,outputs_sha256=sha(a.output/'outputs.h5'))
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:m['elapsed_seconds']=time.monotonic()-tick;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
