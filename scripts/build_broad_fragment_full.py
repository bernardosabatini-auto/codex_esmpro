"""Frozen source-backed targets, preserved base inputs, and additive short crops."""
import argparse,hashlib,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.backbone import align_backbone_to_reference
from latentfold.decoder import load_proteinae
from latentfold.precision import inference_precision
from latentfold.fragment_codec_batch import run_codec_batches
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.fragment_designability import motif_fit
from broad_fragment_full_core import audit,crops,gates,verify_original
from generate_isolated_motif import canonical_fragment
from prepare_overfit import sha
from profile_gpu import atomic_json


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());new,base,history=audit(c);spec=c['spec'];a.output.mkdir(exist_ok=False);tick=time.monotonic();m=dict(status='running',config=c,records=[],controls=[],batches=[],training_updates_executed=0);atomic_json(a.output/'manifest.json',m);control_ids={next(r['id'] for r in new if r['bucket']==b) for b in (128,256,384,512)}
    try:
        torch.set_num_threads(2);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False);rows=[dict(r,base=False) for r in new]+[dict(r,base=True) for r in base]
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['cache']) as cache,h5py.File(c['source_backbones']) as source,h5py.File(c['base_fragments']) as old,h5py.File(a.output/'fragments.h5','x') as out:
            out.create_group('train');out.create_group('rejected');out.create_group('historical')
            for offset in range(0,len(rows),spec['chunk_proteins']):
                if time.monotonic()-tick>spec['work_cap_seconds']:raise TimeoutError('Full fragment construction cap')
                chunk=rows[offset:offset+spec['chunk_proteins']];meta={};inputs=[];full_items={}
                if offset==0:
                    for ident in history:
                        q=old['development/'+ident+'/conditions/f30_center'];inputs.append(dict(key='historical/'+ident,target_id=ident,backbone=q['fragment'][:],stream='historical_unused:0'))
                for row in chunk:
                    ident=row['id'];n=row['length']
                    if row['base']:
                        g=old['train/'+ident];bb=g['reference_backbone'][:];z=g['reference_z'][:];ca_error=None
                    else:
                        g=cache['train/'+ident];z=g['z'][:];ca=g['ca_coords'][:]
                        if str(g.attrs['sequence'])!=row['sequence'] or str(source[ident].attrs['sequence'])!=row['sequence']:raise ValueError('Changed source sequence')
                        for key,value in [('z',z),('ca_coords',ca)]:
                            if not np.isfinite(value).all() or hashlib.sha256(value.tobytes()).hexdigest()!=row['array_sha256'][key]:raise ValueError('Changed cached array')
                        raw=torch.from_numpy(source[ident+'/backbone'][:]).cuda();proxy=raw.clone();proxy[:,1]=torch.from_numpy(ca).cuda();reference=align_backbone_to_reference(raw[None],proxy,torch.ones(n,dtype=torch.bool,device='cuda'))[0];bb=reference.cpu().numpy();ca_error=float(np.sqrt(np.mean(np.sum((bb[:,1]-ca)**2,-1))))
                        if ca_error>.02:raise ValueError('Source frame correspondence failed')
                        item=dict(key='full/'+ident,target_id=ident,backbone=bb,reference_latent=z,stream='broad_full:0');inputs.append(item);full_items[ident]=item
                    conditions=crops(bb,row['sequence'],short_only=row['base']);meta[ident]=dict(row=row,bb=bb,z=z,ca_error=ca_error,conditions=conditions)
                    for q in conditions:
                        inputs.append(dict(key='crop/'+ident+'/'+q['name'],target_id=ident,backbone=q['fragment'],stream='broad_fragment:'+q['name']))
                        if ident in control_ids and q['name'] in ('f30_center','c20_center'):
                            k=len(q['fragment']);raw=bb[q['start']:q['start']+k].astype(np.float64);posed,_=canonical_fragment(raw@np.array([[0,-1,0],[1,0,0],[0,0,1]],np.float64)+np.array([11,7,-3],np.float64));q['pose_fragment']=posed;inputs.append(dict(key='pose/'+ident+'/'+q['name'],target_id=ident,backbone=posed,stream='broad_fragment:'+q['name']))
                results,batches=run_codec_batches(decoder,inputs,batch_size=16,seed=spec['seed'],length_multiple=1);m['batches'].extend(batches)
                if max(r['peak_reserved_GiB'] for r in batches)>spec['max_reserved_GiB']:raise ValueError('Full codec memory cap')
                if offset==0:
                    for ident in history:
                        z=results['historical/'+ident]['latent'];reference=old['development/'+ident+'/conditions/f30_center/latent'][:];error=float(np.max(abs(z-reference)));m['controls'].append(dict(kind='historical',target_id=ident,latent_max_abs=error));out.create_dataset('historical/'+ident,data=z)
                        if error>1e-5:raise ValueError('Historical code changed')
                for row in chunk:
                    ident=row['id'];v=meta[ident];bb=v['bb'];record=dict(target_id=ident,base=row['base'],length=row['length'],bucket=row['bucket'],source_ca_error=v['ca_error'],source_valid=bool(backbone_geometry(bb[None])['coarse_valid'][0]),conditions=[])
                    if row['base']:
                        old.copy(old['train/'+ident],out['train'],name=ident);g=out['train/'+ident];record['qualified']=True
                    else:
                        full=results['full/'+ident];parity=float(np.sqrt(np.mean((full['encoded']-v['z'])**2)));valid=bool(backbone_geometry(full['backbone'][None])['coarse_valid'][0]);rmsd=ca_metrics(full['backbone'][:,1],bb[:,1])['ca_rmsd']
                        if not np.isfinite(parity) or parity>.05 or not np.array_equal(full['latent'],v['z']):raise ValueError('Full cached target parity failed')
                        qualified=record['source_valid'] and valid and rmsd<=1;record.update(full_encoding_rmse=parity,decoded_valid=valid,decoded_ca_rmsd=rmsd,qualified=qualified);g=out.create_group(('train/' if qualified else 'rejected/')+ident);g.attrs.update(length=row['length'],family=row['family'])
                        for key,value in [('reference_backbone',bb),('reference_z',v['z']),('encoded_z',full['encoded']),('roundtrip',full['backbone'])]:g.create_dataset(key,data=value)
                        if ident in control_ids:
                            check,extra=run_codec_batches(decoder,[full_items[ident]],batch_size=1,seed=spec['seed'],length_multiple=1);m['batches'].extend(extra);check=check['full/'+ident];metric=ca_metrics(check['backbone'][:,1],full['backbone'][:,1]);error=float(np.max(abs(check['encoded']-full['encoded'])));same=bool(record['source_valid'] and backbone_geometry(check['backbone'][None])['coarse_valid'][0] and ca_metrics(check['backbone'][:,1],bb[:,1])['ca_rmsd']<=1)==qualified;m['controls'].append(dict(kind='singleton',target_id=ident,latent_max_abs=error,same_qualification=same,**metric));g.create_dataset('singleton_encoded',data=check['encoded']);g.create_dataset('singleton_backbone',data=check['backbone'])
                            if error>1e-4 or metric['ca_rmsd']>.01 or metric['ca_lddt']<.999 or not same:raise ValueError('Singleton/full-batch parity failed')
                    for q in v['conditions']:
                        result=results['crop/'+ident+'/'+q['name']];r=g.create_group('conditions/'+q['name']);r.attrs.update(start=q['start'],sequence=q['sequence'],near_degenerate=q['near_degenerate'])
                        for key,value in [('fragment',q['fragment']),('latent',result['latent']),('roundtrip',result['backbone'])]:
                            if not np.isfinite(value).all():raise ValueError('Nonfinite crop output')
                            r.create_dataset(key,data=value)
                        record['conditions'].append(dict(name=q['name'],**motif_fit(result['backbone'],q['fragment'],0)))
                        if 'pose_fragment' in q:
                            pose=results['pose/'+ident+'/'+q['name']]['latent'];coordinate=float(np.max(abs(q['pose_fragment']-q['fragment'])));error=float(np.max(abs(pose-result['latent'])));m['controls'].append(dict(kind='pose',target_id=ident,condition=q['name'],coordinate_max_abs=coordinate,latent_max_abs=error));r.create_dataset('pose_fragment',data=q['pose_fragment']);r.create_dataset('pose_latent',data=pose)
                            if coordinate>1e-4 or error>1e-4:raise ValueError('Crop pose control failed')
                    if row['base']:verify_original(old['train/'+ident],g)
                    m['records'].append(record)
                out.flush();atomic_json(a.output/'manifest.json',m)
        if len(m['controls'])!=16:raise ValueError('Missing full-data controls')
        m.update(gates(m['records']));m.update(status='complete',fragments_sha256=sha(a.output/'fragments.h5'))
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:m['elapsed_seconds']=time.monotonic()-tick;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
