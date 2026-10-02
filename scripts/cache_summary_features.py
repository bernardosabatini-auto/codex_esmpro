"""Cache only frozen reliable32 features after qualified extraction controls."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.embedding import FinalESMC
from latentfold.precision import inference_precision
from teacher_summary import load_adapter,StreamedSummary,full_summary
from prepare_overfit import sha
from profile_gpu import atomic_json


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('protocol','label_manifest','extraction_report'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('changed '+key)
    if not json.loads(Path(c['extraction_report']).read_text())['qualified']:raise ValueError('unqualified extraction')
    labels=json.loads(Path(c['label_manifest']).read_text());lp=Path(c['label_manifest']).parent/'labels.h5'
    if labels['status']!='complete' or not labels['training_gate_passed'] or sha(lp)!=labels['labels_sha256']:raise ValueError('unqualified labels')
    rows=labels['config']['targets']
    if len(rows)!=32 or len({r['family'] for r in rows})!=32:raise ValueError('wrong panel')
    adapter,identity=load_adapter(a.source/'data/esmfold2_fast')
    if identity!=c['adapter_tensor_sha256']:raise ValueError('teacher weights changed')
    a.output.mkdir(parents=True,exist_ok=False);torch.cuda.set_device(0);torch.set_num_threads(4);torch.cuda.set_per_process_memory_fraction(.85)
    start=time.monotonic();m=dict(status='running',qualified=False,config=c,rows=[],controls=[]);atomic_json(a.output/'manifest.json',m)
    try:
        m['gpu']=torch.cuda.get_device_name(0)
        if 'RTX PRO 6000' not in m['gpu']:raise ValueError('qualified RTX extraction required')
        e=FinalESMC(a.source/'data/esmc6b',precision='fp32');adapter.cuda();stream=StreamedSummary(e,adapter);controlled=set()
        with torch.no_grad(),inference_precision('fp32'),h5py.File(lp) as source,h5py.File(a.output/'features.h5','x') as out:
            for r in rows:
                if time.monotonic()-start>480:raise TimeoutError('feature cache cap')
                ident=r['id'];n=r['length'];length=r['bucket']
                final,summary=stream([r['sequence']],length);historical=source[ident]['esm'][:];error=final[0,:n].cpu().numpy()-historical
                row=dict(id=ident,bucket=length,final_rmse=float(np.sqrt(np.mean(error**2))),final_max_abs=float(np.abs(error).max()))
                if row['final_rmse']>1e-4 or row['final_max_abs']>1e-3:raise ValueError('historical final embedding mismatch: '+str(row))
                if length not in controlled:
                    reference_final,reference_summary=full_summary(e,[r['sequence']],length,adapter);delta=summary-reference_summary
                    control=dict(bucket=length,rmse=float(delta[:,:n].square().mean().sqrt()),max_abs=float(delta[:,:n].abs().max()),final_exact=torch.equal(final,reference_final))
                    if control['rmse']>1e-5 or control['max_abs']>1e-4 or not control['final_exact']:raise ValueError('summary reference failed')
                    m['controls'].append(control);controlled.add(length)
                    del reference_final,reference_summary,delta
                # Both arms retain the exact historical2560D condition. Control
                # projection therefore uses the same historical tensor, not a recast.
                projected=adapter.pair_proj(adapter.pair_input_norm(torch.from_numpy(historical).cuda()))
                g=out.create_group(ident);g.attrs['sequence_sha256']=r['sequence_sha256']
                g.create_dataset('projected_final',data=projected.cpu().numpy());g.create_dataset('teacher_summary',data=summary[0,:n].cpu().numpy())
                m['rows'].append(row);atomic_json(a.output/'manifest.json',m)
        m['peak_reserved_gib']=torch.cuda.max_memory_reserved()/1024**3
        if len(m['rows'])!=32 or controlled!={128,256,384,512} or m['peak_reserved_gib']>80:raise ValueError('incomplete or oversized cache')
        m.update(status='complete',qualified=True,features_sha256=sha(a.output/'features.h5'))
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
