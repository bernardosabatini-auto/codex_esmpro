"""Encode training fragments in isolation; preserve verified full targets separately."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from torch.nn import functional as F
from latentfold.decoder import load_proteinae
from latentfold.backbone import encode_backbone
from latentfold.flow import target_noise
from latentfold.precision import inference_precision
from latentfold.fragment_conditioning import fragment_features
from latentfold.ensemble_metrics import backbone_geometry
from generate_isolated_motif import canonical_fragment
from latentfold.fragment_designability import motif_error
from prepare_overfit import sha
from profile_gpu import atomic_json


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('protocol','training_manifest','training_labels','development_manifest','development_predictions','selection','decoder_checkpoint'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    expanded=c.get('expanded_fragment_data',False)
    if expanded:
        from prepare_fragment_expansion import audit_sources
        audit_sources(c)
    expected_proteins=c.get('training_protein_count',128) if expanded else 32
    a.output.mkdir(parents=True,exist_ok=False);start=time.monotonic();m=dict(status='running',config=c,records=[],controls=[],development=[],reference_validity=[]);atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
        decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['training_labels']) as src,h5py.File(c['development_predictions']) as dev,h5py.File(a.output/'fragments.h5','x') as out:
            old=None
            if expanded:
                old=h5py.File(c['base_fragments']);bm=json.loads(Path(c['base_manifest']).read_text());m['records']=list(bm['records']);m['controls']=list(bm['controls']);m['reference_validity']=list(bm['reference_validity'])
            for row in c['training_targets']:
                if expanded and row['id'] in c['base_training_ids']:
                    old.copy(old['train/'+row['id']],out.require_group('train'),name=row['id']);continue
                ident=row['id'];bb=src[ident]['reference_backbone'][:];z=src[ident]['reference_z'][:];n=len(bb);g=out.create_group('train/'+ident);g.create_dataset('reference_backbone',data=bb);g.create_dataset('reference_z',data=z);g.attrs['family']=row['family'];g.attrs['length']=n
                valid=bool(backbone_geometry(bb[None])['coarse_valid'][0]);m['reference_validity'].append(dict(target_id=ident,coarse_valid=valid))
                if not valid:raise ValueError('Previously audited training backbone changed geometry')
                for fraction in (.2,.3,.4):
                    k=max(8,int(fraction*n))
                    for position,st in [('left',0),('center',(n-k)//2),('right',n-k)]:
                        if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Fragment encoding cap')
                        name=f'f{round(fraction*100)}_{position}';raw=bb[st:st+k].copy();fragment,degenerate=canonical_fragment(raw);mask=torch.ones(1,k,dtype=torch.bool,device='cuda');codes=F.layer_norm(encode_backbone(decoder,torch.from_numpy(fragment)[None].cuda(),mask),(8,));sequence=row['sequence'][st:st+k];fragment_features(codes[0],sequence,length=n,start=st)
                        dn=target_noise([ident],[4*k],3,seed=c['seed'],stream='fragment_roundtrip:'+name,device='cuda')*decoder.fm.scale_ref;_,rt=decoder(codes,mask,noise=dn,return_backbone=True);rt=rt[0].cpu().numpy();error=float(motif_error(rt[None],fragment,np.ones(k,bool))[0])
                        q=g.create_group('conditions/'+name);q.create_dataset('fragment',data=fragment);q.create_dataset('latent',data=codes[0].cpu().numpy());q.create_dataset('roundtrip',data=rt);q.attrs['start']=st;q.attrs['sequence']=sequence;q.attrs['near_degenerate']=degenerate
                        m['records'].append(dict(target_id=ident,condition=name,start=st,length=k,roundtrip_drms=error))
                        if name=='f30_center':
                            precision=np.float64 if c.get('pose_control_precision')=='fp64' else np.float32;rotation=np.array([[0,-1,0],[1,0,0],[0,0,1]],precision);posed,_=canonical_fragment(raw.astype(precision)@rotation+np.array([11,7,-3],precision));zc=F.layer_norm(encode_backbone(decoder,torch.from_numpy(posed)[None].cuda(),mask),(8,));control=dict(target_id=ident,coordinate_max_abs=float(np.max(abs(posed-fragment))),latent_rmse=float((zc-codes).square().mean().sqrt()));m['controls'].append(control)
                            if c.get('pose_control_precision')=='fp64':
                                exact,_=canonical_fragment(raw.astype(np.float64));control['exact_double_pose_max']=float(np.max(abs(exact-posed)))
                                if control['exact_double_pose_max']>1e-4:raise ValueError('Exact fragment pose failed')
                            if control['coordinate_max_abs']>1e-4 or control['latent_rmse']>1e-4:raise ValueError('Fragment pose control failed')
                out.flush();atomic_json(a.output/'manifest.json',m);print('encoded',ident,flush=True)
            if old is not None:old.close()
            for row in c['development_rows']:
                ident=row['target_id'];n=row['length'];k=max(8,int(.3*n));st=(n-k)//2;g=out.create_group('development/'+ident);q=g.create_group('conditions/f30_center');q.create_dataset('fragment',data=dev[ident+'/fragment'][:]);q.create_dataset('latent',data=dev[ident+'/fragment_latent'][:]);q.create_dataset('roundtrip',data=dev[ident+'/fragment_roundtrip'][:]);q.attrs['start']=st;q.attrs['sequence']=row['sequence'][st:st+k];g.attrs['family']=row['family'];g.attrs['length']=n;fragment_features(torch.from_numpy(q['latent'][:]),q.attrs['sequence'],length=n,start=st);m['development'].append(dict(target_id=ident,length=n,start=st,fragment_length=k))
        if len(m['records'])!=9*expected_proteins or len(m['controls'])!=expected_proteins or len(m['development'])!=16:raise ValueError('Incomplete fragment corpus')
        fraction=float(np.mean([r['roundtrip_drms']<=.5 for r in m['records']]))
        new_fraction=float(np.mean([r['roundtrip_drms']<=.5 for r in m['records'] if r['target_id'] not in c['base_training_ids']])) if expanded else fraction
        if expanded:m['new_fragment_roundtrip_fraction_under_half_A']=new_fraction
        m.update(status='complete',fragment_roundtrip_fraction_under_half_A=fraction,training_gate_passed=fraction>=.9 and new_fraction>=.9,fragments_sha256=sha(a.output/'fragments.h5'),peak_reserved_GiB=torch.cuda.max_memory_reserved()/2**30)
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
