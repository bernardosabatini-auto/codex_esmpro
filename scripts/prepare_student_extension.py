"""Freeze both student128 continuations from qualified parent ensembles."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    protocol=root/'configs/student_extension_protocol.json';recipe=json.loads(protocol.read_text())
    quality=root/'reports/compact_ensemble_comparison.json';q=json.loads(quality.read_text())
    if q['status']!='complete' or not q['sampling_quality_gate_passed']:raise ValueError('parent quality gate failed')
    teacher=root/'runs/state_scores_49629888/score.json';t=json.loads(teacher.read_text())
    if t['status']!='complete':raise ValueError('teacher128 incomplete')
    for name,jid,guidance in (('original','49618816',2),('compact500','49771176',1)):
        path=root/f'runs/ensemble_{jid}/manifest.json';m=json.loads(path.read_text());base=m['config'];scores=root/f'runs/state_scores_{jid}/score.json';s=json.loads(scores.read_text());setting=f'cfg{guidance}/latent'
        ids=sorted(r['target_id'] for r in s['rows'] if r['setting']==setting and r.get('contact_state_count',0)==2)
        if m['status']!='complete' or s['status']!='complete' or len(ids)!=16 or len(set(ids))!=16:raise ValueError('incomplete fixed parent')
        if sha(scores)!=q['reference_sha256' if name=='original' else 'candidate_sha256']:raise ValueError('qualified parent scores changed')
        if any(s['definitions'][i]!=t['definitions'][i] for i in ids):raise ValueError('teacher/student state definitions differ')
        if name=='original':
            identity=json.loads((root/'runs/inference_checkpoints/original459m_ema.ckpt.identity.json').read_text())
            if not identity['tensor_values_verified'] or identity['source_sha256']!=m['checkpoint']['sha256']:raise ValueError('compact original checkpoint identity failed')
            checkpoint=Path(identity['path']);expected=identity['sha256']
        else:checkpoint=Path(base['checkpoint']);expected=base['checkpoint_sha256']
        if sha(checkpoint)!=expected:raise ValueError('checkpoint changed')
        c=dict(name=name,target_ids=ids,seed=base['seed'],guidance=guidance,setting=setting,compact_condition=name=='compact500',samples=recipe['samples'],sample_batch=recipe['sample_batch'],work_cap_seconds=780)
        fields=dict(protocol=protocol,panel=Path(base['panel']),base_manifest=path,base_predictions=path.parent/'predictions.h5',base_scores=scores,teacher_scores=teacher,quality_report=quality,embedding_cache=root/'runs/ensemble_49618816/embeddings.h5',checkpoint=checkpoint,decoder_checkpoint=Path(m['decoder_checkpoint']['path']))
        for key,value in fields.items():c[key]=str(value.resolve());c[key+'_sha256']=sha(value)
        if c['panel_sha256']!=base['panel_sha256'] or c['decoder_checkpoint_sha256']!=m['decoder_checkpoint']['sha256']:raise ValueError('panel or decoder changed')
        out=a.output.with_name(f'{a.output.stem}_{name}.json');out.write_text(json.dumps(c,indent=2)+'\n');print(out)


if __name__=='__main__':main()
