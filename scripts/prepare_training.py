"""Build a small fixed, fully residue-mapped training pilot from cached inputs.

No encoder or ESM work. All source data are read only. Choose by sequence-ID
hash before losses/scores, then verify exact sequence and rigid CA agreement
against source AFDB PDBs. Preserve original confidence, without filtering on it.
"""
import argparse,hashlib,json,time,urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import h5py,numpy as np
from latentfold.metrics import ca_metrics
from prepare_holdout import AA,fasta


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True);p.add_argument('--per-bucket',type=int,default=256)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);data=a.source/'data/phase1_dataset';started=time.time()
 report=dict(status='running',records=[],rejections=[],selection='SHA256(pilot-v1:id); fixed length strata; training split only',per_bucket=a.per_bucket)
 def save():(a.output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
 source_files={};buckets={128:[],256:[],384:[],512:[]}
 try:
  short={name[2:]:seq for name,seq in fasta(data/'train_seqs.fasta') if name.startswith('k_')}
  long=dict(fasta(data/'afdb_long_seqs.fasta'))
  candidates=sorted({**short,**long}.items(),key=lambda r:hashlib.sha256(('pilot-v1:'+r[0]).encode()).digest())
  for filename in ['dataset_100k_esmc.h5']+[f'dataset_afdb_long_{i}_esmc.h5' for i in range(4)]:
   path=data/filename
   if path.exists():source_files[filename]=h5py.File(path,'r')
  if 'dataset_100k_esmc.h5' not in source_files:raise ValueError('short ESMC cache missing')
  # Membership checks for only the chosen pool avoid scanning all embedding metadata.
  for name,seq in candidates:
   n=len(seq)
   if not 32<=n<=512:continue
   bucket=next(k for k in buckets if n<=k)
   if len(buckets[bucket])>=a.per_bucket:continue
   options=['dataset_100k_esmc.h5'] if name in short else [k for k in source_files if 'long' in k]
   sources=[k for k in options if name in source_files[k]['train']]
   if len(sources)!=1:continue
   buckets[bucket].append(dict(id=name,sequence=seq,file=sources[0],bucket=bucket))
   if all(len(v)==a.per_bucket for v in buckets.values()):break
  if any(len(v)!=a.per_bucket for v in buckets.values()):raise ValueError('insufficient uniquely mapped cached training records')
  chosen=[r for v in buckets.values() for r in v];raw=a.output/'source_pdb';raw.mkdir()
  report['selected_ids_sha256']=hashlib.sha256('\n'.join(r['id'] for r in chosen).encode()).hexdigest();save()
  def fetch(meta):
   name=meta['id'];path=raw/f'{name}.pdb'
   if not path.exists():
    for attempt in range(3):
     try:
      with urllib.request.urlopen(f'https://alphafold.ebi.ac.uk/files/{name}.pdb',timeout=30) as response:contents=response.read()
      path.write_bytes(contents);break
     except Exception:
      if attempt==2:raise
      time.sleep(1)
   rows=[];seen=set()
   for line in path.read_text().splitlines():
    if line.startswith('ENDMDL'):break
    if line.startswith('ATOM') and line[12:16].strip()=='CA':
     key=(line[21],int(line[22:26]),line[26])
     if key in seen:continue
     seen.add(key);rows.append((key,AA.get(line[17:20],'X'),[float(line[30:38]),float(line[38:46]),float(line[46:54])],float(line[60:66])))
   if ''.join(r[1] for r in rows)!=meta['sequence']:raise ValueError(f'{name}: source sequence mismatch')
   return meta,rows,hashlib.sha256(path.read_bytes()).hexdigest()
  with h5py.File(a.output/'pilot.h5','w') as output,ThreadPoolExecutor(max_workers=2) as workers:
   group=output.create_group('train')
   for meta,rows,sha in workers.map(fetch,chosen):
    name=meta['id'];source=source_files[meta['file']]['train'][name];seq=str(source.attrs['sequence'])
    if seq!=meta['sequence']:raise ValueError('cache FASTA sequence mismatch')
    z,ca,esm=[source[k][:] for k in ('z','ca_coords','esm2_emb')]
    n=len(seq)
    if z.shape!=(n,8) or ca.shape!=(n,3) or esm.shape!=(n,2560):raise ValueError('invalid cache shapes')
    if not all(np.isfinite(v).all() for v in (z,ca,esm)):raise ValueError('nonfinite cache')
    rmsd=ca_metrics(np.asarray([r[2] for r in rows]),ca)['ca_rmsd']
    if rmsd>.02:raise ValueError(f'{name}: source coordinates disagree by {rmsd} A')
    maps=[r[0] for r in rows]
    adjacent=[x[0]==y[0] and x[1]+1==y[1] and x[2]==y[2]==' ' for x,y in zip(maps,maps[1:])]
    g=group.create_group(name)
    for k,v in [('z',z),('ca_coords',ca),('esm2_emb',esm.astype(np.float16)),('adjacent',np.array(adjacent,dtype=bool)),('plddt',np.array([r[3] for r in rows],dtype=np.float32))]:g.create_dataset(k,data=v)
    g.attrs.update(sequence=seq,source_file=str(data/meta['file']),source_split='train',source_sha256=sha)
    report['records'].append(dict(id=name,length=n,bucket=meta['bucket'],source_file=str(data/meta['file']),
       sequence_sha256=hashlib.sha256(seq.encode()).hexdigest(),source_pdb_sha256=sha,residue_map=maps,
       source_ca_rmsd=rmsd,mean_plddt=float(np.mean([r[3] for r in rows]))))
    if len(report['records'])%16==0:
     output.flush();save();print('verified training records',len(report['records']),flush=True)
  report.update(status='complete',count=len(report['records']),dataset=str(a.output/'pilot.h5'))
 except BaseException as error:report.update(status='failed',error=f'{type(error).__name__}: {error}');raise
 finally:
  for f in source_files.values():f.close()
  report['elapsed_seconds']=time.time()-started;save()

if __name__=='__main__':main()
