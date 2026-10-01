"""Expand the cached latent-only training pool without new embeddings or downloads."""
import argparse
import hashlib
import json
import time
from pathlib import Path
import h5py
import numpy as np
from prepare_holdout import fasta, digest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--original',type=Path,required=True)
    p.add_argument('--exclusion-audit',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--per-bucket',type=int,default=4096)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    started=time.time();data=a.source/'data/phase1_dataset'
    original=json.loads(a.original.read_text());audit=json.loads(a.exclusion_audit.read_text())
    report=dict(status='running',records=[],count=0,original_manifest_sha256=digest(a.original),
        selection='SHA256(pilot-v1:id), same source caches and length buckets as original; train split only',
        per_bucket=a.per_bucket,exclusion_corpus_sha256=audit['exclusion_corpus_sha256'],
        residue_maps='Original pilot maps preserved; other records have unverified correspondence. Latent-only training permitted; geometry supervision prohibited.',
        dataset=str((a.output/'pilot.h5').resolve()))
    def save():
        path=a.output/'manifest.json';tmp=path.with_suffix('.tmp')
        tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(path)
    handles={};save()
    try:
        if original['status']!='complete':raise ValueError('original training audit incomplete')
        for corpus in audit['corpora']:
            if Path(corpus['file']).name in ('train_seqs.fasta','afdb_long_seqs.fasta'):
                if digest(Path(corpus['file']))!=corpus['sha256']:raise ValueError('source sequence export changed')
        short={name[2:]:seq for name,seq in fasta(data/'train_seqs.fasta') if name.startswith('k_')}
        long=dict(fasta(data/'afdb_long_seqs.fasta'))
        candidates=sorted({**short,**long}.items(),key=lambda r:hashlib.sha256(('pilot-v1:'+r[0]).encode()).digest())
        files=['dataset_100k_esmc.h5']+[f'dataset_afdb_long_{i}_esmc.h5' for i in range(4)]
        audited={r['file'] for r in audit['coverage'] if r['id_coverage']==1}
        for name in files:
            if name.replace('_esmc','') not in audited:raise ValueError('source not covered by training exclusion audit')
            handles[name]=h5py.File(data/name,'r')
        buckets={n:[] for n in (128,256,384,512)}
        for name,seq in candidates:
            if not 32<=len(seq)<=512:continue
            bucket=next(k for k in buckets if len(seq)<=k)
            if len(buckets[bucket])>=a.per_bucket:continue
            options=files[:1] if name in short else files[1:]
            sources=[k for k in options if name in handles[k]['train']]
            if len(sources)!=1:continue
            buckets[bucket].append(dict(id=name,sequence=seq,file=sources[0],bucket=bucket))
            if all(len(v)==a.per_bucket for v in buckets.values()):break
        report['selected_counts']={str(k):len(v) for k,v in buckets.items()};save()
        if any(len(v)!=a.per_bucket for v in buckets.values()):raise ValueError('insufficient cached training records')
        chosen=[r for v in buckets.values() for r in v];old={r['id']:r for r in original['records']}
        if not set(old)<={r['id'] for r in chosen}:raise ValueError('expanded selection lost original records')
        report['selected_ids_sha256']=hashlib.sha256('\n'.join(r['id'] for r in chosen).encode()).hexdigest();save()
        with h5py.File(original['dataset'],'r') as prior,h5py.File(report['dataset'],'w') as out:
            group=out.create_group('train')
            for meta in chosen:
                name=meta['id'];g=handles[meta['file']]['train'][name];seq=str(g.attrs['sequence']);n=len(seq)
                if seq!=meta['sequence']:raise ValueError('source sequence differs from exclusion export')
                arrays={k:g[k][:] for k in ('z','ca_coords','esm2_emb')}
                if arrays['z'].shape!=(n,8) or arrays['ca_coords'].shape!=(n,3) or arrays['esm2_emb'].shape!=(n,2560):raise ValueError('cache shapes differ')
                arrays['esm2_emb']=arrays['esm2_emb'].astype(np.float16)
                if not all(np.isfinite(x).all() for x in arrays.values()):raise ValueError('nonfinite cached arrays')
                if name in old:
                    for key,x in arrays.items():
                        if not np.array_equal(x,prior['train'][name][key][:]):raise ValueError('original training record changed')
                    arrays['adjacent']=prior['train'][name]['adjacent'][:]
                dst=group.create_group(name)
                for key,x in arrays.items():dst.create_dataset(key,data=x)
                dst.attrs.update(sequence=seq,source_file=str(data/meta['file']),source_split='train')
                report['records'].append(dict(id=name,length=n,bucket=meta['bucket'],source_file=str(data/meta['file']),
                    sequence_sha256=hashlib.sha256(seq.encode()).hexdigest(),
                    array_sha256={k:hashlib.sha256(x.tobytes()).hexdigest() for k,x in arrays.items()},
                    has_verified_residue_map=name in old))
                if len(report['records'])%256==0:
                    report['count']=len(report['records']);out.flush();save();print('verified',report['count'],flush=True)
        report.update(status='complete',count=len(report['records']),original_records_verified=len(old))
    except BaseException as error:
        report.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        for h in handles.values():h.close()
        report['elapsed_seconds']=time.time()-started;save()


if __name__=='__main__':main()
