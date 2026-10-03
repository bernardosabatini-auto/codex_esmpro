"""Advance only the frozen training -> generation -> refolding graph, one submission/tick."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess

from prepare_overfit import sha
from watch_jobs import TERMINAL, stamp, write_json

UNIT = 'esm-proae-broad-fragment-followups.timer'
PYTHON = '/n/home08/bsabatini/.conda/envs/proteinae/bin/python'
ARMS = ('control_weight3', 'control_balanced', 'broad_weight3', 'broad_balanced')
CONDITIONS = ('c20_center', 'f30_center')


def graph_layout(study):
    if study == 'broad':
        return ARMS, CONDITIONS
    if study == 'frozen':
        return ('control_frozen', 'broad_frozen'), ('c20_center',)
    if study == 'quality':
        return ('control', 'quality'), ('c20_center',)
    raise ValueError('Unknown fixed fragment study')


def generation_paths(study, condition, arm):
    if study == 'quality':
        name = 'fragment_quality_eval_' + arm
        return ('slurm/' + name + '_rtx.sbatch', 'runs/' + name + '_20261003.json',
                'configs/fragment_quality_c20_validation_protocol.json')
    if study == 'frozen':
        name = 'fragment_frozen_eval_' + arm.removesuffix('_frozen')
        return ('slurm/' + name + '_rtx.sbatch', 'runs/' + name + '_20261003.json',
                'configs/fragment_frozen_c20_validation_protocol.json')
    name = 'broad_eval_' + condition + '_' + arm
    return ('slurm/' + name + '_rtx.sbatch', 'runs/' + name + '.json',
            'configs/fragment_broad_' + condition + '_validation_protocol.json')


def existing_job(jobs, script):
    found = [j for j in jobs if j.get('script') == script]
    if len(found) > 1:
        raise ValueError('Duplicate fixed follow-up: ' + script)
    return found[0] if found else None


def completed_report(root, job, watch, prefix):
    jid = job['id']
    state = watch.get('jobs', {}).get(jid, {}).get('tasks', {}).get(jid, {}).get('state')
    if state in TERMINAL - {'COMPLETED'}:
        raise ValueError('Failed registered predecessor ' + jid + ': ' + state)
    path = root / 'reports' / (prefix + '_' + jid + '.json')
    if state != 'COMPLETED' or not path.exists():
        return None
    report = json.loads(path.read_text())
    if report['status'] != 'complete':
        raise ValueError('Failed predecessor analysis: ' + str(path))
    mp = root / 'runs' / (prefix + '_' + jid) / 'manifest.json'
    if report['manifest_sha256'] != sha(mp):
        raise ValueError('Stale predecessor analysis: ' + str(path))
    return report


def advance(root, plan, jobs, watch, *, dry_run=False):
    byid = {j['id']: j for j in jobs}
    study = plan.get('study', 'broad'); arms, conditions = graph_layout(study)
    if set(plan['parents']) != set(arms) or len(set(plan['parents'].values())) != len(arms):
        raise ValueError('Changed fixed training graph')
    parents = []; waiting_training = False
    for arm in arms:
        jid = plan['parents'][arm]
        if jid not in byid or byid[jid]['completion_action'] != 'summarize_fragment_training':
            raise ValueError('Unregistered training parent')
        frozen = json.loads((Path(byid[jid]['code_snapshot']) / 'entry_configs/0.json').read_text())
        if frozen['extension_arm'] != arm or frozen['profile_only'] or frozen['updates'] != 2000 or frozen['broad_corpus_protocol_sha256'] != plan['training_protocol_sha256']:
            raise ValueError('Wrong registered training parent')
        if bool(frozen.get('freeze_trunk')) != (study in ('frozen','quality')):
            raise ValueError('Wrong generator update policy')
        if bool(frozen.get('condition_selection')) != (study == 'quality'):
            raise ValueError('Wrong condition-selection policy')
        if completed_report(root, byid[jid], watch, 'fragment_training') is None:
            waiting_training = True
        parents.append(root / 'runs' / ('fragment_training_' + jid))
    if waiting_training:
        return dict(status='active', phase='waiting_training')
    env = dict(os.environ, CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
               OPENBLAS_NUM_THREADS='1', PYTHONPATH=str(root / 'src'))
    def run(args, timeout=600):
        out = subprocess.run([PYTHON, *map(str, args)], cwd=root, env=env, text=True,
                             capture_output=True, timeout=timeout)
        if out.returncode:
            raise RuntimeError((out.stderr or out.stdout)[-3000:])
        return out.stdout
    def submit(script, config, action, purpose):
        minutes = json.loads((root / config).read_text()).get('allocation_minutes', 20)
        try:
            result = run(['scripts/submit_registered.py', '--script', script, '--purpose', purpose,
                          '--minutes', str(minutes), '--action', action])
        except RuntimeError as error:
            # The registered guard remains the sole authority for capacity and watcher health.
            # Preserve a transient rejection and retry on the next timer tick, never bypass it.
            if not any(message in str(error) for message in ('project GPU cap would be exceeded', 'watcher heartbeat stale')):
                raise
            return dict(status='active', phase='submission_guard_wait', script=script, error=str(error))
        return dict(status='active', phase='submitted', script=script,
                    submitted=json.loads(result.strip().splitlines()[-1])['submitted'])
    comparison = root / dict(frozen='reports/fragment_frozen_training_20261003.json',quality='reports/fragment_quality_training_20261003.json',broad='reports/broad_fragment_training_20261003.json')[study]
    if not comparison.exists():
        if dry_run:
            return dict(status='active', phase='ready_training_comparison')
        run([dict(frozen='scripts/compare_frozen_fragment_training.py',quality='scripts/compare_fragment_quality_training.py',broad='scripts/compare_broad_fragment_training.py')[study], '--runs', *parents,
             '--output', comparison.with_suffix('')])
        return dict(status='active', phase='training_compared')
    compared = json.loads(comparison.read_text())
    if compared['status'] != 'complete' or compared['profile_only'] or compared['matched_training_updates'] != 2000 or compared['protocol_sha256'] != plan['training_protocol_sha256']:
        raise ValueError('Unqualified matched training comparison')
    generations = {}
    for condition in conditions:
        generations[condition] = []
        for arm in arms:
            script, config, protocol = generation_paths(study, condition, arm)
            job = existing_job(jobs, script)
            if job is None:
                if dry_run:
                    return dict(status='active', phase='ready_generation', script=script)
                run(['scripts/prepare_extra_fragment_validation.py', '--protocol',
                     protocol,
                     '--arm', arm, '--output', config])
                return submit(script, config, 'summarize_extra_fragment_validation',
                              'Fixed ' + study + '-fragment endpoint generation ' + condition + ' ' + arm)
            frozen = json.loads((Path(job['code_snapshot']) / 'entry_configs/0.json').read_text())
            if frozen['arm'] != arm or frozen['spec']['condition'] != condition or Path(frozen['model_manifest']).parent.name != 'fragment_training_' + plan['parents'][arm]:
                raise ValueError('Wrong existing generation lineage')
            completed_report(root, job, watch, 'extra_fragment_validation')
            generations[condition].append(job)
    all_done = True
    for condition in conditions:
        gen_jobs = generations[condition]
        if any(completed_report(root, j, watch, 'extra_fragment_validation') is None for j in gen_jobs):
            all_done = False
            continue
        refold_prefix = dict(frozen='fragment_frozen_refold_',quality='fragment_quality_refold_',broad='broad_refold_')[study]
        prefix = 'runs/' + refold_prefix + condition
        configs = [Path(prefix + '_' + str(k) + '.json') for k in range(4)]
        if not all((root / c).exists() for c in configs):
            if any((root / c).exists() for c in configs):
                raise ValueError('Partial refold preparation; inspect before resuming')
            if dry_run:
                return dict(status='active', phase='ready_refold_preparation', condition=condition)
            run(['scripts/prepare_extra_fragment_refold.py', '--generations',
                 *[root / 'runs' / ('extra_fragment_validation_' + j['id']) for j in gen_jobs],
                 '--output-prefix', prefix], timeout=720)
            return dict(status='active', phase='refolds_prepared', condition=condition)
        refolds = []
        for k, config in enumerate(configs):
            name = refold_prefix + condition + '_' + str(k)
            script = 'slurm/' + name + '_rtx.sbatch'
            c = json.loads((root / config).read_text())
            if c['partition'] != k or Path(c['protocol']).name != Path(generation_paths(study, condition, arms[0])[2]).name:
                raise ValueError('Wrong prepared refold configuration')
            job = existing_job(jobs, script)
            if job is None:
                if dry_run:
                    return dict(status='active', phase='ready_refold', script=script)
                minutes = c['allocation_minutes']
                body = (root / 'slurm/broad_refold_template_rtx.sbatch').read_text()
                body = body.replace('@NAME@', name).replace('@TIME@', f'{minutes//60:02d}:{minutes%60:02d}:00').replace('@CONFIG@', str(config))
                path = root / script
                if path.exists() and path.read_text() != body:
                    raise ValueError('Changed generated refold script')
                path.write_text(body)
                return submit(script, str(config), 'summarize_extra_fragment_refold',
                              'Fixed ' + study + '-fragment same-refold assay ' + condition + ' partition' + str(k))
            frozen = json.loads((Path(job['code_snapshot']) / 'entry_configs/0.json').read_text())
            if frozen['partition'] != k or frozen['generation_manifest_sha256'] != c['generation_manifest_sha256'] or frozen['predictions_sha256'] != c['predictions_sha256']:
                raise ValueError('Wrong existing refold lineage')
            completed_report(root, job, watch, 'extra_fragment_refold')
            refolds.append(job)
        if any(completed_report(root, j, watch, 'extra_fragment_refold') is None for j in refolds):
            all_done = False
            continue
        out = root / 'reports' / dict(frozen='fragment_frozen_c20_comparison_20261003.json',quality='fragment_quality_c20_comparison_20261003.json',broad='broad_fragment_' + condition + '_comparison.json')[study]
        if not out.exists():
            if dry_run:
                return dict(status='active', phase='ready_refold_comparison', condition=condition)
            extra=['--protocol','configs/fragment_quality_comparison_protocol.json'] if study=='quality' else []
            run(['scripts/compare_frozen_fragment_refolds.py' if study in ('frozen','quality') else 'scripts/compare_extra_fragment_refolds.py', *extra, '--runs',
                 *[root / 'runs' / ('extra_fragment_refold_' + j['id']) for j in refolds],
                 '--output', out.with_suffix('')])
            return dict(status='active', phase='refolds_compared', condition=condition)
        if json.loads(out.read_text())['status'] != 'complete':
            raise ValueError('Incomplete endpoint comparison')
    return dict(status='resolved' if all_done else 'active', phase='resolved' if all_done else 'waiting_assays')


def tick(root, dry_run=False, study='broad'):
    root = Path(root).resolve()
    graph_layout(study)
    stem = study + '_fragment_followups'
    plan = json.loads((root / ('runs/' + stem + '.json')).read_text())
    if plan.get('study', 'broad') != study:raise ValueError('Wrong fixed study plan')
    policy = json.loads((root / 'runs/execution_policy.json').read_text())
    if plan['status'] != 'active' or policy['status'] != 'active':
        return dict(status='inactive')
    with (root / ('runs/' + stem + '.lock')).open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return dict(status='locked')
        try:
            for path, digest in plan['code_sha256'].items():
                if sha(root / path) != digest:
                    raise ValueError('Frozen follow-up source changed: ' + path)
            jobs = json.loads((root / 'runs/jobs.json').read_text())['jobs']
            watch = json.loads((root / 'runs/watch/state.json').read_text())
            result = advance(root, plan, jobs, watch, dry_run=dry_run)
        except Exception as error:
            result = dict(status='failed', error=f'{type(error).__name__}: {error}')
        result['checked_at'] = stamp()
        if not dry_run:
            write_json(root / ('runs/' + stem + '_state.json'), result)
            if result['status'] in ('failed', 'resolved'):
                subprocess.run(['systemctl', '--user', 'stop', 'esm-proae-' + stem.replace('_','-') + '.timer'], check=True, timeout=10)
        return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--study', choices=('broad','frozen','quality'), default='broad')
    a = p.parse_args()
    print(json.dumps(tick(Path(__file__).resolve().parents[1], a.dry_run, a.study)))
