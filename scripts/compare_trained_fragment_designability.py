"""Paired designability contrast with shared backbone/sequence and numerical refold controls."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from summarize_fragment_training import interval
from prepare_overfit import sha
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=2,required=True);p.add_argument('--reports',type=Path,nargs=2,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();ms=[json.loads((r/'manifest.json').read_text()) for r in a.runs];ds=[json.loads(r.read_text()) for r in a.reports]
    if [d['arm'] for d in ds]!=['adapter_only','full'] or any(d['status']!='complete' or not d['interpretation_qualified'] for d in ds):raise ValueError('Audited qualified paired assays required')
    if any(d['manifest_sha256']!=sha(run/'manifest.json') for d,run in zip(ds,a.runs)):raise ValueError('Changed assay manifest')
    keys=('assay','protocol_sha256','num_sequences','temperature','mpnn_seed','seed','mpnn','dependencies','teacher_artifacts','precision','usalign_sha256','reference_predictions_sha256','isolated_predictions_sha256','fragments_sha256')
    if any(ms[0]['config'][k]!=ms[1]['config'][k] for k in keys):raise ValueError('Unmatched assay recipe')
    shared=[r for r in ms[0]['config']['entries'] if r['mode'] in ('real','isolated_clamp','original_null')];same=0;controls=[]
    with h5py.File(a.runs[0]/'refolded.h5') as left,h5py.File(a.runs[1]/'refolded.h5') as right:
        for r in shared:
            name=r['name']
            if ms[0]['sequences'][name]!=ms[1]['sequences'][name]:raise ValueError('Shared control sequence draws differ')
            for k in range(8):
                x,y=left[name+'/'+str(k)][:],right[name+'/'+str(k)][:];metric=ca_metrics(x[:,1],y[:,1]);valid=bool(backbone_geometry(x[None])['coarse_valid'][0]==backbone_geometry(y[None])['coarse_valid'][0]);controls.append(dict(name=name,slot=k,bitwise_identical=bool(np.array_equal(x,y)),same_validity=valid,**metric))
                if metric['ca_rmsd']>.01 or metric['ca_lddt']<.999 or not valid:raise ValueError('Shared control exceeds established teacher repeatability tolerances')
                same+=1
    for r in shared:
        decisions=[next(x for x in d['backbones'] if x['name']==r['name']) for d in ds]
        if any(decisions[0][key]!=decisions[1][key] for key in ('strict_joint_success','valid_designable','legacy_drms_joint_success')):raise ValueError('Shared control decisions disagree')
    rows=[[r for r in d['backbones'] if r['mode']=='conditioned'] for d in ds];families=sorted({r['family'] for r in rows[0]});comparisons=[]
    for metric in ('strict_joint_success','valid_designable','raw_gate_passed'):
        values=[[np.mean([r[metric] for r in rr if r['family']==family]) for family in families] for rr in rows];comparisons.append(dict(metric=metric,adapter_only=float(np.mean(values[0])),full=float(np.mean(values[1])),full_minus_adapter=interval(np.asarray(values[1])-np.asarray(values[0]))))
    d=dict(status='complete',identical_control_backbones=len(shared),identical_control_sequences=same,numerically_equivalent_control_refolds=same,max_control_ca_rmsd=max(r['ca_rmsd'] for r in controls),min_control_ca_lddt=min(r['ca_lddt'] for r in controls),bitwise_identical_refolds=sum(r['bitwise_identical'] for r in controls),same_control_decisions=True,comparisons=comparisons,source_report_hashes=[sha(p) for p in a.reports]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Paired trained-fragment designability\n\nAll fixed-budget outputs retained.20shared control backbones produce the same160designed sequences and numerically equivalent refolds under the established teacher repeatability tolerances; all control decisions agree in both assays. Generated backbones hold supplied motif residues fixed; these rates cannot be compared directly with unconstrained sequence-design rates. Four-family feasibility, not a population estimate or experimental validation.\n\n```json\n'+json.dumps(d,indent=2)+'\n```\n');print(json.dumps(d,indent=2))

if __name__=='__main__':main()
