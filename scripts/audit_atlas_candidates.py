"""Data-only ATLAS eligibility and homology audit; does not select or score models."""
import argparse
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path('.'))
    p.add_argument('--mmseqs', type=Path, required=True)
    a = p.parse_args()
    root = a.root.resolve()
    source = root / 'runs/ensemble_sources/atlas'
    out = source / 'family_audit'
    out.mkdir(exist_ok=False)
    manifest = dict(status='running', started=datetime.now(timezone.utc).isoformat(),
                    eligibility='standard 20 AA; length 64..512; metadata no_contact=True; exact metadata length',
                    homology='identity >=0.30 and coverage >=0.50 of either sequence; MMseqs e<=1e-3, sensitivity 7.5',
                    scope='Metadata audit only. No model scoring or confirmation panel selection.', sources={})

    def save():
        temporary = out / 'manifest.tmp'
        temporary.write_text(json.dumps(manifest, indent=2) + '\n')
        temporary.replace(out / 'manifest.json')

    save()
    try:
        rows = list(csv.DictReader((source / 'metadata.tsv').open(), delimiter='\t'))
        if len({r['PDB'] for r in rows}) != len(rows):
            raise ValueError('duplicate ATLAS IDs')
        eligible = [r for r in rows if r['no_contact'] == 'True' and
                    64 <= len(r['sequence']) <= 512 and
                    len(r['sequence']) == int(r['length']) and
                    set(r['sequence']) <= set('ACDEFGHIKLMNPQRSTVWY')]
        query = out / 'candidates.fasta'
        query.write_text(''.join(f">{r['PDB']}\n{r['sequence']}\n" for r in eligible))
        current = out / 'current_exclusion.fasta'
        paths = [root / 'runs/layer_probe/frozen.json',
                 root / 'runs/ensemble_sources/candidate_catalog_v2.json',
                 root / 'runs/holdout_expanded_20260930/locked_test.json']
        sequences = []
        for path in paths:
            data = json.loads(path.read_text())
            for split in ('train', 'tuning', 'confirmation', 'targets'):
                for r in data.get(split, []):
                    sequences.append(r['sequence'])
        current.write_text(''.join(f'>excluded_{i}\n{s}\n' for i, s in enumerate(sorted(set(sequences)))))
        inherited = root / 'runs/holdout_local_20260930/exclude.fasta'
        for path in [source / 'metadata.tsv', source / 'parsable.zip', *paths, inherited]:
            manifest['sources'][str(path.relative_to(root))] = sha(path)
        manifest.update(metadata_rows=len(rows), eligible_rows=len(eligible), searches={})
        save()
        hits = {}
        for name, database in [('current', current), ('inherited', inherited), ('self', query)]:
            result = out / f'{name}.tsv'
            command = [str(a.mmseqs), 'easy-search', str(query), str(database), str(result),
                       str(out / f'tmp_{name}'), '-s', '7.5', '-e', '1e-3', '--max-seqs', '10000',
                       '--threads', '2', '--split-memory-limit', '4G',
                       '--format-output', 'query,target,fident,qcov,tcov', '-v', '1']
            with (out / f'{name}.log').open('w') as log:
                subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT, timeout=1200)
            passing = []
            for line in result.read_text().splitlines():
                q, t, identity, qcov, tcov = line.split('\t')
                if float(identity) >= .30 and max(float(qcov), float(tcov)) >= .50:
                    passing.append((q, t))
            hits[name] = passing
            manifest['searches'][name] = dict(command=command, sha256=sha(result), passing_pairs=len(passing))
            save()
        overlap = {name: {q for q, t in pairs} for name, pairs in hits.items()}
        parents = {r['PDB']: r['PDB'] for r in eligible}

        def find(x):
            while parents[x] != x:
                parents[x] = parents[parents[x]]
                x = parents[x]
            return x

        for q, t in hits['self']:
            x, y = find(q), find(t)
            parents[max(x, y)] = min(x, y)
        candidates = [dict(id=r['PDB'], sequence=r['sequence'], length=len(r['sequence']),
                           family=find(r['PDB']), current_overlap=r['PDB'] in overlap['current'],
                           inherited_overlap=r['PDB'] in overlap['inherited']) for r in eligible]
        excluded_current = {r['family'] for r in candidates if r['current_overlap']}
        excluded_inherited = {r['family'] for r in candidates if r['inherited_overlap']}
        available = [r for r in candidates if r['family'] not in excluded_current]
        unseen = [r for r in available if r['family'] not in excluded_inherited]
        manifest.update(status='complete', candidates=candidates,
                        current_disjoint_families=len({r['family'] for r in available}),
                        inherited_and_current_disjoint_families=len({r['family'] for r in unseen}),
                        finished=datetime.now(timezone.utc).isoformat())
        save()
        print(json.dumps({k: v for k, v in manifest.items() if k not in ('candidates', 'sources', 'searches')}, indent=2))
    except Exception as error:
        manifest.update(status='failed', error=repr(error))
        save()
        raise


if __name__ == '__main__':
    main()
