"""Audit all refolds and require motif/global/geometry success in the same one."""
import argparse,json
from itertools import combinations
from pathlib import Path
import h5py,numpy as np
from latentfold.metrics import usalign_coordinates
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.fragment_designability import motif_fit,same_refold_success
from prepare_trained_fragment_designability import audit_inputs
from fixed_motif_design import verify_fixed_sequences
from summarize_fragment_training import interval
from prepare_overfit import sha


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest',records=[])
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error','Incomplete'),completed_refolds=len(m['records']))
    c=m['config'];audit_inputs(c);verify_fixed_sequences(m['sequences'],c['entries']);wanted={(r['name'],i) for r in c['entries'] for i in range(8)};index={(r['name'],r['sequence_index']):r for r in m['records']}
    if len(m['records'])!=288 or set(index)!=wanted:raise ValueError('Missing/duplicate refolds')
    positives={r['name'] for r in c['entries'] if r['head']=='experimental'}
    if len(m['controls'])!=4 or {r['name'] for r in m['controls']}!=positives or any(r['ca_rmsd']>.01 or r['ca_lddt']<.999 for r in m['controls']):raise ValueError('Teacher repeatability failed')
    results=[];backbones={}
    with h5py.File(c['predictions']) as inp,h5py.File(run/'refolded.h5') as f:
        if set(f)!={r['name'] for r in c['entries']}:raise ValueError('Unexpected refold inventory')
        for r in c['entries']:
            name=r['name'];raw=inp[r['dataset']][:] if r['head']=='experimental' else inp[r['dataset']][r['slot']];fragment=inp['motifs/'+r['target_id']][:];raw_metrics=dict(coarse_valid=bool(backbone_geometry(raw[None])['coarse_valid'][0]),**motif_fit(raw,fragment,int(r['motif_start'])));rows=[];backbones[name]=raw
            if set(f[name])!=set(map(str,range(8))):raise ValueError('Incomplete refold archive')
            for slot in range(8):
                bb=f[name+'/'+str(slot)][:]
                if bb.shape!=raw.shape or not np.isfinite(bb).all():raise ValueError('Invalid archived refold')
                tm=usalign_coordinates(c['usalign'],bb[:,1],raw[:,1])
                if abs(tm-index[(name,slot)]['sc_tm'])>1e-7:raise ValueError('Stored global score failed audit')
                rows.append(dict(sequence_index=slot,sc_tm=tm,coarse_valid=bool(backbone_geometry(bb[None])['coarse_valid'][0]),**motif_fit(bb,fragment,int(r['motif_start']))))
            result=dict(**r,raw=raw_metrics,refolds=rows,**same_refold_success(raw_metrics,rows));results.append(result)
    controls_ok=all(r['valid_designable'] for r in results if r['head']=='experimental');summaries=[];diversity=[]
    for mode in sorted({r['mode'] for r in results}):
        rr=[r for r in results if r['mode']==mode];families=sorted({r['family'] for r in rr});summary=dict(mode=mode,backbones=len(rr))
        for metric in ('strict_joint_success','legacy_drms_joint_success','valid_designable','raw_gate_passed'):
            summary[metric]=dict(count=sum(r[metric] for r in rr),fraction=float(np.mean([r[metric] for r in rr])),family_interval=interval([np.mean([r[metric] for r in rr if r['family']==family]) for family in families]))
        summaries.append(summary)
        if mode!='real':
            for scope in ('all','strict_joint_success'):
                pairs=[(x,y) for x,y in combinations(rr,2) if x['family']==y['family'] and (scope=='all' or x[scope] and y[scope])];values=[usalign_coordinates(c['usalign'],backbones[x['name']][:,1],backbones[y['name']][:,1]) for x,y in pairs];diversity.append(dict(mode=mode,scope=scope,pairs=len(values),mean_pairwise_tm=float(np.mean(values)) if values else None))
    comparisons=[]
    for baseline in ('trained_null','isolated_clamp','original_null'):
        families=sorted({r['family'] for r in results});differences=[np.mean([r['strict_joint_success'] for r in results if r['mode']=='conditioned' and r['family']==family])-np.mean([r['strict_joint_success'] for r in results if r['mode']==baseline and r['family']==family]) for family in families];comparisons.append(dict(baseline=baseline,conditioned_minus_baseline=interval(differences)))
    return dict(status='complete',positive_controls_passed=controls_ok,interpretation_qualified=controls_ok,arm=c['arm'],manifest_sha256=sha(path),refolded_sha256=sha(run/'refolded.h5'),completed_refolds=288,backbones=results,summaries=summaries,comparisons=comparisons,diversity=diversity,mpnn_seconds=m['mpnn_seconds'],elapsed_seconds=m['elapsed_seconds'],peak_reserved_GiB=max(r['peak_reserved_bytes'] for r in m['records'])/2**30)


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');view={k:v for k,v in d.items() if k!='backbones'};a.output.with_suffix('.md').write_text('# Trained fragment designability\n\nAll36backbones and288designed-sequence refolds retained. Strict success requires valid raw geometry and motif fit, then one SAME refold with scTM>.5, valid geometry, motif dRMS<=1A and proper-rotation motifCA RMSD<=1A. Motif residues fixed; no scaffold sequence supplied. Four-family development feasibility only.\n\n```json\n'+json.dumps(view,indent=2)+'\n```\n')

if __name__=='__main__':main()
