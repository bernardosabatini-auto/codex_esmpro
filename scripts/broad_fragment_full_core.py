import json
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha
from broad_codec_batch_core import audit as codec_audit
from generate_isolated_motif import canonical_fragment


def audit(c):
    for key in ('protocol','codec_manifest','codec_report','candidates','base_manifest','base_fragments','source_manifest','source_backbones','decoder_checkpoint'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed full-data source '+key)
    spec=json.loads(Path(c['protocol']).read_text());cm=json.loads(Path(c['codec_manifest']).read_text());cd=json.loads(Path(c['codec_report']).read_text());bm=json.loads(Path(c['candidates']).read_text());base=json.loads(Path(c['base_manifest']).read_text());sm=json.loads(Path(c['source_manifest']).read_text())
    if spec!=c['spec'] or cd['status']!='complete' or not cd['profile_qualified'] or cd['manifest_sha256']!=c['codec_manifest_sha256'] or cm['config']['spec']['length_multiple']!=1 or cm['config']['spec']['batch_size']!=16 or cm['config']['decoder_checkpoint']!=c['decoder_checkpoint']:raise ValueError('Unqualified exact-length codec')
    if base['status']!='complete' or not base['training_gate_passed'] or base['fragments_sha256']!=c['base_fragments_sha256'] or bm['status']!='complete' or sm['status']!='complete' or not sm['source_gate_passed'] or sm['backbones_sha256']!=c['source_backbones_sha256']:raise ValueError('Unqualified corpus source')
    k=c['partition'];new=bm['selected'][k::4];old=sorted(base['config']['training_targets'],key=lambda r:(r['bucket'],r['id']))[k::4]
    if k not in range(4) or len(new)!=1920 or len(old)!=128 or len(sm['records'])!=1920 or sm['rejections'] or sm['target_ids']!=[r['id'] for r in new] or sm['cache']!=c['cache'] or {r['id'] for r in new}&{r['id'] for r in old}:raise ValueError('Changed data partition')
    return new,old,codec_audit(cm['config'])['config']['control_ids']


def crops(backbone,sequence,*,short_only=False):
    n=len(backbone);result=[]
    if len(sequence)!=n:raise ValueError('Source sequence length mismatch')
    for prefix,k in ([] if short_only else [(f'f{round(f*100)}',max(8,int(f*n))) for f in (.2,.3,.4)])+[('c20',20)]:
        for position,start in [('left',0),('center',(n-k)//2),('right',n-k)]:
            fragment,degenerate=canonical_fragment(backbone[start:start+k].astype(np.float64));result.append(dict(name=prefix+'_'+position,start=start,sequence=sequence[start:start+k],fragment=fragment,near_degenerate=degenerate))
    return result


def verify_original(old,new):
    if dict(old.attrs)!=dict(new.attrs):raise ValueError('Original protein attributes changed')
    for key in ('reference_backbone','reference_z'):
        if not np.array_equal(old[key][:],new[key][:]):raise ValueError('Original target changed')
    if set(new['conditions'])!=set(old['conditions'])|{'c20_left','c20_center','c20_right'}:raise ValueError('Changed additive condition inventory')
    for name,q in old['conditions'].items():
        other=new['conditions/'+name]
        if dict(q.attrs)!=dict(other.attrs) or set(q)!=set(other) or any(not np.array_equal(q[k][:],other[k][:]) for k in q):raise ValueError('Original condition changed')


def gates(records):
    new=[r for r in records if not r['base']];old=[r for r in records if r['base']]
    if len(new)!=1920 or len(old)!=128 or len({r['target_id'] for r in records})!=2048:raise ValueError('Changed complete data ledger')
    frac=[q for r in new for q in r['conditions'] if q['name'].startswith('f')];short=[q for r in records for q in r['conditions'] if q['name'].startswith('c20')]
    if len(frac)!=1920*9 or len(short)!=2048*3:raise ValueError('Changed fragment audit denominator')
    good=lambda rows:sum(q['motif_ca_rmsd']<=.5 and q['motif_drms']<=.5 for q in rows)
    n=sum(r['qualified'] for r in new);a,b=good(frac),good(short)
    return dict(qualified_new_proteins=n,retained_training_proteins=n+128,fractional_roundtrips=len(frac),qualified_fractional_roundtrips=a,short_roundtrips=len(short),qualified_short_roundtrips=b,data_gate_passed=n/1920>=.9 and a/len(frac)>=.9 and b/len(short)>=.9)
