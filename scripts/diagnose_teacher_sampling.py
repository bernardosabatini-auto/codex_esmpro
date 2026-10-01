"""Calibrate recall variation from finite draws of empirical teacher labels."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--selection',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();raw=a.selection.read_bytes();rows=json.loads(raw)['targets']
    if len(rows)!=32 or len({r['id'] for r in rows})!=32:
        raise ValueError('expected the frozen 32-target panel')
    rng=np.random.default_rng(2026100171);recall=np.zeros(100000);expected=[]
    for r in rows:
        clusters=np.asarray(r['state_definition']['clusters'],dtype=int)
        prob=np.bincount(clusters)/len(clusters)
        if (prob<=0).any():raise ValueError('empty teacher state')
        counts=rng.multinomial(32,prob,size=len(recall))
        recall+=(counts>0).mean(1)/len(rows)
        expected.append(float(np.mean(1-(1-prob)**32)))
    d=dict(scope='Repeated direct empirical-teacher draws; no decoder; no biological population estimate',
           selection_sha256=hashlib.sha256(raw).hexdigest(),seed=2026100171,
           repetitions=len(recall),samples_per_target=32,targets=32,
           expected_recall=float(np.mean(expected)),monte_carlo_mean=float(recall.mean()),
           repeated_sampling_95_interval=np.quantile(recall,[.025,.975]).tolist(),
           standard_deviation=float(recall.std()))
    a.output.write_text(json.dumps(d,indent=2)+'\n')


if __name__=='__main__':main()
