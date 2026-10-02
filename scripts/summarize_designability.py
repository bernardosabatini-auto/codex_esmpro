"""Audit the complete design/refold budget and report joint constraint success."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from latentfold.metrics import usalign_coordinates
from latentfold.ensemble_metrics import backbone_geometry
from itertools import combinations
from prepare_overfit import sha


def analyze(run):
    m=json.loads((run/'manifest.json').read_text())
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error','Incomplete'),completed_refolds=len(m['records']))
    c=m['config'];entries=c['entries'];wanted={(r['name'],i) for r in entries for i in range(8)}
    if len(m['records'])!=len(wanted) or {(r['name'],r['sequence_index']) for r in m['records']}!=wanted:raise ValueError('Missing/duplicate refolds')
    for key in ('generation_manifest','predictions','protocol','usalign'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    expected={r['name'] for r in entries if r['head']=='experimental'}
    if {r['name'] for r in m['controls']}!=expected or len(m['controls'])!=len(expected) or any(r['ca_rmsd']>.01 or r['ca_lddt']<.999 for r in m['controls']):raise ValueError('Invalid teacher controls')
    source_backbones={}
    with h5py.File(run/'refolded.h5') as f,h5py.File(c['predictions']) as source:
        for r in entries:
            if len(m['sequences'][r['name']])!=8:raise ValueError('Missing sequence designs')
            ref=source[r['dataset']][:] if r['head']=='experimental' else source[r['dataset']][r['slot']]
            source_backbones[r['name']]=ref
            for rec in [x for x in m['records'] if x['name']==r['name']]:
                bb=f[r['name']+'/'+str(rec['sequence_index'])][:]
                if bb.shape!=ref.shape or not np.isfinite(bb).all():raise ValueError('Invalid archived refold')
                actual=usalign_coordinates(c['usalign'],bb[:,1],ref[:,1])
                if abs(actual-rec['sc_tm'])>1e-7:raise ValueError('Stored score failed audit')
    results=[]
    for r in entries:
        best=max(x['sc_tm'] for x in m['records'] if x['name']==r['name']);designable=best>.5;motif_ok=r['motif_drms'] is not None and r['motif_drms']<=1
        coarse=bool(backbone_geometry(source_backbones[r['name']][None])['coarse_valid'][0])
        results.append(dict(**r,sc_tm=best,designable=designable,coarse_valid=coarse,joint_motif_success=bool(designable and motif_ok),valid_designable=bool(designable and coarse),valid_joint_motif_success=bool(designable and coarse and motif_ok)))
    groups=sorted({(r['head'],r['mode']) for r in entries});summary=[]
    for head,mode in groups:
        rr=[r for r in results if (r['head'],r['mode'])==(head,mode)];names={r['name'] for r in rr};times=[r for r in m['records'] if r['name'] in names]
        summary.append(dict(head=head,mode=mode,backbones=len(rr),sc_tm=float(np.mean([r['sc_tm'] for r in rr])),designable=float(np.mean([r['designable'] for r in rr])),joint_motif_success=float(np.mean([r['joint_motif_success'] for r in rr])) if mode.startswith('motif') else None,refold_seconds=sum(r['seconds'] for r in times),peak_reserved_GiB=max(r['peak_reserved_bytes'] for r in times)/2**30))
    for group in summary:
        rr=[r for r in results if (r['head'],r['mode'])==(group['head'],group['mode'])]
        group['valid_designable']=float(np.mean([r['valid_designable'] for r in rr]))
        group['valid_joint_motif_success']=float(np.mean([r['valid_joint_motif_success'] for r in rr])) if group['mode'].startswith('motif') else None
    diversity=[]
    for head,mode in groups:
        if head=='experimental':continue
        rr=[r for r in results if (r['head'],r['mode'])==(head,mode)]
        for scope in ('all','valid_designable','valid_joint_motif_success'):
            if scope=='valid_joint_motif_success' and mode=='unconditional':continue
            pairs=[]
            for family in sorted({r['family'] for r in rr}):
                eligible=[r for r in rr if r['family']==family and (scope=='all' or r[scope])]
                for x,y in combinations(eligible,2):pairs.append(usalign_coordinates(c['usalign'],source_backbones[x['name']][:,1],source_backbones[y['name']][:,1]))
            diversity.append(dict(head=head,mode=mode,scope=scope,pairs=len(pairs),mean_pairwise_fixed_tm=float(np.mean(pairs)) if pairs else None))
    comparisons=[]
    for mode in ('unconditional','motif_u1','motif_u3'):
        families=sorted({r['family'] for r in results if r['mode']==mode})
        if not families:continue
        rng=np.random.default_rng(2026100212);ix=rng.integers(0,len(families),(10000,len(families)))
        for metric in ('sc_tm','designable','joint_motif_success'):
            if metric=='joint_motif_success' and mode=='unconditional':continue
            d=np.array([np.mean([r[metric] for r in results if r['head']=='reflow10' and r['mode']==mode and r['family']==f])-np.mean([r[metric] for r in results if r['head']=='original50' and r['mode']==mode and r['family']==f]) for f in families]);comparisons.append(dict(mode=mode,metric=metric,difference=float(d.mean()),family_interval=np.quantile(d[ix].mean(1),[.025,.975]).tolist()))
    return dict(status='complete',summaries=summary,comparisons=comparisons,diversity=diversity,backbones=results,completed_refolds=len(m['records']),mpnn_seconds=m['mpnn_seconds'],elapsed_seconds=m['elapsed_seconds'],teacher_adapter=m['teacher_adapter'],scope='4families/2samples profile, fixed-correspondence USalign, positive controls required; no independent-test or experimental-validation claim')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');lines=['# Fixed-budget ProteinMPNN/refolding profile','',f"Status: {d['status']}."]
    if d['status']=='complete':
        lines+=['','| Head | Mode | Backbones | Best8 scTM | Designable | Joint motif success | Refold s |','|---|---|---:|---:|---:|---:|---:|']
        for r in d['summaries']:lines.append(f"| {r['head']} | {r['mode']} | {r['backbones']} | {r['sc_tm']:.4f} | {r['designable']:.4f} | {r['joint_motif_success']} | {r['refold_seconds']:.2f} |")
        lines+=['',d['scope'],'','Joint success means best8 scTM>0.5 AND motif distance-matrix RMS<=1A. Each backbone receives8designed sequences/8refolds; no rejection sampling. Timings include full guarded FP32 teacher folding and exclude CPU scoring; total elapsed and ProteinMPNN time retained in JSON. Motif codes derive from complete source backbones; separate designs do not demonstrate one sequence supporting multiple states. Every failure is retained.','',f"All {d['completed_refolds']} refolds audited; ProteinMPNN {d['mpnn_seconds']:.2f}s; total elapsed {d['elapsed_seconds']:.2f}s."]
        lines+=['','Requiring the unchanged full-backbone coarse-validity gate as well:']
        for r in d['summaries']:lines.append(f"- {r['head']} {r['mode']}: valid and designable={r['valid_designable']:.4f}, valid joint motif success={r['valid_joint_motif_success']}.")
        lines+=['','Pairwise structural similarity (lower means greater diversity), with pair counts; sparse successful pairs cannot establish ensemble capacity:']
        for r in d['diversity']:lines.append(f"- {r['head']} {r['mode']} {r['scope']}: pairs={r['pairs']}, mean fixed-correspondence TM={r['mean_pairwise_fixed_tm']}.")
        for r in d['comparisons']:lines.append(f"- reflow10 minus original50, {r['mode']} {r['metric']}: {r['difference']:+.4f}, family interval {r['family_interval']}.")
    else:lines+=['',d['error']]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
