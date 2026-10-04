"""Paired full-panel geometry contrast; never a designability claim."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from fragment_junction_core import flank_bonds
from extra_fragment_validation_core import load_conditions
from compare_extra_fragment_refolds import clustered
from prepare_overfit import sha


def analyze(report,root):
    d=json.loads(report.read_text());m=json.loads(Path(d['manifest_path']).read_text());c=m['config']
    if (d['status']!='complete' or d['profile_only'] or not d['flank_context'] or not d['numerically_qualified']
            or d['updates']!=2000 or d['manifest_sha256']!=sha(d['manifest_path']) or d['context_flank']!=8):
        raise ValueError('Complete final wider-mask endpoint required')
    base_report=root/'reports/local_closure_canonical_full_20261004.json';base=json.loads(base_report.read_text())
    bp=root/'runs/local_closure_canonical_full_20261004/predictions.h5'
    bm=json.loads(Path(base['manifest_path']).read_text())
    if (base['status']!='complete' or base['profile_only'] or base['manifest_sha256']!=sha(base['manifest_path'])
            or base['predictions_sha256']!=sha(bp) or bm['config']['source_manifest']!=c['flank_baseline_manifest']
            or base['protocol_sha256']!=sha(c['flank_closure_protocol'])):raise ValueError('Different baseline or closure recipe')
    ids=[r['id'] for r in c['selected']];arms=('generated_cond','generated_untrained')
    items=load_conditions(c['fragments'],ids,'c20_center',cohort='train');rows=[]
    for arm in arms:
        for source,records in (('baseline',base['records']),('flank',d['closure_records'])):
            chosen=[r for r in records if r['arm']==arm]
            if len(chosen)!=128 or {(r['target_id'],r['generation_slot']) for r in chosen}!={(i,k) for i in ids for k in range(4)}:
                raise ValueError('Changed full comparison denominator')
    with h5py.File(bp) as f:
        for r in base['records']:
            if r['arm'] not in arms:continue
            ident=r['target_id'];x=f[r['arm']+'/'+ident+'/backbone'][r['generation_slot']]
            edges=flank_bonds(x,items[ident]['start'],20,8)
            rows.append(dict(model='baseline',arm=r['arm'],target_id=ident,slot=r['generation_slot'],
                             eligible=bool(r['qualified_raw'] and edges['all_edges_valid']),complete=bool(r['qualified_raw'])))
    for r in d['closure_records']:
        if r['refold_eligible_geometry']!=(r['qualified_raw'] and r['hidden_flank_bonds']['all_edges_valid']):raise ValueError('Inconsistent hidden-edge qualification')
        rows.append(dict(model='flank',arm=r['arm'],target_id=r['target_id'],slot=r['generation_slot'],
                         eligible=bool(r['refold_eligible_geometry']),complete=bool(r['qualified_raw'])))
    lookup={(r['model'],r['arm'],r['target_id'],r['slot']):r for r in rows};contrasts=[]
    for candidate,reference in [(('flank','generated_cond'),('baseline','generated_cond')),
                                (('flank','generated_cond'),('flank','generated_untrained'))]:
        contrasts.append(dict(candidate=list(candidate),reference=list(reference),
            eligible_difference=clustered([np.mean([int(lookup[*candidate,i,k]['eligible'])-int(lookup[*reference,i,k]['eligible']) for k in range(4)]) for i in ids])))
    summary=[dict(model=model,arm=arm,samples=128,complete_geometry=sum(r['complete'] for r in rows if (r['model'],r['arm'])==(model,arm)),
                  eligible_geometry=sum(r['eligible'] for r in rows if (r['model'],r['arm'])==(model,arm)))
             for model in ('baseline','flank') for arm in arms]
    return dict(status='complete',source_report_sha256=sha(report),baseline_report_sha256=sha(base_report),summary=summary,
                contrasts=contrasts,scope='Same32training proteins x4noises; all outputs retained. Complete local geometry plus every peptide/CAedge in eight flanks. Family bootstrap. This is geometric feasibility, not designability or generalization.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=analyze(a.report,Path(__file__).resolve().parents[1]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    a.output.with_suffix('.md').write_text('# Paired wider-context-mask geometry\n\n```json\n'+json.dumps(d,indent=2)+'\n```\n');print(json.dumps(d))


if __name__=='__main__':main()
