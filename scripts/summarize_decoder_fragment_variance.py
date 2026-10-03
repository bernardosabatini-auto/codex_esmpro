"""Audit every crossed sample and separate decoder variation from motif error."""
import argparse
import json
from pathlib import Path
import h5py
import numpy as np
from decoder_fragment_variance_core import audit,motif_distances,variance_components
from evaluate_decoder_fragment_variance import check_backbones
from fragment_validation_core import raw_rows
from prepare_overfit import sha


def analyze(run):
    mp=run/'manifest.json';m=json.loads(mp.read_text()) if mp.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'))
    c=m['config'];spec=audit(c)
    if (m['training_updates_executed']!=0 or len(m['timing'])!=32 or len(m['controls'])!=64
            or m['predictions_sha256']!=sha(run/'predictions.h5') or any(r['peak_reserved_GiB']>75 for r in m['timing'])):raise ValueError('Changed crossed study inventory or resources')
    expected={(kind,i) for i in c['target_ids'] for kind in ('historical','native_batch')}
    if {(r['kind'],r['target_id']) for r in m['controls']}!=expected:raise ValueError('Missing parity controls')
    records=[];per_protein=[]
    with h5py.File(run/'predictions.h5') as f,h5py.File(c['baseline_predictions']) as old,h5py.File(c['fragments']) as fr:
        if set(f)!={'generated','native'} or any(set(f[k])!=set(c['target_ids']) for k in f):raise ValueError('Changed stored target inventory')
        for source in c['selected']:
            ident=source['id'];n=source['length'];q=fr['train/'+ident+'/conditions/c20_center'];fragment=q['fragment'][:];start=int(q.attrs['start'])
            g=f['generated/'+ident];ng=f['native/'+ident];bb=g['backbone'][:];native=ng['backbone'][:]
            if (bb.shape!=(4,5,n,4,3) or native.shape!=(5,n,4,3) or ng['single_backbone'].shape!=(n,4,3)
                    or not np.isfinite(bb).all() or not np.isfinite(native).all()
                    or not np.array_equal(g['latent'][:],old['new/'+ident+'/latent'][:])
                    or not np.array_equal(ng['latent'][:],fr['train/'+ident+'/reference_z'][:])):raise ValueError('Changed fixed latent or decoded inventory')
            diagonal=np.stack([bb[k,k] for k in range(4)])
            for kind,actual,reference in [('historical',diagonal,old['new/'+ident+'/backbone'][:]),('native_batch',ng['single_backbone'][:][None],native[:1])]:
                check=check_backbones(actual,reference,fragment,start,ident);logged=next(r for r in m['controls'] if (r['kind'],r['target_id'])==(kind,ident))
                if any(check[k]!=logged[k] for k in check):raise ValueError('Stored parity values changed')
            target=motif_distances(fragment,0);values=motif_distances(bb,start);components=variance_components(values,target)
            generated_rows=[]
            for latent_slot in range(4):
                rr=raw_rows(bb[latent_slot],fragment,start,'generated',ident,source['family'])
                generated_rows.extend([dict(r,flow_slot=latent_slot,decoder_slot=r['generation_slot'],bucket=source['bucket']) for r in rr])
            native_rows=[dict(r,decoder_slot=r['generation_slot'],bucket=source['bucket']) for r in raw_rows(native,fragment,start,'native',ident,source['family'])]
            records.extend(generated_rows+native_rows)
            native_dist=motif_distances(native,start);native_error=float(np.mean((native_dist-target)**2));native_var=float(np.mean((native_dist-native_dist.mean(0))**2))
            per_protein.append(dict(target_id=ident,family=source['family'],bucket=source['bucket'],**components,
                                    native_squared_distance_error=native_error,native_decoder_variance=native_var,
                                    generated_raw=sum(r['raw_gate_passed'] for r in generated_rows),generated_valid=sum(r['coarse_valid'] for r in generated_rows),
                                    original_diagonal_raw=sum(r['raw_gate_passed'] for r in generated_rows if r['flow_slot']==r['decoder_slot']),
                                    oracle_latents_any_raw=sum(any(r['raw_gate_passed'] for r in generated_rows if r['flow_slot']==k) for k in range(4)),
                                    native_raw=sum(r['raw_gate_passed'] for r in native_rows),native_valid=sum(r['coarse_valid'] for r in native_rows)))
    if len(records)!=800 or len(per_protein)!=32:raise ValueError('Incomplete crossed decoding')
    summary=[]
    for bucket in (None,128,256,384,512):
        rr=[r for r in per_protein if bucket is None or r['bucket']==bucket];avg=lambda key:float(np.mean([r[key] for r in rr]));error=avg('mean_squared_distance_error');within=avg('within_latent_decoder_variance');total=avg('total_variance')
        summary.append(dict(bucket=bucket,proteins=len(rr),generated_samples=20*len(rr),native_samples=5*len(rr),
                            mean_squared_distance_error=error,systematic_distance_error=avg('systematic_distance_error'),within_latent_decoder_variance=within,between_latent_variance=avg('between_latent_variance'),total_variance=total,
                            decoder_fraction_of_error=within/error if error else None,decoder_fraction_of_variance=within/total if total else None,
                            native_squared_distance_error=avg('native_squared_distance_error'),native_decoder_variance=avg('native_decoder_variance'),
                            **{k:sum(r[k] for r in rr) for k in ('generated_raw','generated_valid','original_diagonal_raw','oracle_latents_any_raw','native_raw','native_valid')}))
    return dict(status='complete',manifest_sha256=sha(mp),predictions_sha256=m['predictions_sha256'],protocol_sha256=sha(c['protocol']),historical_predictions_audited=128,native_batch_controls=32,
                summary=summary,per_protein=per_protein,records=records,elapsed_seconds=m['elapsed_seconds'],peak_reserved_GiB=max(r['peak_reserved_GiB'] for r in m['timing']),scope=spec['scope'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    interpretation=''
    if d['status']=='complete':
        s=d['summary'][0]
        interpretation=(f"Across32 proteins and128 fixed generated latents, within-latent decoder variance accounts for {100*s['decoder_fraction_of_error']:.3f}% of squared motif-distance error and {100*s['decoder_fraction_of_variance']:.3f}% of motif-distance variance. "
                        f"Original raw motif successes: {s['original_diagonal_raw']}/128; oracle any-of-five decoder success: {s['oracle_latents_any_raw']}/128. "
                        f"Native full-latent controls pass {s['native_raw']}/{s['native_samples']} raw motif checks.\n\n"
                        "These are finite five-noise variance identities, not causal attribution of every systematic error to the generator. Native controls show that the frozen codec can represent these motifs in their native contexts; they do not prove that every generated scaffold admits the requested motif. "
                        "The panel is repeatedly used training data. Raw motif geometry does not establish same-refold designability, and oracle decoder selection is not a deployable sampling result.\n\n")
    a.output.with_suffix('.md').write_text('# Fixed-latent decoder variance\n\n'+interpretation+'```json\n'+json.dumps({k:v for k,v in d.items() if k not in ('records','per_protein')},indent=2)+'\n```\n')
    print(json.dumps(d.get('summary',d)))


if __name__=='__main__':main()
