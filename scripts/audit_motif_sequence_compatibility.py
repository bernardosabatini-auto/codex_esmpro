"""CPU-only fixed-sequence compatibility and all-atom motif diagnostics."""
import argparse,importlib.util,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.training_subset import frozen_digest
from prepare_overfit import sha


def atom_fit(bb,motif,start):
    x=bb[start:start+len(motif)].astype(np.float64);y=motif.astype(np.float64);xc=x[:,1].mean(0);yc=y[:,1].mean(0)
    u,_,vt=np.linalg.svd((x[:,1]-xc).T@(y[:,1]-yc));d=np.eye(3);d[-1,-1]=np.linalg.det(u@vt);rotation=u@d@vt
    error=np.sum(((x-xc)@rotation-(y-yc))**2,axis=-1)
    return dict(ca_aligned_allatom_rmsd=float(np.sqrt(error.mean())),atom_rmsd={k:float(np.sqrt(error[:,i].mean())) for i,k in enumerate(('N','CA','C','O'))})


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--mode',choices=['ca','backbone'],default='ca');a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/('configs/full_backbone_compatibility_protocol.json' if a.mode=='backbone' else 'configs/motif_sequence_compatibility_protocol.json');spec=json.loads(protocol.read_text());run=root/'runs'/spec['assay'];mp=run/'manifest.json';rp=root/'reports'/(run.name+'.json');m=json.loads(mp.read_text());d=json.loads(rp.read_text());c=m['config'];tick=time.monotonic();torch.set_num_threads(1)
    if m['status']!='complete' or d['status']!='complete' or d['manifest_sha256']!=sha(mp) or d['refolded_sha256']!=sha(run/'refolded.h5'):raise ValueError('Changed complete assay')
    utils=Path(c['mpnn'])/'protein_mpnn_utils.py';weights=Path(c['mpnn'])/('vanilla_model_weights/v_48_020.pt' if a.mode=='backbone' else 'ca_model_weights/v_48_020.pt');bound={r['path']:r['sha256'] for r in c['dependencies']}
    if a.mode=='backbone':
        prior=json.loads((root/spec['qualified_weight_source']).read_text());bound.update({r['path']:r['sha256'] for r in prior['config']['dependencies']})
    if sha(utils)!=bound[str(utils)] or sha(weights)!=bound[str(weights)]:raise ValueError('Changed qualified ProteinMPNN')
    module_spec=importlib.util.spec_from_file_location('qualified_protein_mpnn_utils',utils);module=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(module)
    ck=torch.load(weights,map_location='cpu',weights_only=False);model=module.ProteinMPNN(ca_only=a.mode=='ca',num_letters=21,node_features=128,edge_features=128,hidden_dim=128,num_encoder_layers=3,num_decoder_layers=3,augment_eps=0.,k_neighbors=ck['num_edges']).eval().requires_grad_(False);model.load_state_dict(ck['model_state_dict'],strict=True);before=frozen_digest(model)
    records=[];controls=[];alphabet='ACDEFGHIKLMNPQRSTVWYX'
    with h5py.File(c['predictions'],locking=False) as raw,h5py.File(run/'refolded.h5',locking=False) as folds:
        for r in d['records']:
            ident=r['target_id'];st=r['fixed_start'];seq=r['fixed_sequence'];motif=raw['motifs/'+ident][:];n=r['length'];target=torch.tensor([alphabet.index(x) for x in seq]);mask=torch.ones(1,n);idx=torch.arange(n)[None];chain=torch.ones(1,n,dtype=torch.long)
            def probabilities(x):return model.unconditional_probs(x,mask,idx,chain)[:,st:st+len(seq)]
            def objective(x):return -probabilities(x)[0,torch.arange(len(seq)),target].mean()
            arrays=[('raw',raw[r['dataset']][0],None)]
            eligible=[x for x in r['refolds'] if x['coarse_valid'] and x['sc_tm']>.5 and x['scaffold_tm']>.5]
            if eligible:
                chosen=min(eligible,key=lambda x:x['sequence_index']);arrays.append(('refold',folds[r['name']+'/'+str(chosen['sequence_index'])][:],chosen))
            for stage,bb,chosen in arrays:
                x=torch.from_numpy((bb[:,1] if a.mode=='ca' else bb).astype(np.float32))[None]
                with torch.no_grad():lp=probabilities(x)[0];nll=float(-lp[torch.arange(len(seq)),target].mean());reverse=float(-lp[torch.arange(len(seq)),target.flip(0)].mean())
                records.append(dict(name=r['name'],arm=r['arm'],target_id=ident,slot=r['generation_slot'],stage=stage,motif_nll=nll,reversed_sequence_nll=reverse,ordinary_designable=r['valid_designable'],strict=r['scaffold_joint_success'],selected_refold=None if chosen is None else chosen['sequence_index'],**atom_fit(bb,motif,st)))
                if r['arm']=='native' and stage=='raw':
                    rotation=x.new_tensor([[0,-1,0],[1,0,0],[0,0,1]])
                    with torch.no_grad():pose_error=float((probabilities(x@rotation+x.new_tensor([11,7,-3]))[0]-lp).abs().max())
                    probe=x.clone().requires_grad_();loss=objective(probe);grad,=torch.autograd.grad(loss,probe);norm=grad.norm()
                    if not torch.isfinite(grad).all() or norm<=1e-10:
                        controls.append(dict(target_id=ident,pose_max_logprob_error=pose_error,gradient_finite=bool(torch.isfinite(grad).all()),nonfinite_elements=int((~torch.isfinite(grad)).sum()),gradient_norm=float(norm) if torch.isfinite(norm) else None,finite_differences=[],qualified=False))
                        continue
                    direction=grad/norm;analytic=float((grad*direction).sum());checks=[]
                    with torch.no_grad():
                        for eps in (.01,.001,.0001):
                            numeric=float((objective(x+eps*direction)-objective(x-eps*direction))/(2*eps));checks.append(dict(epsilon=eps,analytic=analytic,numeric=numeric,passed=abs(numeric-analytic)<=max(.001,.05*abs(analytic))))
                    controls.append(dict(target_id=ident,pose_max_logprob_error=pose_error,gradient_finite=True,finite_differences=checks,qualified=pose_error<=1e-4 and any(z['passed'] for z in checks)))
            print(r['name'],r['arm'],flush=True)
    if before!=frozen_digest(model):raise ValueError('Frozen weights changed')
    summary=[]
    for arm in ('native','baseline','guided'):
        for stage in ('raw','refold'):
            rr=[r for r in records if r['arm']==arm and r['stage']==stage];summary.append(dict(arm=arm,stage=stage,n=len(rr),mean_motif_nll=float(np.mean([r['motif_nll'] for r in rr])) if rr else None,mean_reverse_minus_actual=float(np.mean([r['reversed_sequence_nll']-r['motif_nll'] for r in rr])) if rr else None,mean_ca_aligned_allatom_rmsd=float(np.mean([r['ca_aligned_allatom_rmsd'] for r in rr])) if rr else None))
    sources=[protocol,mp,rp,Path(c['predictions']),run/'refolded.h5',utils,weights,Path(__file__)];result=dict(status='complete',mode=a.mode,seconds=time.monotonic()-tick,summary=summary,records=records,controls=controls,gradient_qualified=all(r['qualified'] for r in controls),weights_unchanged=True,sources=[dict(path=str(p.resolve()),sha256=sha(p)) for p in sources],scope=spec['interpretation'])
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Fixed motif sequence compatibility: CPU diagnostic\n\n'+spec['interpretation']+'\n\n```json\n'+json.dumps(dict(summary=summary,gradient_qualified=result['gradient_qualified'],controls=controls),indent=2)+'\n```\n');print(json.dumps(summary))

if __name__=='__main__':main()
