"""CPU-only, sequence-selected training expansion; no structural outcome selection."""
import argparse,hashlib,json,subprocess,time
from pathlib import Path
from collections import Counter
import h5py
from audit_training_expansion import components
from prepare_holdout import fasta
from prepare_overfit import sha
from profile_gpu import atomic_json


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/fragment_broad_cache_protocol.json';spec=json.loads(protocol.read_text());basepath=root/spec['base_manifest'];base=json.loads(basepath.read_text())['config']['training_targets'];extra=root/'runs/fragment_extra_development_20261003/manifest.json';em=json.loads(extra.read_text());excludepath=extra.parent/'exclusion.fasta';mm=Path('/n/holylabs/bsabatini_lab/Users/bsabatini/mmseqs/bin/mmseqs');a.output.mkdir(exist_ok=False);tick=time.monotonic();source_manifest=root/spec['source_manifest'];sm=json.loads(source_manifest.read_text());sources=[protocol,basepath,extra,excludepath,mm,source_manifest,Path(__file__).resolve()]
    if sm['status']!='complete' or sm['count']!=16384 or sm['dataset']!=spec['source']:raise ValueError('Unqualified inherited cache')
    m=dict(status='running',sources={str(x):sha(x) for x in sources},source=spec['source'],source_size=Path(spec['source']).stat().st_size,records_scanned=0,commands=[],scope='CPU-only candidate selection. No decoded structures, teacher outputs, or evaluation scores used. Source training overlap with the inherited model persists.');atomic_json(a.output/'manifest.json',m)
    try:
        exclusions={s for _,s in fasta(excludepath)}
        exclusions.update(r['sequence'] for r in em['selected'])
        exclusions.update(r['sequence'] for r in base)
        rows={};counts=Counter();rejections=Counter();salt=spec['salt'];quota=spec['candidate_pool_per_bucket'];order=lambda i:hashlib.sha256((salt+i).encode()).hexdigest()
        with h5py.File(spec['source']) as f:
            train=f['train'];metadata={r['id']:r for r in sm['records']};ids=sorted(metadata,key=order);m['source_train_records']=len(ids);atomic_json(a.output/'manifest.json',m)
            for ident in ids:
                g=train[ident];meta=metadata[ident];n=meta['length'];m['records_scanned']+=1
                if n<50 or n>512:rejections['length']+=1;continue
                bucket=next(b for b in (128,256,384,512) if n<=b)
                if counts[bucket]>=quota:continue
                seq=str(g.attrs.get('sequence',''))
                if hashlib.sha256(seq.encode()).hexdigest()!=meta['sequence_sha256'] or g.attrs['source_split']!='train':raise ValueError('Changed cached sequence or provenance')
                if len(seq)!=n or set(seq)-set('ACDEFGHIKLMNPQRSTVWY'):rejections['sequence']+=1;continue
                if g['z'].shape!=(n,8) or g['ca_coords'].shape!=(n,3):rejections['shape']+=1;continue
                if seq in exclusions:rejections['exact_excluded_sequence']+=1;continue
                rows[ident]=dict(id=ident,sequence=seq,sequence_sha256=hashlib.sha256(seq.encode()).hexdigest(),length=n,bucket=bucket,source_file=spec['source'],source_group='train/'+ident,array_sha256={k:meta['array_sha256'][k] for k in ('z','ca_coords')},original_source_file=meta['source_file']);counts[bucket]+=1
                if len(rows)%512==0:m.update(pool_counts=dict(counts),metadata_rejections=dict(rejections));atomic_json(a.output/'manifest.json',m)
                if all(counts[b]>=quota for b in (128,256,384,512)):break
        m.update(pool_counts=dict(counts),metadata_rejections=dict(rejections),pool_sequences=len(rows),exclusion_sequences=len(exclusions));atomic_json(a.output/'manifest.json',m)
        if any(counts[b]<spec['bucket_counts'][str(b)] for b in (128,256,384,512)):raise ValueError('Insufficient metadata-eligible bucket coverage')
        query=a.output/'pool.fasta';query.write_text(''.join(f'>{i}\n{r["sequence"]}\n' for i,r in sorted(rows.items())))
        exclude=a.output/'exclusion.fasta';exclude.write_text(''.join(f'>excluded_{k}\n{s}\n' for k,s in enumerate(sorted(exclusions))))
        for label,database in [('self',query),('exclude',exclude)]:
            command=[str(mm),'easy-search',str(query),str(database),str(a.output/(label+'.tsv')),str(a.output/('tmp_'+label)),'-s','7.5','-e','1e-3','--max-seqs','20000','--threads','2','--split-memory-limit','4G','--format-output','query,target,fident,qcov,tcov','-v','1'];m['commands'].append(command);atomic_json(a.output/'manifest.json',m)
            with (a.output/(label+'.log')).open('w') as log:subprocess.run(command,check=True,stdout=log,stderr=subprocess.STDOUT,timeout=3600)
        groups=components(rows,(a.output/'self.tsv').read_text());blocked=set()
        for line in (a.output/'exclude.tsv').read_text().splitlines():
            q,t,identity,qcov,tcov=line.split('\t')
            if float(identity)>=.3 and max(float(qcov),float(tcov))>=.5:blocked.add(groups[q])
        selected=[];used=set();basecounts=Counter(r['bucket'] for r in base)
        for bucket in (128,256,384,512):
            wanted=spec['bucket_counts'][str(bucket)]-basecounts[bucket];chosen=[]
            for ident in sorted(rows,key=order):
                r=rows[ident];family=groups[ident]
                if r['bucket']!=bucket or family in blocked or family in used:continue
                chosen.append(dict(r,family=family));used.add(family)
                if len(chosen)==wanted:break
            if len(chosen)!=wanted:raise ValueError(f'Insufficient independent candidates in bucket{bucket}: {len(chosen)}/{wanted}')
            selected.extend(chosen)
        m.update(status='complete',new_proteins=len(selected),training_proteins=len(selected)+len(base),selected=selected,sequence_components=len(set(groups.values())),blocked_components=len(blocked),source_fasta_hashes={str(p):sha(p) for p in (query,exclude,a.output/'self.tsv',a.output/'exclude.tsv')},pilot_ids=[r['id'] for b in (128,256,384,512) for r in sorted((r for r in selected if r['bucket']==b),key=lambda r:order(r['id']))[:16]])
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:m['elapsed_seconds']=time.monotonic()-tick;atomic_json(a.output/'manifest.json',m)
    print(json.dumps({k:m[k] for k in ('status','new_proteins','training_proteins','sequence_components','blocked_components','elapsed_seconds')}))

if __name__=='__main__':main()
