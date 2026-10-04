"""CPU kinematic validation on every original training-diagnostic bridge."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.internal_bridge import InternalBridge
from latentfold.local_closure import geometry_audit
from extra_fragment_validation_core import load_conditions
from prepare_overfit import sha


def run(root,protocol):
    tick=time.monotonic();spec=json.loads(protocol.read_text())
    report=root/spec['source_report'];d=json.loads(report.read_text())
    if (sha(report)!=spec['source_report_sha256'] or d['status']!='complete'
            or d['qualified'] or not d['numerically_qualified'] or not d['scaffold_bridge']):
        raise ValueError('Bound completed failed bridge experiment required')
    mp=Path(d['manifest_path']);m=json.loads(mp.read_text());c=m['config'];pred=mp.parent/'predictions.h5'
    if d['manifest_sha256']!=sha(mp) or d['predictions_sha256']!=sha(pred):raise ValueError('Changed source arrays')
    ids=[r['id'] for r in c['selected']]
    if len(ids)!=spec['proteins'] or len(set(ids))!=len(ids):raise ValueError('Changed full panel')
    items=load_conditions(c['fragments'],ids,'c20_center',cohort='train')
    rng=np.random.default_rng(spec['seed']);rows=[]
    with h5py.File(pred) as f:
        for arm in spec['arms']:
            for ident in ids:
                start=items[ident]['start'];stop=start+spec['motif_length'];width=spec['flank_width']
                for slot in range(spec['slots']):
                    reference=np.asarray(f[arm+'/'+ident+'/backbone'][slot],dtype=np.float64)
                    for side,lo,hi in [('left',start-width,start),('right',stop,stop+width)]:
                        if not 0<lo<hi<len(reference):raise ValueError('Terminal bridges need a separate protocol; no filtering')
                        offsets=rng.normal(0,spec['torsion_perturbation_sd_radians'],2*width+1)
                        q,_=np.linalg.qr(rng.normal(size=(3,3)));q[:,0]*=np.linalg.det(q)
                        shift=rng.normal(size=3)*10
                        for name,dtype in [('float64',torch.float64),('float32',torch.float32)]:
                            if time.monotonic()-tick>spec['cpu_seconds_cap']:raise TimeoutError('CPU preflight cap')
                            x=torch.tensor(reference,dtype=dtype);model=InternalBridge(x,lo,hi)
                            zero=torch.zeros(model.n_torsions,dtype=dtype)
                            original,residual=model.assemble(x,zero)
                            delta=torch.tensor(offsets,dtype=dtype,requires_grad=True)
                            moving,ghost=model.reconstruct(x,delta)
                            out,error=model.assemble(x,delta)
                            fixed=torch.ones(len(x),dtype=torch.bool);fixed[lo:hi]=False
                            if not torch.equal(out[fixed],x[fixed]):raise ValueError('Fixed atoms changed')
                            grad=torch.autograd.grad(moving.square().mean()+ghost.square().mean(),delta)[0]
                            if not torch.isfinite(grad).all() or grad.norm()<=0:raise ValueError('Nonfinite or zero kinematic gradient')
                            # Independent molecular audit uses ghost right N/CA/C.
                            # The fixed right O is irrelevant to every touched edge.
                            right=torch.cat((ghost.detach(),x[hi,3:4]))
                            extended=torch.cat((x[lo-1:lo],moving.detach(),right[None]))
                            geometry=geometry_audit(extended.numpy(),x[lo-1:hi+1].numpy(),width+1,1,width)
                            rotation=torch.tensor(q,dtype=dtype);translation=torch.tensor(shift,dtype=dtype)
                            moved=x@rotation+translation
                            transformed,transformed_error=InternalBridge(moved,lo,hi).assemble(moved,delta.detach())
                            row=dict(arm=arm,target_id=ident,slot=slot,side=side,dtype=name,
                                roundtrip_max_abs=float((original-x).abs().max()),
                                roundtrip_endpoint_max_abs=float(residual.abs().max()),
                                proper_pose_max_abs=float((transformed-out.detach()@rotation-translation).abs().max()),
                                proper_pose_endpoint_max_abs=float((transformed_error-error.detach()@rotation).abs().max()),
                                fixed_exact=True,gradient_norm=float(grad.norm()),
                                max_bond_delta=geometry['max_bond_delta'],max_angle_delta=geometry['max_angle_delta'],
                                max_peptide_torsion_delta=geometry['max_torsion_delta'],
                                perturbed_endpoint_rmsd=float(error.detach().square().sum(-1).mean().sqrt()))
                            tol=spec[name+'_coordinate_tolerance_angstrom'];ang=spec[name+'_angle_tolerance_degrees']
                            row['numerical_pass']=all(row[k]<=tol for k in ('roundtrip_max_abs','roundtrip_endpoint_max_abs',
                                'proper_pose_max_abs','proper_pose_endpoint_max_abs','max_bond_delta')) and all(
                                row[k]<=ang for k in ('max_angle_delta','max_peptide_torsion_delta'))
                            rows.append(row)
    if len(rows)!=2*spec['bridges']:raise ValueError('Incomplete unfiltered bridge panel')
    summaries=[]
    for dtype in ('float64','float32'):
        rr=[r for r in rows if r['dtype']==dtype]
        summary=dict(dtype=dtype,bridges=len(rr),passed=sum(r['numerical_pass'] for r in rr))
        for key in ('roundtrip_max_abs','roundtrip_endpoint_max_abs','proper_pose_max_abs','proper_pose_endpoint_max_abs',
                    'max_bond_delta','max_angle_delta','max_peptide_torsion_delta'):
            summary[key]=max(r[key] for r in rr)
        summary['median_perturbed_endpoint_rmsd']=float(np.median([r['perturbed_endpoint_rmsd'] for r in rr]))
        summaries.append(summary)
    return dict(status='complete',qualified=all(r['numerical_pass'] for r in rows),seconds=time.monotonic()-tick,
        protocol_sha256=sha(protocol),source_report_sha256=sha(report),predictions_sha256=sha(pred),
        code_sha256=sha(root/'src/latentfold/internal_bridge.py'),script_sha256=sha(Path(__file__)),
        summary=summaries,rows=rows,scope=spec['scope'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--protocol',type=Path,default=Path('configs/internal_bridge_preflight_protocol.json'))
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=run(Path(__file__).resolve().parents[1],a.protocol)
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    brief={k:v for k,v in result.items() if k!='rows'}
    a.output.with_suffix('.md').write_text('# Internal-coordinate bridge preflight\n\n```json\n'+json.dumps(brief,indent=2)+'\n```\n')
    print(json.dumps(brief,indent=2))


if __name__=='__main__':main()
