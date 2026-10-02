"""CPU feasibility of exact within-sequence noise/teacher matching, no training."""
import json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.conditional_coupling import couple_targets
from latentfold.teacher_states import draw_teacher
from prepare_overfit import sha


def main():
 root=Path(__file__).resolve().parents[1];manifest=root/'runs/overfit_labels_49693246/manifest.json';m=json.loads(manifest.read_text());path=manifest.parent/'labels.h5'
 if m['status']!='complete' or not m['training_gate_passed'] or sha(path)!=m['labels_sha256']:raise ValueError('Invalid label parent')
 torch.set_num_threads(1);rng=np.random.default_rng(2026100221);gen=torch.Generator().manual_seed(2026100221);rows=[];start=time.monotonic()
 with h5py.File(path) as f:
  for target in m['config']['targets']:
   ident=target['id'];g=f[ident];n=target['length'];valid=np.flatnonzero(g['coarse_valid'][:]);state=json.loads(g.attrs['state_definition']);bank=torch.from_numpy(g['teacher_z_aligned'][:]);mask=torch.ones(8,n,dtype=torch.bool)
   for repeat in range(32):
    choices=[draw_teacher(valid,state,rng.random(),'balanced') for _ in range(8)];z=bank[choices];noise=torch.randn(z.shape,generator=gen);assigned,info=couple_targets(noise,z,mask,[ident]*8,group_size=8,arm='optimal')
    if not torch.equal(assigned,z[info['permutation']]) or sorted(info['permutation'])!=list(range(8)):raise ValueError('Target marginal changed')
    cost=info['costs'][0];rows.append(dict(target_id=ident,repeat=repeat,length=n,**cost,target_variance=float((z-z.mean(0)).square().mean()),changed_assignments=sum(i!=j for i,j in enumerate(info['permutation']))))
 summary=dict(groups=len(rows),draws=len(rows)*8,mean_independent_cost=float(np.mean([r['independent'] for r in rows])),mean_optimal_cost=float(np.mean([r['optimal'] for r in rows])),mean_cost_reduction=float(np.mean([r['independent']-r['optimal'] for r in rows])),mean_target_variance=float(np.mean([r['target_variance'] for r in rows])),fraction_assignments_changed=float(np.mean([r['changed_assignments']/8 for r in rows])),elapsed_seconds=time.monotonic()-start)
 d=dict(status='complete',label_manifest=str(manifest),label_manifest_sha256=sha(manifest),labels_sha256=sha(path),summary=summary,rows=rows,training_updates=0)
 out=root/'reports/conditional_coupling_feasibility_20261002';out.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');out.with_suffix('.md').write_text('# Within-sequence matching feasibility\n\nNo GPU inference or training. All32training proteins,32groups of8balanced teacher draws each. Exact assignment changes only the noise–target pairing, retaining every drawn target exactly once.\n\n'+json.dumps(summary,indent=2)+'\n\nLower pairwise transport cost is not evidence of improved modeling or structural diversity. A matched training experiment would require the same group composition and all RNG draws, plus fresh-noise evaluation. No test data used.\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
