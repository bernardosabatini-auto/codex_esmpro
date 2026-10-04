"""Joint connected success must exist in a single refold, with raw quality explicit."""
import math


def connected_outcome(raw,refolds,*,physical_raw):
    if len(refolds)!=8 or {r['sequence_index'] for r in refolds}!=set(range(8)):
        raise ValueError('All eight distinct sequence attempts required')
    connected=[];strict=[]
    for r in refolds:
        for k in ('sc_tm','scaffold_tm','motif_drms','motif_ca_rmsd'):
            if not math.isfinite(r[k]) or r[k]<0:raise ValueError('Invalid score')
        if r['sc_tm']>1 or r['scaffold_tm']>1:raise ValueError('Invalid TM score')
        if r['coarse_valid'] and r['sc_tm']>.5 and r['scaffold_tm']>.5 and r['flank_edges_valid']:
            connected.append(r['sequence_index'])
            if r['motif_drms']<=1 and r['motif_ca_rmsd']<=1:strict.append(r['sequence_index'])
    raw_ok=bool(raw['coarse_valid'] and raw['motif_drms']<=1 and raw['motif_ca_rmsd']<=1)
    return dict(physical_raw=bool(physical_raw),connected_refold_indices=connected,
        connected_designable=bool(raw['coarse_valid'] and connected),
        complete_connected_designable=bool(physical_raw and raw['coarse_valid'] and connected),
        complete_strict_indices=strict if physical_raw and raw_ok else [],
        complete_strict=bool(physical_raw and raw_ok and strict))
