"""Check paired sampler training and all predeclared tuning evaluations."""
import argparse,json
from pathlib import Path
import numpy as np
from summarize_comparison import hardware
from summarize_distillation_campaign import comparison


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0]
    m=json.loads((run/'manifest.json').read_text()) if (run/'manifest.json').exists() else dict(status='failed',error='missing manifest')
    c=m.get('config',{});d=dict(status=m['status'],arm=c.get('arm'),profile_only=c.get('profile_only'),summaries={})
    if m['status']=='complete':
        if m['updates']!=c['updates']:raise ValueError('incomplete updates')
        d.update(training_seconds=sum(r['seconds'] for r in m['batches']),max_reserved_gib=max(r['peak_reserved_bytes'] for r in m['batches'])/1024**3)
        if not c.get('profile_only'):
            ids=sorted(r['id'] for r in json.loads(Path(c['selection']).read_text())['tuning'])
            keys=[(0,25)]+[(step,n) for step in c['evaluation_steps'] for n in (5,10)];values={}
            if len(m['scores'])!=len(keys)*192 or len(m['controls'])!=4*len(keys):raise ValueError('incomplete evaluation')
            for step,n in keys:
                rows=[r for r in m['scores'] if r['step']==step and r['sampling_steps']==n]
                if len(rows)!=192 or {r['target_id'] for r in rows}!=set(ids) or any(sorted(r['sample'] for r in rows if r['target_id']==i)!=[0,1,2] for i in ids):raise ValueError('evaluation coverage mismatch')
                values[step,n]={k:[float(np.mean([r[k] for r in rows if r['target_id']==i])) for i in ids] for k in ('ca_lddt','coarse_valid','tm_after_kabsch')}
            for step,n in keys[1:]:
                d['summaries'][f'{step}_{n}']={k:comparison(v,values[0,25][k]) for k,v in values[step,n].items()}
        try:d['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as error:d['hardware']=dict(status='unavailable',error=str(error))
    else:d['error']=m.get('error','incomplete')
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# Paired sampler training','',f"Status: {d['status']}; arm: {d['arm']}; capacity profile: {d['profile_only']}.",'','Comparisons use the unchanged 25-step CFG2 initialization on the same 64 tuning families and three seeds. Candidate sampling uses CFG1. No new biological-state labels.','', '| Updates and steps | CA-lDDT | Delta | 95% family interval |','|---|---:|---:|---|']
    for key,v in d['summaries'].items():
        r=v['ca_lddt'];lines.append(f"| {key} | {r['candidate_mean']:.5f} | {r['difference']:+.5f} | {r['ci95']} |")
    if 'error' in d:lines+=['',d['error']]
    lines+=['','Require decoded quality, valid state coverage and measured end-to-end speed before promotion. Independent test and reserved confirmation are unscored.']
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
