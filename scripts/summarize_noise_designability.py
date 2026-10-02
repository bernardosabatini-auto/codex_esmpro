"""Audit every constrained-design refold and report joint success and diversity."""
import argparse,json
from pathlib import Path
from itertools import combinations
import h5py,numpy as np
from prepare_noise_designability import audit_inputs
from summarize_designability import analyze as design_audit
from summarize_noise_guidance import contact,analyze as guidance_audit
from latentfold.metrics import usalign_coordinates


def analyze(run):
    if not (run/'manifest.json').exists():return dict(status='failed',error='Missing startup manifest')
    m=json.loads((run/'manifest.json').read_text())
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error','Incomplete'),completed_refolds=len(m['records']))
    c=m['config'];audit_inputs(c);d=design_audit(run);generation=guidance_audit(Path(c['generation_manifest']).parent)
    if generation['status']!='complete':raise ValueError('Invalid generation parent')
    if len(d['backbones'])!=28 or d['completed_refolds']!=224:raise ValueError('Incomplete assay')
    controls=[r for r in d['backbones'] if r['head']=='experimental']
    if len(controls)!=4 or not all(r['valid_designable'] for r in controls):raise ValueError('Experimental positive-control failure')
    summaries=[];diversity=[]
    with h5py.File(c['predictions']) as f:
        bbs={r['name']:f[r['dataset']][:] if r['head']=='experimental' else f[r['dataset']][r['slot']] for r in d['backbones']}
        for r in d['backbones']:
            r['contact_distance']=float(contact(bbs[r['name']]));r['contact_success']=abs(r['contact_distance']-8)<=1;r['joint_success']=bool(r['contact_success'] and r['valid_designable'])
        for mode in ('initial','guided','random'):
            rr=[r for r in d['backbones'] if r['mode']==mode];cost=next(r['seconds'] for r in generation['summaries'] if r['mode']==mode)
            row=dict(mode=mode,n=len(rr),generation_seconds=cost,joint_successes=sum(r['joint_success'] for r in rr),generation_seconds_per_joint_success=cost/sum(r['joint_success'] for r in rr) if any(r['joint_success'] for r in rr) else None)
            for key in ('contact_success','coarse_valid','designable','valid_designable','joint_success','sc_tm'):row[key]=float(np.mean([r[key] for r in rr]))
            row['refold_seconds']=sum(r['seconds'] for r in m['records'] if r['name'] in {x['name'] for x in rr});summaries.append(row)
            for scope in ('all','valid_designable','joint_success'):
                pairs=[]
                for family in sorted({r['family'] for r in rr}):
                    eligible=[r for r in rr if r['family']==family and (scope=='all' or r[scope])]
                    for x,y in combinations(eligible,2):pairs.append(dict(family=family,tm=usalign_coordinates(c['usalign'],bbs[x['name']][:,1],bbs[y['name']][:,1])))
                diversity.append(dict(mode=mode,scope=scope,pairs=pairs,mean_pairwise_tm=float(np.mean([r['tm'] for r in pairs])) if pairs else None))
    return dict(status='complete',summaries=summaries,diversity=diversity,backbones=d['backbones'],completed_refolds=224,controls=controls,mpnn_seconds=d['mpnn_seconds'],assay_elapsed_seconds=d['elapsed_seconds'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');lines=['# Noise steering: matched designability','',f"Status: {d['status']}."]
    if d['status']=='complete':
        lines+=['','All eight cases per method; four experimental controls passed; all224refolds audited. Joint success requires contact within1A of8A, full-backbone coarse validity, and best8scTM>.5.','', '| Method | Contact | Geometry | Designable | Joint | Generation s | s/joint success |','|---|---:|---:|---:|---:|---:|---:|']
        for r in d['summaries']:lines.append(f"| {r['mode']} | {r['contact_success']:.3f} | {r['coarse_valid']:.3f} | {r['designable']:.3f} | {r['joint_success']:.3f} | {r['generation_seconds']:.2f} | {r['generation_seconds_per_joint_success']} |")
        lines+=['','Generation costs include initial draws and optimization/random search; designability assay costs are separate. No equal-compute or experimental-validation claim. Four families provide a feasibility comparison, not a population rate.',f"ProteinMPNN seconds: {d['mpnn_seconds']:.2f}; assay elapsed seconds: {d['assay_elapsed_seconds']:.2f}.",'','Pairwise diversity, retaining pair counts:']
        for r in d['diversity']:lines.append(f"- {r['mode']} {r['scope']}: {len(r['pairs'])} pairs; mean fixed-correspondence TM {r['mean_pairwise_tm']}.")
        lines+=['','Sparse successful pairs cannot establish ensemble diversity. Separate designed sequences do not establish multistability of one sequence.']
    else:lines+=['',d['error']]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
