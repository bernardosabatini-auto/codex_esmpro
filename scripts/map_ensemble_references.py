"""Map published backbone references to full benchmark sequences before selection."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
from Bio.Align import PairwiseAligner
from latentfold.metrics import ca_metrics
from prepare_holdout import AA


def parse_reference(path, sequence):
    residues={}
    for line in path.read_text().splitlines():
        if line.startswith('ENDMDL'):break
        if not line.startswith('ATOM') or line[16] not in (' ','A'):continue
        atom=line[12:16].strip()
        if atom not in ('N','CA','C','O'):continue
        key=(line[21],int(line[22:26]),line[26]);letter=AA.get(line[17:20].strip())
        if letter is None:raise ValueError('unsupported residue')
        entry=residues.setdefault(key,dict(letter=letter,atoms={}))
        if entry['letter']!=letter or atom in entry['atoms']:raise ValueError('ambiguous residue or backbone atom')
        entry['atoms'][atom]=[float(line[30:38]),float(line[38:46]),float(line[46:54])]
    keys=list(residues)
    if not keys or len({k[0] for k in keys})!=1:raise ValueError('expected one nonempty chain')
    observed=''.join(residues[k]['letter'] for k in keys)
    aligner=PairwiseAligner(mode='global',match_score=2,mismatch_score=-4,open_gap_score=-6,extend_gap_score=-.1)
    alignments=aligner.align(sequence,observed)
    def mapping(alignment):
        pairs=[]
        for a,b in zip(alignment.coordinates.T[:-1],alignment.coordinates.T[1:]):
            if b[0]>a[0] and b[1]>a[1]:
                if b[0]-a[0]!=b[1]-a[1]:raise ValueError('unexpected alignment segment')
                pairs.extend((int(i),int(j)) for i,j in zip(range(a[0],b[0]),range(a[1],b[1])))
        return pairs
    first=list(itertools.islice(alignments,2))
    pairs=mapping(first[0])
    if len(first)>1 and mapping(first[1])!=pairs:raise ValueError('ambiguous optimal sequence correspondence')
    mismatches=[(i,j) for i,j in pairs if sequence[i]!=observed[j]]
    complete=[(i,j) for i,j in pairs if sequence[i]==observed[j] and set(residues[keys[j]]['atoms'])=={'N','CA','C','O'}]
    if len(mismatches)>max(1,int(.02*len(sequence))):raise ValueError('construct sequence differs by more than two percent')
    if len(complete)<30 or len(complete)/len(sequence)<.9:raise ValueError('less than 90 percent complete mapped backbone')
    positions=[i for i,_ in complete]
    bb=np.asarray([[residues[keys[j]]['atoms'][atom] for atom in ('N','CA','C','O')] for _,j in complete])
    if not np.isfinite(bb).all():raise ValueError('nonfinite coordinates')
    return dict(path=str(path.resolve()),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),observed_indices=positions,
        residue_map=[list(keys[j]) for _,j in complete],backbone=bb.tolist(),mismatched_sequence_positions=[i for i,j in mismatches],
        observed_fraction=len(complete)/len(sequence),alignment_score=float(first[0].score))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--catalog',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    source=json.loads(a.catalog.read_text());result=dict(status='complete',source_commit=source['source_commit'],catalog_sha256=hashlib.sha256(a.catalog.read_bytes()).hexdigest(),mapped=[],rejected=[],md_candidates=[])
    for row in source['targets']:
        if not row['within_length_limit']:continue
        if row['category']=='md_emulation':result['md_candidates'].append(row);continue
        if len(row['references'])<2:continue
        try:
            refs=[parse_reference(Path(path),row['sequence']) for path in row['references']]
            common=sorted(set.intersection(*[set(r['observed_indices']) for r in refs]))
            if len(common)/len(row['sequence'])<.85:raise ValueError('less than 85 percent common reference coverage')
            arrays=[np.asarray(r['backbone'])[[r['observed_indices'].index(i) for i in common],1] for r in refs]
            distances=[dict(i=i,j=j,**ca_metrics(arrays[i],arrays[j])) for i in range(len(refs)) for j in range(i)]
            info=Path(row['metadata']).parent/'local_residinfo'/f"{row['id']}.json"
            features=json.loads(info.read_text()) if info.exists() else None
            result['mapped'].append(dict(**{k:v for k,v in row.items() if k!='references'},references=refs,common_indices=common,pairwise_reference_metrics=distances,published_local_residue_definitions=features))
        except Exception as error:result['rejected'].append(dict(id=row['id'],category=row['category'],reason=str(error)))
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(mapped=len(result['mapped']),rejected=len(result['rejected']),md_candidates=len(result['md_candidates']),low_global_dispersion_candidates=sum(max(d['ca_rmsd'] for d in r['pairwise_reference_metrics'])<.5 for r in result['mapped']))))


if __name__=='__main__':main()
