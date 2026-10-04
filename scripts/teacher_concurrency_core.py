import json
from pathlib import Path
from teacher_coordinates_profile_core import audit as audit_original, sha


def file_stats(original):
    result=[]
    for dep in original['teacher_artifacts']+original['external_sources']:
        stat=Path(dep['path']).stat()
        result.append(dict(path=dep['path'],size=stat.st_size,mtime_ns=stat.st_mtime_ns,inode=stat.st_ino))
    return result


def audit(c, *, verify_weights=True):
    for key in ('protocol', 'reference_manifest', 'reference_report', 'reference_coordinates'):
        if sha(c[key]) != c[key+'_sha256']: raise ValueError('Changed concurrency source: '+key)
    p=json.loads(Path(c['protocol']).read_text())
    m=json.loads(Path(c['reference_manifest']).read_text()); d=json.loads(Path(c['reference_report']).read_text())
    if (Path(c['reference_manifest']).parent.name != p['reference_run'] or m['status']!='complete'
            or d['status']!='complete' or not d['numerical_parity'] or d['manifest_sha256']!=sha(c['reference_manifest'])
            or d['coordinates_sha256']!=sha(c['reference_coordinates']) or c['original']!=m['config']
            or p['memory_fraction_per_worker']!=.4 or p['repeats_including_warmup']!=4):
        raise ValueError('Unqualified immutable concurrency reference')
    if verify_weights:
        audit_original(c['original'])
    elif c.get('cpu_verified_file_stats') != file_stats(c['original']):
        raise ValueError('Dependencies changed since CPU content verification')
    return p
