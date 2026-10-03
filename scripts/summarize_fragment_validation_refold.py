"""Strict fresh-noise success and diversity with explicitly overlapping views."""
import argparse,itertools,json
from pathlib import Path
import h5py,numpy as np
from fragment_refinement_core import score_assay
from fragment_validation_core import view_rows
from latentfold.fragment_designability import scaffold_rmsd
from latentfold.metrics import usalign_coordinates
from prepare_fragment_validation_refold import audit_inputs
from prepare_overfit import sha


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'))
    c=m['config'];audit_inputs(c);records=score_assay(run);spec=json.loads(Path(c['protocol']).read_text());focus=spec['focus_id'];positive={r['target_id']:r['strict_joint_success'] for r in records if r['arm']=='native'};summaries=[];diversity=[]
    for arm in spec['parents']:
        for view in ('whole_panel','focus'):
            screen=view_rows(c['screen_rows'],arm,view,focus);rr=view_rows(records,arm,view,focus);success=[r for r in rr if r['strict_joint_success']]
            if len(screen)!=(64 if view=='whole_panel' else 16):raise ValueError('Changed view denominator')
            summaries.append(dict(arm=arm,view=view,screened=len(screen),families=len({r['family'] for r in screen}),raw_matches=len(rr),strict_successes=len(success),strict_fraction=len(success)/len(screen),successful_families=len({r['family'] for r in success}),successes_with_passing_native_control=sum(positive[r['target_id']] for r in success),global_designability_of_raw_failures='not measured'))
        success=[r for r in view_rows(records,arm,'focus',focus) if r['strict_joint_success'] and positive[focus]];chosen=[dict(generation_slot=r['generation_slot'],name=r['name'],sequence_index=r['successful_refold_indices'][0]) for r in success];pairs=[]
        with h5py.File(run/'refolded.h5') as refold,h5py.File(c['predictions']) as raw:
            for left,right in itertools.combinations(success,2):
                x=refold[left['name']+'/'+str(left['successful_refold_indices'][0])][:];y=refold[right['name']+'/'+str(right['successful_refold_indices'][0])][:];keep=np.zeros(len(x),dtype=bool);start=left['motif_start'];keep[start:start+len(raw['motifs/'+focus])]=True
                pairs.append(dict(left=left['generation_slot'],right=right['generation_slot'],global_tm=usalign_coordinates(c['usalign'],x[:,1],y[:,1]),motif_aligned_scaffold_rmsd=scaffold_rmsd(x,y,keep)))
        diversity.append(dict(arm=arm,successful_backbones=len(success),chosen_first_qualifying_refolds=chosen,pairs=pairs,mean_global_tm=float(np.mean([r['global_tm'] for r in pairs])) if pairs else None,mean_motif_aligned_scaffold_rmsd=float(np.mean([r['motif_aligned_scaffold_rmsd'] for r in pairs])) if pairs else None))
    return dict(status='complete',manifest_sha256=sha(path),refolded_sha256=sha(run/'refolded.h5'),completed_refolds=len(m['records']),unique_generated_samples=152,overlapping_focus_samples_per_arm=4,native_strict_controls=positive,summaries=summaries,successful_refold_diversity=diversity,records=records,elapsed_seconds=m['elapsed_seconds'],interpretation=spec['scope']+' The64and16sample views overlap; never add their success counts or denominators.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Fresh-noise strict refolding and diversity\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k!='records'},indent=2)+'\n```\n')

if __name__=='__main__':main()
