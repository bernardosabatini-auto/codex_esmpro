"""Full-coverage checkpoint comparisons, including failed numerical controls."""
import argparse,hashlib,json
from pathlib import Path
from latentfold.metrics import paired_comparison
from summarize_comparison import validate_scores,means_by_target,hardware
from summarize_pilot import geometry_by_target


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=dict(status='complete',runs={},failures=[])
    lines=['# Frozen checkpoint diagnostic','',
        'Predeclared comparison of original training-selected best EMA and final unaveraged weights against final EMA. All 626 development proteins, three fixed samples, 25 steps, guidance 2, strict FP32 and fixed correspondence. No new training or test-set scoring.','',
        '| Checkpoint | TM | Delta vs final EMA [95% cluster CI] | CA lDDT |', '|---|---:|---|---:|']
    for run in a.runs:
        try:
            m=json.loads((run/'manifest.json').read_text())
            if m['status']!='complete':raise ValueError(m.get('error','incomplete collection'))
            s=json.loads((run/'scores.json').read_text());validate_scores(m,s);cfg=m['config']
            if m['checkpoint']['sha256']!=cfg['probe']['checkpoint_sha256']:raise ValueError('candidate checkpoint changed')
            ref=Path(cfg['reference_run']);bm=json.loads((ref/'manifest.json').read_text());bs=json.loads((ref/'scores.json').read_text());validate_scores(bm,bs)
            for key in ['dataset','decoder_checkpoint','precision']:
                if m[key]!=bm[key]:raise ValueError('changed reference '+key)
            for key in ['seed','samples','target_ids','target_manifest_sha256','decoder_steps']:
                if cfg[key]!=bm['config'][key]:raise ValueError('changed reference '+key)
            if s['usalign']!=bs['usalign']:raise ValueError('scorer changed')
            cp=Path(cfg['development_clusters'])
            if hashlib.sha256(cp.read_bytes()).hexdigest()!=cfg['development_clusters_sha256']:raise ValueError('cluster mapping changed')
            clusters=json.loads(cp.read_text())['clusters'];setting='steps25_cfg2'
            paired={metric:paired_comparison(means_by_target(bs['records'],setting,metric),means_by_target(s['records'],setting,metric),clusters=clusters) for metric in ['tm_fixed_reference','ca_lddt']}
            geom={key:paired_comparison(geometry_by_target(bs['records'],key),geometry_by_target(s['records'],key),clusters=clusters) for key in ['predicted_ca_gaps_on_reference_short','peptide_length_outliers_on_reference_short']}
            row=dict(probe=cfg['probe'],paired=paired,geometry=geom,accuracy=s['summaries'][setting])
            try:row['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
            except Exception as error:row['hardware']=dict(status='unavailable',error=str(error))
            result['runs'][run.name]=row;tm=paired['tm_fixed_reference']
            lines.append(f"| {cfg['probe']['name']} | {tm['theirs']:.5f} | {tm['theirs_minus_ours']:+.5f} {tm['ci95']} | {paired['ca_lddt']['theirs']:.5f} |")
        except Exception as error:result['failures'].append(dict(run=str(run),error=f'{type(error).__name__}: {error}'))
    if result['failures']:result['status']='incomplete'
    lines+=['','Results are checkpoint diagnostics, not independent training-seed replications. No original legacy TM score is treated as comparable to the new scorer.','', '```json',json.dumps(result,indent=2),'```']
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
