"""Paired quality gates for an inference-only solver comparison."""
import argparse,json
from pathlib import Path
import numpy as np
from latentfold.teacher_states import paired_change
from prepare_overfit import sha
from summarize_comparison import hardware


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0];path=run/'manifest.json'
    m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest');d=dict(status=m['status'],summaries={})
    if m['status']=='complete':
        c=m['config']
        if sha(c['selection'])!=c['selection_sha256'] or sha(c['protocol'])!=c['protocol_sha256']:raise ValueError('changed screen protocol')
        rows=json.loads(Path(c['selection']).read_text())['tuning'];families={r['id']:r['family'] for r in rows};settings=json.loads(Path(c['protocol']).read_text())['settings']
        if len(families)!=64 or len(set(families.values()))!=64 or len(m['scores'])!=len(settings)*192 or len(m['controls'])!=len(settings)*4 or m['training_updates_executed']!=0:raise ValueError('incomplete solver screen')
        def scores(name):
            values=[r for r in m['scores'] if r['setting']==name]
            if len(values)!=192 or {r['target_id'] for r in values}!=set(families) or any(sorted(r['sample'] for r in values if r['target_id']==i)!=[0,1,2] for i in families):raise ValueError('incomplete setting')
            return {k:{i:float(np.mean([r[k] for r in values if r['target_id']==i])) for i in families} for k in ('ca_lddt','coarse_valid')}
        expected_controls={(f"{s['solver']}_{s['steps']}_cfg{s['guidance']}",length) for s in settings for length in (128,256,384,512)}
        if {(r['setting'],r['length']) for r in m['controls']}!=expected_controls or any(not np.isfinite(r['ca_rmsd']) or not np.isfinite(r['ca_lddt']) or r['ca_rmsd']>.2 or r['ca_lddt']<.99 for r in m['controls']):raise ValueError('missing or failed batching controls')
        if any(not np.isfinite(r[k]) for r in m['scores'] for k in ('ca_lddt','coarse_valid')):raise ValueError('nonfinite quality scores')
        baseline=scores('euler_25_cfg2')
        for setting in settings:
            name=f"{setting['solver']}_{setting['steps']}_cfg{setting['guidance']}";values=scores(name)
            comparisons={k:paired_change(values[k],baseline[k],families=families) for k in values}
            nfe=setting['steps']*(2 if setting['solver']=='midpoint' else 1)
            d['summaries'][name]=dict(**setting,velocity_evaluations=nfe,network_forwards=nfe*(2 if setting['guidance']!=1 else 1),metrics=comparisons,passed=bool(comparisons['ca_lddt']['ci95'][0]>-.005 and comparisons['coarse_valid']['difference']>=-.01),measured_batch_seconds=sum(r['seconds'] for r in m['batches'] if r['setting']==name))
        d['max_reserved_gib']=max(r['peak_reserved_bytes'] for r in m['batches'])/1024**3
        try:d['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as error:d['hardware']=dict(status='unavailable',error=str(error))
    else:d['error']=m.get('error','Incomplete solver screen')
    lines=['# Inference-only numerical-solver screen','',f"Status: {d['status']}.",'',
           'Same original weights,64 tuning families,three paired seeds,strict FP32 and3-step decoding. References are AFDB predictions. Euler25 CFG2 must reproduce the earlier baseline. All settings and geometry failures remain included.','',
           '| Setting | Velocity evaluations | Network forwards | CA-lDDT | Delta | Paired 95% interval | Valid fraction | Validity delta | Gate |',
           '|---|---:|---:|---:|---:|---|---:|---:|---|']
    for name,r in d['summaries'].items():
        ca=r['metrics']['ca_lddt'];v=r['metrics']['coarse_valid'];lines.append(f"| {name} | {r['velocity_evaluations']} | {r['network_forwards']} | {ca['candidate']:.5f} | {ca['difference']:+.5f} | {ca['ci95']} | {v['candidate']:.5f} | {v['difference']:+.5f} | {r['passed']} |")
    if 'error' in d:lines+=['',d['error']]
    lines+=['','Intervals are unadjusted family bootstraps. Nominal evaluation savings are not measured end-to-end speedups. Passing this screen only permits ensemble quality/diversity and matched resident-latency tests.']
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
