"""Report fresh teacher recurrence without converting predictions into biology."""
import argparse,json
from pathlib import Path
import numpy as np
from latentfold.teacher_states import audited_families,paired_change
from summarize_comparison import hardware


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0]
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    d=dict(status=m['status'],summaries={})
    if m['status']=='complete':
        if len(m['scores'])!=64 or len(m['controls'])!=64:raise ValueError('incomplete recurrence')
        families=audited_families(m['config']);lookup={}
        for mode in ('fixed_trunk','new_trunk'):
            rows=[r for r in m['scores'] if r['mode']==mode]
            if len(rows)!=32 or {r['target_id'] for r in rows}!=set(families) or any(len(r['assignments'])!=32 for r in rows):raise ValueError('incomplete sample coverage')
            d['summaries'][mode]={k:float(np.mean([r[k] for r in rows])) for k in ('valid_fraction','teacher_ca_lddt','valid_teacher_hit_fraction','state_total_variation')}
            d['summaries'][mode].update(coverage32=float(np.mean([r['coverage']['32'] for r in rows])),strict_coverage32=float(np.mean([r['strict_coverage']['32'] for r in rows])),singleton_states=sum(r['singleton_states'] for r in rows),singleton_hits=sum(r['singleton_hits'] for r in rows))
            lookup[mode]={r['target_id']:r for r in rows}
        d['new_minus_fixed']={k:paired_change({i:r[k] for i,r in lookup['new_trunk'].items()},{i:r[k] for i,r in lookup['fixed_trunk'].items()},families=families) for k in ('valid_fraction','valid_teacher_hit_fraction','state_total_variation')}
        d['max_replay_rmsd']=max(r['replay']['max_ca_rmsd'] for r in m['controls']);d['max_original_rmsd']=max(r['original']['max_ca_rmsd'] for r in m['controls'] if 'original' in r)
        d['max_reserved_gib']=max(r['peak_reserved_bytes'] for r in m['batches'])/1024**3
        try:d['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as error:d['hardware']=dict(status='unavailable',error=str(error))
    else:d['error']=m.get('error','Incomplete recurrence')
    lines=['# Fresh teacher-state recurrence','',f"Status: {d['status']}.",'',
           'Both conditions use fresh matched diffusion seeds. Fixed trunk reuses the original stochastic teacher trunk; new trunk changes it. The original training atlas stays frozen. Atlas misses can indicate an incomplete atlas or poor structure and are not automatically invalid biological conformations. Singleton recurrence here uses fresh teacher generation; the earlier87.3% reference only resampled the16 stored teacher labels.','',
           '| Condition | Recall @2A | Recall @1A | Coarse valid | Atlas hit fraction | Teacher CA-lDDT | Empirical state TV | Singleton states hit |',
           '|---|---:|---:|---:|---:|---:|---:|---:|']
    for mode,r in d['summaries'].items():lines.append(f"| {mode} | {r['coverage32']:.5f} | {r['strict_coverage32']:.5f} | {r['valid_fraction']:.5f} | {r['valid_teacher_hit_fraction']:.5f} | {r['teacher_ca_lddt']:.5f} | {r['state_total_variation']:.5f} | {r['singleton_hits']}/{r['singleton_states']} |")
    if 'error' in d:lines+=['',d['error']]
    else:lines+=['',f"Maximum CA RMSD in original-label reproduction: {d['max_original_rmsd']:.6f} A; sampler replay: {d['max_replay_rmsd']:.6f} A. Peak reserved memory: {d['max_reserved_gib']:.2f} GiB."]
    lines+=['','Teacher predictions do not establish biological populations. One new trunk realization is a limited sensitivity check. No training examples or states are removed based on these outcomes.']
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
