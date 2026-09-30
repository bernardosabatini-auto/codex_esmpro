"""Select recent experimental targets without model scores, using audited exclusions."""
import argparse,hashlib,json,subprocess,time,urllib.request,urllib.parse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from prepare_holdout import AA,digest,parse_cif


def get_json(url,payload=None):
    data=None if payload is None else json.dumps(payload).encode()
    request=urllib.request.Request(url,data=data,headers={'Content-Type':'application/json','User-Agent':'ESM-ProteinAE-research/1.0'})
    with urllib.request.urlopen(request,timeout=60) as response:return json.load(response)


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--exclude-run',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True);p.add_argument('--since',default='2026-09-01');a=p.parse_args()
 a.output.mkdir(parents=True,exist_ok=False);base=json.loads((a.exclude_run/'holdout.json').read_text());corpus=a.exclude_run/'exclude.fasta'
 if digest(corpus)!=base['exclusion_corpus_sha256'] or len(base['coverage'])!=12:raise ValueError('exclusion audit incomplete or corpus changed')
 report=dict(status='running',started=time.time(),coverage=base['coverage'],corpora=base['corpora'],
             exclusion_corpus_sha256=base['exclusion_corpus_sha256'],candidates=[],rejections=[],source='Recent PDB releases; full polymer sequences; no model scores')
 def save():
  path=a.output/'holdout.json';tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(path)
 try:
  nodes=[dict(type='terminal',service='text',parameters=dict(attribute=attr,operator=op,value=val)) for attr,op,val in
    [('rcsb_accession_info.initial_release_date','greater_or_equal',a.since),('rcsb_accession_info.initial_release_date','less_or_equal','2026-09-30'),('rcsb_entry_info.resolution_combined','less_or_equal',3.),('entity_poly.rcsb_entity_polymer_type','exact_match','Protein')]]
  query=dict(query=dict(type='group',logical_operator='and',nodes=nodes),return_type='polymer_entity',request_options=dict(return_all_hits=True))
  report['search_query']=query;save()
  response=get_json('https://search.rcsb.org/rcsbsearch/v2/query?json='+urllib.parse.quote(json.dumps(query)))
  (a.output/'search_response.json').write_text(json.dumps(response));ids=[r['identifier'] for r in response['result_set']]
  entities=[]
  for start in range(0,len(ids),150):
   q='query { polymer_entities(entity_ids: '+json.dumps(ids[start:start+150])+') { rcsb_id entity_poly { pdbx_seq_one_letter_code_can } rcsb_polymer_entity_container_identifiers { auth_asym_ids } entry { rcsb_entry_info { resolution_combined } exptl { method } rcsb_accession_info { initial_release_date } } } }'
   result=get_json('https://data.rcsb.org/graphql',{'query':q})
   if result.get('errors'):raise ValueError(result['errors'])
   if len(result['data']['polymer_entities'])!=len(ids[start:start+150]):raise ValueError('incomplete metadata response')
   entities+=result['data']['polymer_entities'];print('metadata',len(entities),'/',len(ids),flush=True)
  (a.output/'entity_metadata.json').write_text(json.dumps(entities));pool=[];seqseen=set()
  for item in sorted(entities,key=lambda r:hashlib.sha256(('recent-test-v1:'+r['rcsb_id']).encode()).digest()):
   sequence=''.join(item['entity_poly']['pdbx_seq_one_letter_code_can'].split())
   if not 50<=len(sequence)<=512 or any(x not in set(AA.values()) for x in sequence) or sequence in seqseen:continue
   seqseen.add(sequence);pid=item['rcsb_id'].split('_')[0].lower()
   chains=sorted(item['rcsb_polymer_entity_container_identifiers']['auth_asym_ids'])
   pool.append(dict(entity_id=item['rcsb_id'],id=f'{pid}_{chains[0]}',pdb_id=pid,chains=chains,sequence=sequence,
         resolution=min(item['entry']['rcsb_entry_info']['resolution_combined']),method=item['entry']['exptl'][0]['method'],
         initial_release_date=item['entry']['rcsb_accession_info']['initial_release_date']))
  report['candidates']=[dict(id=r['id'],length=len(r['sequence'])) for r in pool];save()
  if not pool:raise ValueError('no eligible recent sequences')
  query_file=a.output/'candidates.fasta';query_file.write_text(''.join(f">{r['id']}\n{r['sequence']}\n" for r in pool))
  mm='/n/holylabs/bsabatini_lab/Users/bsabatini/mmseqs/bin/mmseqs';hits=a.output/'hits.tsv'
  def search(target,path,temp):
   command=[mm,'easy-search',str(query_file),str(target),str(path),str(a.output/temp),'-s','7.5','-e','1e-3','--max-seqs','10000','--threads','1','--split-memory-limit','4G','--format-output','query,target,fident,qcov,tcov','-v','1']
   print('search',target,flush=True);subprocess.run(command,check=True);return command
  report['search_command']=search(corpus,hits,'mmseq_tmp');bad=set()
  for line in hits.read_text().splitlines():
   q,t,identity,qcov,tcov=line.split()
   if float(identity)>=.3 and max(float(qcov),float(tcov))>=.5:bad.add(q)
  clean=[r for r in pool if r['id'] not in bad]
  report.update(screened_candidates=len(pool),homology_exclusions=len(bad),clean_sequences=len(clean));save();print('clean sequences',len(clean),flush=True)
  selfhits=a.output/'self_hits.tsv';search(query_file,selfhits,'self_tmp');parent={r['id']:r['id'] for r in clean}
  def root(x):
   while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
   return x
  for line in selfhits.read_text().splitlines():
   q,t,identity,qcov,tcov=line.split()
   if q in parent and t in parent and float(identity)>=.3 and max(float(qcov),float(tcov))>=.5:parent[root(q)]=root(t)
  chosen=[];clusters=set();counts={True:0,False:0};raw=a.output/'mmcif';raw.mkdir()
  for item in clean:
   cluster=root(item['id']);short=len(item['sequence'])<=256
   if cluster in clusters or counts[short]>=32:continue
   path=raw/f"{item['pdb_id']}.cif"
   try:
    if not path.exists():
     with urllib.request.urlopen(f"https://files.rcsb.org/download/{item['pdb_id'].upper()}.cif",timeout=45) as response:contents=response.read(64*1024**2+1)
     if len(contents)>64*1024**2:raise ValueError('mmCIF exceeds bounded 64 MiB parser input')
     path.write_bytes(contents)
    parsed=None;errors=[]
    for chain in item['chains']:
     try:parsed=parse_cif(path,chain,item['sequence']);selected_chain=chain;break
     except ValueError as error:errors.append(str(error))
    if parsed is None:raise ValueError('; '.join(sorted(set(errors))))
    chosen.append(dict(**{k:v for k,v in item.items() if k not in ('sequence','id')},id=f"{item['pdb_id']}_{selected_chain}",
          source_url=f"https://files.rcsb.org/download/{item['pdb_id'].upper()}.cif",source_sha256=digest(path),sequence_cluster=cluster,**parsed))
    clusters.add(cluster);counts[short]+=1;print('verified test candidates',len(chosen),counts,flush=True)
   except Exception as error:report['rejections'].append(dict(id=item['id'],rejection=f'{type(error).__name__}: {error}'))
   report['selected_count']=len(chosen);save()
   if len(chosen)==64:break
  report['stratum_counts']={str(k):v for k,v in counts.items()}
  if len(chosen)<32:raise ValueError(f'only {len(chosen)} independent, mapped recent structures; holdout not locked')
  locked=dict(protocol='full polymer input; explicit observed CA maps; no model scores used in selection',
    pretraining_overlap='unknown for frozen ESMC and ProteinAE; no independence claim',
    homology='MMseqs2 sensitivity 7.5; exclude >=30% identity at >=50% coverage either direction; heuristic search',
    targets=chosen,exclusion_corpus_sha256=report['exclusion_corpus_sha256'],search_query=query)
  path=a.output/'locked_test.json';path.write_text(json.dumps(locked,indent=2)+'\n')
  report.update(status='complete',locked_manifest=str(path),locked_sha256=digest(path))
 except BaseException as error:report.update(status='failed',error=f'{type(error).__name__}: {error}');raise
 finally:report['elapsed_seconds']=time.time()-report['started'];save()

if __name__=='__main__':main()
