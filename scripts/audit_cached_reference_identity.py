"""Verify inherited reference arrays and exact preservation in aligned labels."""
import argparse,hashlib,json
from pathlib import Path
import h5py


def main():
    p=argparse.ArgumentParser();p.add_argument('--selection',type=Path,required=True);p.add_argument('--shards',type=Path,nargs=4,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    raw=a.selection.read_bytes();selection=json.loads(raw);expected={r['id']:r for r in selection['train']};seen=set();files={}
    with h5py.File(selection['dataset']) as inherited:
        for run in a.shards:
            path=run/'labels.h5'
            with path.open('rb') as f:files[str(path.resolve())]=hashlib.file_digest(f,'sha256').hexdigest()
            with h5py.File(path) as labels:
                for ident in labels:
                    if ident not in expected or ident in seen:raise ValueError('unexpected or duplicate reference')
                    seen.add(ident);record=expected[ident];original=inherited['train'][ident]
                    for key in ('z','ca_coords'):
                        if hashlib.sha256(original[key][:].tobytes()).hexdigest()!=record['array_sha256'][key]:raise ValueError('inherited array changed')
                    reference=labels[ident]['reference_z'][:];cached=original['z'][:]
                    if reference.dtype!=cached.dtype or reference.shape!=cached.shape or reference.tobytes()!=cached.tobytes():raise ValueError('reference labels not bitwise identical')
    if seen!=set(expected) or len(seen)!=512:raise ValueError('incomplete reference coverage')
    result=dict(status='complete',targets=512,cached_reference_labels_bitwise_equal=True,source_cached_z_and_ca_match_frozen_array_hashes=True,selection_sha256=hashlib.sha256(raw).hexdigest(),label_files=files)
    a.output.write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
