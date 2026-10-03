"""Independent checks of decoded native labels and fixed cross-decoder preferences."""
import math
import h5py
import numpy as np
from fragment_validation_core import raw_rows
from latentfold.metrics import ca_metrics
from latentfold.fragment_preferences import motif_quality


def score_native_decodes(run,manifest,items,*,expected_count=16,minimum_both=10,minimum_long=4):
    c=manifest['config'];controls=manifest['native_controls'];rows=[]
    if len(items)!=expected_count or len(controls)!=expected_count or {r['target_id'] for r in controls}!=set(items):
        raise ValueError('Changed native decoder inventory')
    with h5py.File(run/'predictions.h5') as f,h5py.File(c['fragments']) as fr:
        if set(f['native'])!=set(items):raise ValueError('Changed native output targets')
        for ident,item in items.items():
            g=f['native/'+ident];source=fr['train/'+ident];n=item['length']
            z=g['latent'][:];bb=g['backbone'][:];repeat=g['same_batch_repeat'][:]
            if (z.shape!=(2,n,8) or not np.array_equal(z,np.broadcast_to(source['reference_z'][:],z.shape))
                    or bb.shape!=(2,n,4,3) or repeat.shape!=bb.shape
                    or not np.isfinite(bb).all() or not np.isfinite(repeat).all()):
                raise ValueError('Native latent or decoder inventory changed')
            error=float(np.max(abs(bb-repeat)));control=next(r for r in controls if r['target_id']==ident)
            if error>1e-4 or error!=control['coordinate_max_abs'] or not math.isfinite(control['peak_reserved_GiB']) or control['peak_reserved_GiB']>75:
                raise ValueError('Native repeat or resource audit failed')
            current=raw_rows(bb,item['fragment'],item['start'],'native_latent',ident,item['family'])
            for k,r in enumerate(current):r['full_native_ca_rmsd']=ca_metrics(bb[k,:,1],source['reference_backbone'][:,1])['ca_rmsd']
            rows.extend(current)
    qualified=[ident for ident in items if all(r['raw_gate_passed'] and r['full_native_ca_rmsd']<=1 for r in rows if r['target_id']==ident)]
    long_count=sum(items[i]['length']>256 for i in qualified)
    return dict(native_records=rows,native_controls=expected_count,native_raw_both_qualified=len(qualified),
                native_long_both_qualified=long_count,native_generation_gate=len(qualified)>=minimum_both and long_count>=minimum_long)


def native_pair(native, candidates, *, minimum_quality=.5, discovery_margin=.15, confirmation_margin=.1):
    if (len(native)!=2 or [r['generation_slot'] for r in native]!=[0,1]
            or len(candidates)!=4 or {r['generation_slot'] for r in candidates}!=set(range(4))
            or len({r['target_id'] for r in native+candidates})!=1):
        raise ValueError('Fixed two native realizations and four generated candidates required')
    errors=[r['full_native_ca_rmsd'] for r in native]
    if any(not math.isfinite(x) or x<0 for x in errors):raise ValueError('Invalid native roundtrip error')
    scores={r['generation_slot']:[motif_quality(r,range(4)),motif_quality(r,range(4,8))] for r in candidates}
    loser=min(scores,key=lambda k:(scores[k][0],k))
    first=motif_quality(native[0],range(4));second=motif_quality(native[1],range(4,8))
    discovery=first-scores[loser][0];confirmation=second-scores[loser][1]
    both_strict=all(motif_quality(r,range(8))==1 and r['full_native_ca_rmsd']<=1 for r in native)
    eligible=first>=minimum_quality and discovery>=discovery_margin
    confirmed=eligible and second>=minimum_quality and confirmation>=confirmation_margin and both_strict
    return dict(target_id=native[0]['target_id'],negative_slot=loser,generated_scores=scores,
                native_discovery_quality=first,native_confirmation_quality=second,
                discovery_margin=discovery,confirmation_margin=confirmation,
                native_both_strict=both_strict,eligible=eligible,confirmed=confirmed)
