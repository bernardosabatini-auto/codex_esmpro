"""Check whether native fragment sequences make strict positive controls feasible."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from prepare_fragment_fixed_positive import audit_inputs
from fixed_motif_design import verify_fixed_sequences
from latentfold.fragment_designability import motif_fit,same_refold_success
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.metrics import usalign_coordinates
from prepare_overfit import sha


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest',records=[])
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error','Incomplete'),completed_refolds=len(m['records']))
    c=m['config'];audit_inputs(c);verify_fixed_sequences(m['sequences'],c['entries']);wanted={(r['name'],i) for r in c['entries'] for i in range(8)};index={(r['name'],r['sequence_index']):r for r in m['records']}
    if len(m['records'])!=32 or set(index)!=wanted or len(m['controls'])!=4 or {r['name'] for r in m['controls']}!={r['name'] for r in c['entries']} or any(r['ca_rmsd']>.01 or r['ca_lddt']<.999 for r in m['controls']):raise ValueError('Coverage/teacher repeatability failure')
    baseline=json.loads(Path(c['baseline_report']).read_text());results=[]
    with h5py.File(c['predictions']) as inp,h5py.File(run/'refolded.h5') as f:
        if set(f)!={r['name'] for r in c['entries']}:raise ValueError('Unexpected refold inventory')
        for r in c['entries']:
            raw=inp[r['dataset']][0];fragment=inp['motifs/'+r['target_id']][:];raw_metrics=dict(coarse_valid=bool(backbone_geometry(raw[None])['coarse_valid'][0]),**motif_fit(raw,fragment,int(r['motif_start'])));rows=[]
            if set(f[r['name']])!=set(map(str,range(8))):raise ValueError('Incomplete refold archive')
            for slot in range(8):
                bb=f[r['name']+'/'+str(slot)][:]
                if bb.shape!=raw.shape or not np.isfinite(bb).all():raise ValueError('Invalid archived refold')
                tm=usalign_coordinates(c['usalign'],bb[:,1],raw[:,1])
                if abs(tm-index[(r['name'],slot)]['sc_tm'])>1e-7:raise ValueError('Global score failed audit')
                rows.append(dict(sc_tm=tm,coarse_valid=bool(backbone_geometry(bb[None])['coarse_valid'][0]),**motif_fit(bb,fragment,int(r['motif_start']))))
            previous=next(x for x in baseline['backbones'] if x['head']=='experimental' and x['target_id']==r['target_id']);results.append(dict(target_id=r['target_id'],family=r['family'],raw=raw_metrics,refolds=rows,free_strict_success=previous['strict_joint_success'],**same_refold_success(raw_metrics,rows)))
    return dict(status='complete',completed_refolds=32,fixed_strict_success=sum(r['strict_joint_success'] for r in results),free_strict_success=sum(r['free_strict_success'] for r in results),fixed_valid_designable=sum(r['valid_designable'] for r in results),backbones=results,elapsed_seconds=m['elapsed_seconds'],mpnn_seconds=m['mpnn_seconds'],manifest_sha256=sha(path),refolded_sha256=sha(run/'refolded.h5'))


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');view={k:v for k,v in d.items() if k!='backbones'};a.output.with_suffix('.md').write_text('# Fixed-fragment experimental positives\n\nSame four experimental backbones and isolated motifs; only supplied motif residues fixed.32refolds audited. Strict success requires motif/global/geometry criteria in one same refold. Comparison with earlier free-redesign positives is descriptive; sequence-sampling context differs. No threshold changes or failed-target exclusions.\n\n```json\n'+json.dumps(view,indent=2)+'\n```\n')

if __name__=='__main__':main()
