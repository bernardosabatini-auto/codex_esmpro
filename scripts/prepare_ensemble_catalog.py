"""Give distinct experimental constructs unique IDs before sequence screening."""
import argparse,csv,hashlib,json
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument('--assets',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    source=json.loads((a.assets/'download_manifest.json').read_text());rows=[];seen=set()
    for path in sorted((a.assets/'bioemu_benchmarks/assets').rglob('testcases.csv')):
        for row in csv.DictReader(path.open()):
            seq=row['sequence'];sha=hashlib.sha256(seq.encode()).hexdigest();category=path.parent.name
            ident=category+'__'+row['test_case']+'__'+sha[:12]
            if ident in seen:continue
            seen.add(ident)
            refs=sorted((path.parent/'reference'/row['test_case']).glob('*.pdb'))
            rows.append(dict(query_id=ident,category=category,id=row['test_case'],sequence=seq,length=len(seq),sequence_sha256=sha,references=[str(p.resolve()) for p in refs],metadata=str(path.resolve()),within_length_limit=32<=len(seq)<=512))
    result=dict(status='unselected_candidates',source_commit=source['commit'],targets=rows,notes='Biological case IDs can have multiple constructs. Query IDs include the sequence hash. Related constructs must be clustered and must not count as independent evaluation proteins.')
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    fasta=a.output.with_suffix('.fasta');fasta.write_text(''.join('>'+r['query_id']+'\n'+r['sequence']+'\n' for r in rows if r['within_length_limit']))
    print(json.dumps(dict(constructs=len(rows),within_length_limit=sum(r['within_length_limit'] for r in rows),fasta=str(fasta))))


if __name__=='__main__':main()
