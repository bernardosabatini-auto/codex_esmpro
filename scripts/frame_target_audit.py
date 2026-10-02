"""Independently rebuild every selected supervision tensor from frozen labels."""
import hashlib,json
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha


def qualify_frame_data(c):
    """Keep the original gate; a revised route needs its own audited evidence."""
    for key in ('target_frame_protocol','frame_data_report','frame_data_manifest'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed target-frame source')
    d=json.loads(Path(c['frame_data_report']).read_text())
    if d['status']!='complete' or d['manifest_sha256']!=c['frame_data_manifest_sha256'] or d['fragments_sha256']!=c['fragments_sha256']:raise ValueError('Invalid target frame data')
    if d['training_gate_passed']:return 'original_absolute_gate'
    for key in ('frame_confirmation_report','frame_confirmation_manifest','frame_confirmation_protocol'):
        if key not in c or sha(c[key])!=c[key+'_sha256']:raise ValueError('Failed original gate requires unchanged confirmation evidence')
    report=json.loads(Path(c['frame_confirmation_report']).read_text());manifest=json.loads(Path(c['frame_confirmation_manifest']).read_text())
    if report['status']!='complete' or manifest['status']!='complete' or not report['relative_label_gate_passed'] or report['original_absolute_gate_passed'] or report['manifest_sha256']!=c['frame_confirmation_manifest_sha256']:raise ValueError('Failed relative confirmation gate')
    if report['data_manifest_sha256']!=c['frame_data_manifest_sha256'] or report['fragments_sha256']!=c['fragments_sha256'] or manifest['config']['data_manifest_sha256']!=c['frame_data_manifest_sha256'] or manifest['config']['data_report_sha256']!=c['frame_data_report_sha256'] or manifest['config']['protocol_sha256']!=c['frame_confirmation_protocol_sha256']:raise ValueError('Confirmation belongs to different data/protocol')
    return 'revised_fresh_noise_relative_gate'


def audit_frame_targets(m):
    c=m['config']
    qualify_frame_data(c)
    rows=m['frame_target_updates']
    if len(rows)!=m['updates'] or [r['step'] for r in rows]!=list(range(1,m['updates']+1)):raise ValueError('Missing frame target traces')
    with h5py.File(c['fragments']) as f:data={i:dict(original=g['reference_z'][:],targets={name:q['target_latent'][:] for name,q in g['conditions'].items()}) for i,g in f['train'].items()}
    digest=lambda x:hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()
    for row,trace in zip(rows,m['training']):
        b,n=trace['batch'],trace['length'];conditioned=np.zeros((b,n,8),dtype=np.float32);original=np.zeros_like(conditioned);dropped=np.asarray(row['dropped_slots'],dtype=bool)
        if dropped.shape!=(b,) or digest(dropped)!=trace['drop_sha256']:raise ValueError('Dropout mask mismatch')
        for j,(ident,name) in enumerate(zip(trace['ids'],trace['conditions'])):
            item=data[ident];length=len(item['original']);original[j,:length]=item['original'];conditioned[j,:length]=item['targets'][name]
        selected=np.where(dropped[:,None,None],original,conditioned)
        for key,array in [('conditioned_target_sha256',conditioned),('null_target_sha256',original),('selected_target_sha256',selected)]:
            if row[key]!=digest(array):raise ValueError('Frame supervision tensor mismatch')
