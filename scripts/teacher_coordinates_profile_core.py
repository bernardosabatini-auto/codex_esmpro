"""Immutable inputs and coordinate parity for the unused-confidence profile."""
import hashlib
import json
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def selection(manifest):
    result = []
    for bucket in (128, 256, 384, 512):
        entry = next(r for r in manifest['config']['entries'] if r['bucket'] == bucket)
        for index in (0, 1):
            old = next(r for r in manifest['records'] if r['name'] == entry['name'] and r['sequence_index'] == index)
            result.append(dict(name=entry['name'], sequence_index=index, bucket=bucket,
                               length=entry['length'], seed=old['seed'],
                               sequence=manifest['sequences'][entry['name']][index]))
    return result


def audit(config):
    for key in ('protocol', 'parent_manifest', 'parent_refolded'):
        if sha(config[key]) != config[key + '_sha256']:
            raise ValueError('Changed ' + key)
    parent = json.loads(Path(config['parent_manifest']).read_text())
    if parent['status'] != 'complete' or parent.get('teacher_deterministic_algorithms') is not True:
        raise ValueError('Archived deterministic refolds required')
    if config['entries'] != selection(parent):
        raise ValueError('Changed prospective sequence selection')
    if config['teacher_artifacts'] != parent['config']['teacher_artifacts']:
        raise ValueError('Changed teacher artifacts')
    for dep in config['teacher_artifacts'] + config['external_sources']:
        if sha(dep['path']) != dep['sha256']:
            raise ValueError('Changed dependency ' + dep['path'])
    protocol = json.loads(Path(config['protocol']).read_text())
    if protocol['repeats_including_warmup'] != 4 or protocol['precision'] != 'fp32':
        raise ValueError('Wrong profiling protocol')
    return protocol
