"""End-to-end staged loading replay; preserve the original scientific budget."""
import argparse,copy,hashlib,json,os,tempfile,time
from pathlib import Path
import h5py,numpy as np
from context_flow_generation import audit_worker,identity
from prepare_overfit import sha


def validate(c,full=False):
    audit_worker(c)
    v=c['teacher_staging_validation'];spec=json.loads(Path(v['protocol']).read_text())
    pm=json.loads(Path(v['profile_manifest']).read_text());pd=json.loads(Path(v['profile_report']).read_text())
    rm=json.loads(Path(v['reference_manifest']).read_text());rd=json.loads(Path(v['reference_report']).read_text())
    if (c.get('teacher_checkpoint_staging') is not True or spec['reference_run']!=Path(v['reference_manifest']).parent.name
            or spec['profile_run']!=Path(v['profile_manifest']).parent.name or spec['backbones']!=32 or spec['sequences_per_backbone']!=8
            or spec['allocation_minutes']!=35 or c['allocation_minutes']!=35 or c['work_cap_seconds']!=2010
            or pm['status']!='complete' or pd['status']!='complete' or not pd.get('teacher_staging') or not pd['qualified'] or not pd['numerical_parity']
            or pd['manifest_sha256']!=sha(v['profile_manifest']) or rm['status']!='complete' or rd['status']!='complete'
            or rd['manifest_sha256']!=sha(v['reference_manifest']) or len(rm['records'])!=256):
        raise ValueError('Unqualified teacher loading replay')
    original=rm['config']
    for k,value in original.items():
        if k not in ('sources','file_identity','config_sha256') and c[k]!=value:raise ValueError('Changed original refolding configuration: '+k)
    if c['sources'][:len(original['sources'])]!=original['sources']:raise ValueError('Changed original source bindings')
    if full:
        for r in c['sources']:
            if sha(r['path'])!=r['sha256']:raise ValueError('Changed replay source')
        if rd['refolded_sha256']!=sha(v['reference_refolded']):raise ValueError('Changed historical reference coordinates')
    return rm,rd


def stage_for_validation(c):
    from teacher_staging import stage
    validate(c)
    local=tempfile.TemporaryDirectory(prefix='esm-proae-teacher-replay-',dir=os.environ.get('SLURM_TMPDIR') or '/tmp')
    try:
        start=time.monotonic();path=stage(c['teacher_artifacts'],Path(local.name)/'checkpoint')
        return local,path,time.monotonic()-start
    except BaseException:
        local.cleanup();raise


def audit_result(run,m,d):
    c=m['config'];rm,rd=validate(c,full=True)
    if m['sequences']!=rm['sequences'] or len(m['records'])!=256 or not m['cpu_preflight_file_identity_unchanged']:
        raise ValueError('Changed sequence attempts or incomplete replay')
    names={r['name'] for r in c['entries']};maximum=0.
    with h5py.File(run/'refolded.h5',locking=False) as new,h5py.File(c['teacher_staging_validation']['reference_refolded'],locking=False) as old:
        if set(new)!=names or set(old)!=names:raise ValueError('Changed backbone inventory')
        for name in sorted(names):
            if set(new[name])!={str(i) for i in range(8)} or set(old[name])!=set(new[name]):raise ValueError('Missing refold')
            for i in range(8):
                a,b=new[name+'/'+str(i)][:],old[name+'/'+str(i)][:]
                if a.shape!=b.shape or not np.isfinite(a).all():raise ValueError('Invalid replay coordinates')
                maximum=max(maximum,float(np.max(np.abs(a-b))))
    fields=('name','raw_gate_passed','scaffold_joint_success','valid_designable','complete_strict','complete_connected_designable',
            'scaffold_successful_refold_indices','complete_strict_indices')
    decisions=len(d['records'])==len(rd['records']) and all(a[k]==b[k] for a,b in zip(d['records'],rd['records']) for k in fields)
    return dict(qualified=maximum<=1e-5 and decisions,identical_sequences=True,refolds=256,new_scientific_attempts=0,
        max_atom_difference=maximum,identical_decisions=decisions,
        seconds={k:m[k] for k in ('elapsed_seconds','mpnn_seconds','teacher_staging_seconds','teacher_load_seconds')},
        reference_seconds={k:rm[k] for k in ('elapsed_seconds','mpnn_seconds','teacher_load_seconds')},
        scope='Technical replay of original256attempts. Cache/node conditions differ; no controlled throughput claim. No extra attempts added to scientific counts.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    protocol=root/'configs/teacher_staging_replication_protocol.json';spec=json.loads(protocol.read_text());reference=root/'runs'/spec['reference_run'];profile=root/'runs'/spec['profile_run']
    c=copy.deepcopy(json.loads((reference/'manifest.json').read_text())['config']);c['teacher_checkpoint_staging']=True;c['teacher_staging_validation']={}
    for k,p in [('protocol',protocol),('profile_manifest',profile/'manifest.json'),('profile_report',root/'reports'/(profile.name+'.json')),
                ('reference_manifest',reference/'manifest.json'),('reference_report',root/'reports'/(reference.name+'.json')),('reference_refolded',reference/'refolded.h5')]:
        c['teacher_staging_validation'][k]=str(p);c['sources'].append(dict(path=str(p),sha256=sha(p)))
    c['file_identity']=[identity(r['path']) for r in c['sources']];c.pop('config_sha256');c['config_sha256']=hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest()
    validate(c,full=True)
    from prepare_fragment_preference_refold import audit_inputs
    audit_inputs(c)
    with a.output.open('x') as f:json.dump(c,f,indent=2)
    print('Staged replay CPU audit complete',flush=True)


if __name__=='__main__':main()
