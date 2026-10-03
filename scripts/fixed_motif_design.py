"""Explicit fragment-only residue constraints for the CA ProteinMPNN interface."""
import json
from pathlib import Path


def fix_parsed_motifs(parsed,positions,entries):
    rows=[json.loads(line) for line in Path(parsed).read_text().splitlines() if line.strip()];byname={r['name']:r for r in entries};fixed={}
    if len(rows)!=len(entries) or {r['name'] for r in rows}!=set(byname):raise ValueError('Parsed structure coverage mismatch')
    for row in rows:
        entry=byname[row['name']];length=entry['length'];seq=row['seq_chain_A']
        if seq!='A'*length or row['seq']!=seq:raise ValueError('Unexpected input sequence, only motif residues may be supplied')
        start=entry.get('fixed_start',0);fragment=entry.get('fixed_sequence','')
        if start<0 or start+len(fragment)>length or set(fragment)-set('ACDEFGHIKLMNPQRSTVWY'):raise ValueError('Invalid fixed motif')
        if entry['head']=='experimental' and fragment:raise ValueError('Experimental controls must remain free design')
        seq=seq[:start]+fragment+seq[start+len(fragment):];row['seq_chain_A']=seq;row['seq']=seq;fixed[row['name']]={'A':list(range(start+1,start+len(fragment)+1))}
    Path(parsed).write_text(''.join(json.dumps(r)+'\n' for r in rows));Path(positions).write_text(json.dumps(fixed)+'\n')


def verify_fixed_sequences(sequences,entries):
    if set(sequences)!={r['name'] for r in entries}:raise ValueError('Sequence coverage mismatch')
    for r in entries:
        start=r.get('fixed_start',0);fragment=r.get('fixed_sequence','');ss=sequences[r['name']]
        if len(ss)!=8 or any(len(s)!=r['length'] or s[start:start+len(fragment)]!=fragment for s in ss):raise ValueError('Fixed motif sequence changed or incomplete designs')


def requires_fixed_motifs(entries):
    """Constraint presence comes from inputs, never an assay-name allowlist."""
    for row in entries:
        if ('fixed_start' in row)!=('fixed_sequence' in row):raise ValueError('Incomplete fixed motif declaration')
    return any(bool(row.get('fixed_sequence')) for row in entries)
