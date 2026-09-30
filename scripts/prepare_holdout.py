"""CPU-only unused experimental holdout selection with explicit residue maps.

Recover candidates from the earlier selection list that were never in its 626
scored cache. Use full polymer sequence as input and observed CA indices as the
scoring map. Screen against all documented training/benchmark/development data.
No model scores are computed while selecting the test set.
"""
import argparse,collections,csv,gzip,hashlib,io,json,subprocess,time,urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import h5py
import numpy as np
from Bio.PDB.MMCIF2Dict import MMCIF2Dict

AA=dict(zip('ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL'.split(),'ARNDCQEGHILKMFPSTWYV'));AA['MSE']='M'


def fasta(path):
    name=None;seq=[]
    with path.open() as f:
        for line in f:
            if line.startswith('>'):
                if name is not None:yield name,''.join(seq)
                name=line[1:].split()[0];seq=[]
            else:seq.append(line.strip())
        if name is not None:yield name,''.join(seq)


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def parse_cif(path,chain,sequence):
    cif=MMCIF2Dict(str(path));prefix='_atom_site.'
    required=('auth_asym_id','label_seq_id','label_atom_id','label_comp_id','label_alt_id','Cartn_x','Cartn_y','Cartn_z','auth_seq_id','pdbx_PDB_ins_code','pdbx_PDB_model_num')
    cols={key:cif[prefix+key] for key in required};atoms={};mapping={}
    for i,ch in enumerate(cols['auth_asym_id']):
        if ch!=chain or cols['pdbx_PDB_model_num'][i]!='1' or cols['label_alt_id'][i] not in ('.','?','A','1'):continue
        position=cols['label_seq_id'][i]
        if position in ('.','?'):continue
        position=int(position)-1;atom=cols['label_atom_id'][i]
        if atom not in ('N','CA','C','O'):continue
        residue=AA.get(cols['label_comp_id'][i])
        if not 0<=position<len(sequence) or residue!=sequence[position]:raise ValueError('polymer sequence correspondence mismatch')
        atoms.setdefault(position,{})[atom]=[float(cols[k][i]) for k in ('Cartn_x','Cartn_y','Cartn_z')]
        mapping[position]=dict(label_seq_id=position+1,auth_chain=chain,auth_seq_id=cols['auth_seq_id'][i],insertion=cols['pdbx_PDB_ins_code'][i])
    observed=sorted(i for i,v in atoms.items() if 'CA' in v)
    if len(observed)<50 or len(observed)/len(sequence)<.9:raise ValueError('less than 50 CA or less than 90 percent observed')
    ca=np.array([atoms[i]['CA'] for i in observed],dtype=np.float32)
    if not np.isfinite(ca).all():raise ValueError('nonfinite coordinates')
    return dict(sequence=sequence,observed_indices=observed,ca_coords=ca.tolist(),
                residue_map=[mapping[i] for i in observed],backbone_complete=sum(all(k in atoms[i] for k in ('N','CA','C','O')) for i in observed),
                adjacent=[b==a+1 for a,b in zip(observed,observed[1:])])


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--threads',type=int,default=4)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);data=a.source/'data/phase1_dataset'
    report=dict(status='running',started=time.time(),corpora=[],coverage=[],candidates=[],rejections=[])
    state=a.output/'holdout.json'
    def save():state.write_text(json.dumps(report,indent=2)+'\n')
    try:
        # Reuse sequence exports after ID coverage and sequence spot checks.
        # Every inherited input is read only; corpus and search databases are local.
        sequences={};corpus=a.output/'exclude.fasta';seen=set()
        with corpus.open('w') as out:
            for filename in ('train_seqs.fasta','afdb_long_seqs.fasta','short2_seqs.fasta','pdb_long_seqs.fasta','all_val_seqs.fasta'):
                path=data/filename;count=0
                for name,seq in fasta(path):
                    canonical=name[2:] if name.startswith(('k_','a_')) else name
                    if canonical in sequences and sequences[canonical]!=seq:raise ValueError('conflicting inherited sequences')
                    sequences[canonical]=seq
                    out.write(f'>{filename}|{name}\n{seq}\n');count+=1
                report['corpora'].append(dict(file=str(path),sha256=digest(path),sequences=count));save()
            cache_files=['dataset_100k.h5']+[f'dataset_afdb_train_{i}.h5' for i in range(2)]+[f'dataset_afdb_long_{i}.h5' for i in range(4)]+[f'dataset_afdb_short2_{i}.h5' for i in range(4)]+['dataset_pdb_long.h5']
            for filename in cache_files:
                with h5py.File(data/filename,'r') as f:
                    group=f['train'];names=list(group);missing=[n for n in names if n not in sequences]
                    if missing:raise ValueError(f'{filename}: {len(missing)} missing from exclusion corpus')
                    sampled=sorted(names,key=lambda n:hashlib.sha256(n.encode()).digest())[:32]
                    for name in sampled:
                        seq=str(group[name].attrs['sequence'])
                        if seq!=sequences[name]:raise ValueError(f'{filename}:{name}: stale sequence export')
                    report['coverage'].append(dict(file=filename,train_records=len(names),id_coverage=1.,sequence_checks=len(sampled)))
                    seen.update(names)
                print(json.dumps(report['coverage'][-1]),flush=True);save()
            files=['dataset_pdb_train.h5','dataset_casp512.h5','dataset_casp.h5','dataset_cameo22.h5','dataset_apo.h5','dataset_codnas.h5','dataset_exp_val.h5']
            for filename in files:
                with h5py.File(data/filename,'r') as f:
                    for split in f:
                        for name in f[split]:
                            seq=str(f[split][name].attrs['sequence']);seen.add(name)
                            out.write(f'>{filename}|{split}|{name}\n{seq}\n')
                print('excluded',filename,flush=True)
        report['exclusion_corpus_sha256']=digest(corpus);report['corpus_note']='Complete training ID coverage; inherited FASTA sequence contents checked on 32 deterministic records per shard, not re-extracted in full.';save()
        selected=list(csv.DictReader((a.source/'data/pdb/exp_val_chains.tsv').open(),delimiter='\t'))
        selected=[r for r in selected if f"{r['pdb_id']}_{r['chain']}" not in seen and 50<=int(r['length'])<=512]
        wanted={f"{r['pdb_id']}_{r['chain']}" for r in selected};seqs={}
        with gzip.open(a.source/'data/pdb/pdb_seqres.txt.gz','rt') as f:
            name=None
            for line in f:
                if line.startswith('>'):name=line[1:].split()[0]
                elif name in wanted:seqs[name]=seqs.get(name,'')+line.strip()
        selected.sort(key=lambda r:hashlib.sha256(f"holdout-v1:{r['pdb_id']}_{r['chain']}".encode()).digest())
        raw=a.output/'mmcif';raw.mkdir();pool=[]
        def fetch(row):
            name=f"{row['pdb_id']}_{row['chain']}";path=raw/f"{row['pdb_id']}.cif"
            try:
                seq=seqs[name]
                if len(seq)>512 or any(s not in set(AA.values()) for s in seq):raise ValueError('invalid full polymer sequence')
                if not path.exists():
                    with urllib.request.urlopen(f"https://files.rcsb.org/download/{row['pdb_id'].upper()}.cif",timeout=45) as response:
                        contents=response.read(128*1024**2+1)
                    if len(contents)>128*1024**2:raise ValueError('mmCIF download exceeds 128 MiB cap')
                    path.write_bytes(contents)
                result=parse_cif(path,row['chain'],seq)
                return dict(id=name,source_url=f"https://files.rcsb.org/download/{row['pdb_id'].upper()}.cif",source_sha256=digest(path),resolution=float(row['resolution']),method=row['method'],**result)
            except Exception as error:return dict(id=name,rejection=f'{type(error).__name__}: {error}')
        # Bounded source recovery, deterministic candidate order and selection.
        for start in range(0,min(len(selected),256),8):
            with ThreadPoolExecutor(max_workers=2) as workers:batch=list(workers.map(fetch,selected[start:start+8]))
            for result in batch:
                if 'rejection' in result:report['rejections'].append(result)
                else:pool.append(result)
            report['candidates']=[dict(id=r['id'],length=len(r['sequence'])) for r in pool];save()
            print('source recovery',start+len(batch),'accepted',len(pool),flush=True)
            if sum(len(r['sequence'])<=256 for r in pool)>=48 and sum(len(r['sequence'])>256 for r in pool)>=48:break
        if not pool:raise ValueError('no usable unscored experimental candidates')
        query=a.output/'candidates.fasta'
        query.write_text(''.join(f">{r['id']}\n{r['sequence']}\n" for r in pool))
        mm='/n/holylabs/bsabatini_lab/Users/bsabatini/mmseqs/bin/mmseqs';hits=a.output/'hits.tsv'
        cmd=[mm,'easy-search',str(query),str(corpus),str(hits),str(a.output/'mmseq_tmp'),'-s','7.5','-e','1e-3','--max-seqs','10000','--threads',str(a.threads),'--format-output','query,target,fident,qcov,tcov','-v','1']
        report['search_command']=cmd;save();subprocess.run(cmd,check=True)
        bad=set()
        for line in hits.read_text().splitlines():
            q,t,identity,qcov,tcov=line.split()
            if float(identity)>=.3 and max(float(qcov),float(tcov))>=.5:bad.add(q)
        clean=[r for r in pool if r['id'] not in bad]
        # Cluster held-out candidates by the same operational family threshold.
        selfhits=a.output/'self_hits.tsv'
        cmd[3]=str(query);cmd[4]=str(selfhits);cmd[5]=str(a.output/'mmseq_self_tmp');subprocess.run(cmd,check=True)
        parent={r['id']:r['id'] for r in clean}
        def root(x):
            while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
            return x
        for line in selfhits.read_text().splitlines():
            q,t,identity,qcov,tcov=line.split()
            if q in parent and t in parent and float(identity)>=.3 and max(float(qcov),float(tcov))>=.5:parent[root(q)]=root(t)
        chosen=[];clusters=set();counts={True:0,False:0}
        for r in clean:
            cluster=root(r['id']);short=len(r['sequence'])<=256
            if cluster in clusters or counts[short]>=32:continue
            r['sequence_cluster']=cluster;chosen.append(r);clusters.add(cluster);counts[short]+=1
        report.update(screened_candidates=len(pool),homology_exclusions=len(bad),selected_count=len(chosen),stratum_counts={str(k):v for k,v in counts.items()})
        if len(chosen)<32:raise ValueError(f'only {len(chosen)} independent candidates; holdout not locked')
        lock=dict(protocol='full polymer input, fixed observed CA correspondence; no test scores used in selection',
                  pretraining_overlap='unknown for frozen ESMC and ProteinAE; no independence claim',
                  homology='MMseqs2 sensitivity 7.5; reject identity >=30% at coverage >=50% either direction; heuristic search',
                  targets=chosen,exclusion_corpus_sha256=report['exclusion_corpus_sha256'])
        locked=a.output/'locked_test.json';locked.write_text(json.dumps(lock,indent=2)+'\n')
        report.update(status='complete',locked_manifest=str(locked),locked_sha256=digest(locked))
    except BaseException as error:report.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:report['elapsed_seconds']=time.time()-report['started'];save()

if __name__=='__main__':main()
