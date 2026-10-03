"""Measured scaffold designability with graded motif error, not relaxed success."""
import math


def motif_quality(record, sequence_indices):
    """Best motif quality in one valid global-and-scaffold refold.

    Zero means no measured qualifying refold (or invalid raw geometry). Positive
    quality is 1 / max(1, four motif errors in Angstrom). Thus .5 permits 2A
    error for preference calibration only; strict success still requires 1A.
    Never assemble global, scaffold and motif scores from different sequences.
    """
    raw = record['raw']
    folds = record['refolds']
    if len(folds) != 8 or [r['sequence_index'] for r in folds] != list(range(8)):
        raise ValueError('Exactly eight ordered refolds required')
    if not set(sequence_indices) <= set(range(8)) or not sequence_indices:
        raise ValueError('Invalid design split')
    for row in [raw, *folds]:
        if type(row['coarse_valid']) is not bool:
            raise ValueError('Geometry validity must be explicit')
        for key in ('motif_ca_rmsd', 'motif_drms'):
            if not math.isfinite(row[key]) or row[key] < 0:
                raise ValueError('Invalid motif error')
    for row in folds:
        for key in ('sc_tm', 'scaffold_tm'):
            if not math.isfinite(row[key]) or not 0 <= row[key] <= 1.000001:
                raise ValueError('Invalid structural agreement')
    if not raw['coarse_valid']:
        return 0.
    candidates = [1. / max(1., raw['motif_ca_rmsd'], raw['motif_drms'],
                           r['motif_ca_rmsd'], r['motif_drms'])
                  for r in folds if r['sequence_index'] in sequence_indices
                  and r['coarse_valid'] and r['sc_tm'] > .5 and r['scaffold_tm'] > .5]
    return max(candidates, default=0.)


def split_preference(records, *, minimum_quality=.5, discovery_margin=.15,
                     confirmation_margin=.1):
    """Select with designs0..3; verify the SAME ordered pair using4..7."""
    if len(records) < 2 or len({r['slot'] for r in records}) != len(records):
        raise ValueError('Distinct generation candidates required')
    if len({r['target_id'] for r in records}) != 1:
        raise ValueError('Preferences must share their supplied fragment')
    rows = sorted(records, key=lambda r: r['slot'])
    scores = {r['slot']: [motif_quality(r, range(4)), motif_quality(r, range(4, 8)),
                         motif_quality(r, range(8))] for r in rows}
    winner = min(scores, key=lambda k: (-scores[k][0], k))
    loser = min(scores, key=lambda k: (scores[k][0], k))
    discovery = scores[winner][0] - scores[loser][0]
    confirmation = scores[winner][1] - scores[loser][1]
    eligible = (winner != loser and scores[winner][0] >= minimum_quality
                and discovery >= discovery_margin)
    confirmed = eligible and scores[winner][1] >= minimum_quality and confirmation >= confirmation_margin
    return dict(target_id=rows[0]['target_id'], scores=scores, winner=winner, loser=loser,
                discovery_margin=discovery, confirmation_margin=confirmation,
                eligible=eligible, confirmed=confirmed)
