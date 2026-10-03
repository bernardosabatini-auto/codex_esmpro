"""Sequence-isolated, explicitly mapped additional experimental fragment sources."""
import argparse,hashlib,json,subprocess,time,urllib.request
from pathlib import Path
import h5py,numpy as np
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from prepare_holdout import AA
from prepare_overfit import sha
from audit_training_expansion import components
from audit_fragment_teacher_targets import proper_rmsd_batch
from latentfold.ensemble_metrics import backbone_geometry
from profile_gpu import atomic_json


def read_observed_backbone(path,chain,sequence):
    cif=MMCIF2Dict(str(path));prefix='_atom_site.'
    required=('auth_asym_id','label_seq_id','label_atom_id','label_comp_id','label_alt_id','Cartn_x','Cartn_y','Cartn_z','auth_seq_id','pdbx_PDB_ins_code','pdbx_PDB_model_num')
    cols={key:cif[prefix+key] for key in required};atoms={};mapping={};letters={}
    for i,ch in enumerate(cols['auth_asym_id']):
        if ch!=chain or cols['pdbx_PDB_model_num'][i]!='1' or cols['label_alt_id'][i] not in ('.','?','A','1'):continue
        label=cols['label_seq_id'][i];atom=cols['label_atom_id'][i]
        if label in ('.','?') or atom not in ('N','CA','C','O'):continue
        position=int(label);letter=AA.get(cols['label_comp_id'][i],'X');value=[float(cols[k][i]) for k in ('Cartn_x','Cartn_y','Cartn_z')]
        if position in letters and letters[position]!=letter:raise ValueError('Ambiguous residue identity')
        letters[position]=letter;at=atoms.setdefault(position,{})
        if atom in at and at[atom]!=value:raise ValueError('Ambiguous alternate backbone atom')
        at[atom]=value;mapping[position]=dict(label_seq_id=position,auth_seq_id=cols['auth_seq_id'][i],insertion=cols['pdbx_PDB_ins_code'][i],auth_chain=chain)
    observed=sorted(k for k,v in atoms.items() if all(a in v for a in ('N','CA','C','O')))
    if not observed or observed!=list(range(observed[0],observed[-1]+1)):raise ValueError('Internal observed-residue gap')
    if ''.join(letters[k] for k in observed)!=sequence:raise ValueError('Observed sequence differs from cached construct')
    bb=np.asarray([[atoms[k][a] for a in ('N','CA','C','O')] for k in observed],np.float32)
    if bb.shape!=(len(sequence),4,3) or not np.isfinite(bb).all():raise ValueError('Incomplete backbone')
    return bb,[mapping[k] for k in observed]


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/fragment_extra_development_protocol.json';spec=json.loads(protocol.read_text());source=Path(spec['source']);mm=Path('/n/holylabs/bsabatini_lab/Users/bsabatini/mmseqs/bin/mmseqs')
    paths=[root/'runs/fragment_data_49981806/manifest.json',root/'runs/ensemble_sources/candidate_catalog_v2.json',root/'runs/ensemble_sources/frozen_panel48.json',root/'runs/holdout_expanded_20260930/locked_test.json',root/'runs/layer_probe/frozen.json']
    exclusions=set()
    for path in paths:
        d=json.loads(path.read_text())
        if path==paths[0]:exclusions.update(r['sequence'] for r in d['config']['training_targets'])
        else:
            for split in ('targets','development','confirmation','tuning','train'):exclusions.update(r['sequence'] for r in d.get(split,[]))
    a.output.mkdir(parents=True,exist_ok=False);raw=a.output/'mmcif';raw.mkdir();m=dict(status='running',protocol=spec,sources={str(x):sha(x) for x in [protocol,source,mm,*paths,Path(__file__).resolve(),root/'src/latentfold/ensemble_metrics.py',root/'scripts/audit_training_expansion.py',root/'scripts/audit_fragment_teacher_targets.py']},exclusion_sequences=len(exclusions),metadata_rejections=[],structure_rejections=[],selected=[]);atomic_json(a.output/'manifest.json',m)
    try:
        rows={}
        with h5py.File(source) as f:
            if len(f['val'])!=626:raise ValueError('Changed original experimental inventory')
            for ident,g in f['val'].items():
                seq=str(g.attrs['sequence']);n=len(seq)
                if not 50<=n<=512 or g['backbone'].shape!=(n,3,3) or set(seq)-set('ACDEFGHIKLMNPQRSTVWY') or int(g.attrs['chain_breaks'])!=0:
                    m['metadata_rejections'].append(ident);continue
                pid,chain=ident.split('_',1)
                if len(pid)!=4 or not pid.isalnum():raise ValueError('Unsafe PDB identifier')
                rows[ident]=dict(target_id=ident,pdb_id=pid,chain=chain,sequence=seq,length=n,n_seqres=int(g.attrs['n_seqres']),resolution=float(g.attrs['resolution']),method=str(g.attrs['method']))
        query=a.output/'candidates.fasta';query.write_text(''.join(f'>{i}\n{r["sequence"]}\n' for i,r in sorted(rows.items())))
        exclude=a.output/'exclusion.fasta';exclude.write_text(''.join(f'>exclude_{k}\n{s}\n' for k,s in enumerate(sorted(exclusions))))
        m.update(candidate_sequences=len(rows),query_sha256=sha(query),exclusion_sha256=sha(exclude),commands=[]);atomic_json(a.output/'manifest.json',m)
        for label,target in [('self',query),('exclude',exclude)]:
            command=[str(mm),'easy-search',str(query),str(target),str(a.output/(label+'.tsv')),str(a.output/(label+'_tmp')),'-s','7.5','-e','1e-3','--max-seqs','10000','--threads','1','--split-memory-limit','4G','--format-output','query,target,fident,qcov,tcov','-v','1'];m['commands'].append(command)
            with (a.output/(label+'.log')).open('w') as log:subprocess.run(command,check=True,stdout=log,stderr=subprocess.STDOUT,timeout=900)
        families=components(rows,(a.output/'self.tsv').read_text());blocked=set()
        for line in (a.output/'exclude.tsv').read_text().splitlines():
            q,t,identity,qcov,tcov=line.split('\t')
            if q not in rows:raise ValueError('Unknown search query')
            if float(identity)>=.3 and max(float(qcov),float(tcov))>=.5:blocked.add(families[q])
        m.update(self_hits_sha256=sha(a.output/'self.tsv'),exclusion_hits_sha256=sha(a.output/'exclude.tsv'),blocked_families=sorted(blocked),family_count=len(set(families.values())));atomic_json(a.output/'manifest.json',m)
        ordered=sorted(rows,key=lambda i:hashlib.sha256((spec['selection_salt']+i).encode()).hexdigest());counts={False:0,True:0};used=set();tick=time.monotonic()
        with h5py.File(source) as original,h5py.File(a.output/'backbones.h5','x') as out:
            for ident in ordered:
                row=rows[ident];family=families[ident];long=row['length']>spec['length_boundary'];wanted=spec['long_families'] if long else spec['short_families']
                if family in blocked or family in used or counts[long]>=wanted:continue
                if time.monotonic()-tick>1200:raise TimeoutError('Structure verification time cap')
                path=raw/(row['pdb_id']+'.cif')
                try:
                    if not path.exists():
                        with urllib.request.urlopen('https://files.rcsb.org/download/'+row['pdb_id'].upper()+'.cif',timeout=45) as response:contents=response.read(64*1024**2+1)
                        if len(contents)>64*1024**2:raise ValueError('mmCIF exceeds64MiB')
                        path.write_bytes(contents)
                    bb,mapping=read_observed_backbone(path,row['chain'],row['sequence']);cached=original['val/'+ident+'/backbone'][:];rmsd=float(proper_rmsd_batch(bb[None,:,:3].reshape(1,-1,3),cached.reshape(-1,3))[0])
                    if rmsd>.02:raise ValueError('Mapped backbone differs from cached coordinates')
                    if not backbone_geometry(bb[None])['coarse_valid'][0]:raise ValueError('Source fails existing coarse-validity criterion')
                    g=out.create_group(ident);g.create_dataset('backbone',data=bb);g.attrs.update(sequence=row['sequence'],family=family,length=row['length']);m['selected'].append(dict(row,family=family,source_path=str(path.resolve()),source_sha256=sha(path),residue_map=mapping,source_ncac_rmsd=rmsd));used.add(family);counts[long]+=1
                    print('Verified new fragment family',sum(counts.values()),flush=True)
                except (ValueError,KeyError,OSError) as error:m['structure_rejections'].append(dict(target_id=ident,error=str(error)))
                out.flush();atomic_json(a.output/'manifest.json',m)
                if counts=={False:spec['short_families'],True:spec['long_families']}:break
        if counts!={False:spec['short_families'],True:spec['long_families']}:raise ValueError('Insufficient source-qualified disjoint families: '+str(counts))
        if any(sha(path)!=digest for path,digest in m['sources'].items()):raise ValueError('Source changed during selection')
        m.update(status='complete',backbones_sha256=sha(a.output/'backbones.h5'),scope=spec['evaluation'],counts={'short':counts[False],'long':counts[True]})
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
