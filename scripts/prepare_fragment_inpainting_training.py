import argparse
import json
from pathlib import Path
from fragment_inpainting_core import audit
from prepare_overfit import sha


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--profile', action='store_true')
    p.add_argument('--profile-report', type=Path)
    p.add_argument('--junction-weighted', action='store_true')
    p.add_argument('--flank-context', action='store_true')
    p.add_argument('--scaffold-bridge', action='store_true')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    protocol = root / 'configs/fragment_coordinate_inpainting_protocol.json'
    spec = json.loads(protocol.read_text())
    base = root / 'runs' / spec['baseline_generation']
    closed = root / 'runs' / spec['closed_decoder']
    bc = json.loads((base / 'manifest.json').read_text())['config']
    cc = json.loads((closed / 'manifest.json').read_text())['config']
    c = dict(spec=spec, profile_only=a.profile, updates=spec['profile_updates' if a.profile else 'updates'],
             selected=bc['selected'], training_ids=cc['training_ids'], sources=[], allocation_minutes=25, work_cap_seconds=1380)
    def bind(path):
        path = Path(path).resolve()
        c['sources'].append(dict(path=str(path), sha256=sha(path)))
        return str(path)
    for key, path in [('protocol', protocol), ('student_comparison', root/'reports/repaint_student_model_comparison_20261004.json'), ('baseline_manifest', base/'manifest.json'),
                      ('baseline_report', root/'reports'/(base.name+'.json')), ('baseline_predictions', base/'predictions.h5'),
                      ('closed_manifest', closed/'manifest.json'), ('closed_report', root/'reports'/(closed.name+'.json')),
                      ('fragments', bc['fragments']), ('decoder_checkpoint', bc['decoder_checkpoint']),
                      ('diagnostic_manifest', cc['diagnostic_manifest']), ('diagnostic_predictions', cc['diagnostic_predictions'])]:
        c[key] = bind(path)
    if a.junction_weighted or a.flank_context or a.scaffold_bridge:
        c['junction_protocol'] = bind(root/'configs/fragment_junction_weighted_protocol.json')
        c['junction_spec'] = js = json.loads(Path(c['junction_protocol']).read_text())
        c['junction_loss'] = {k: js[k] for k in ('junction_width', 'junction_mass')}
        prior = root/'runs'/js['baseline_training']
        for key, path in [('junction_baseline_manifest', prior/'manifest.json'),
                          ('junction_baseline_predictions', prior/'predictions.h5'),
                          ('junction_baseline_report', root/'reports'/(prior.name+'.json')),
                          ('junction_comparison', root/js['baseline_comparison']),
                          ('junction_diagnostic', root/js['diagnostic'])]:
            c[key] = bind(path)
    if not a.profile:
        if a.profile_report is None:
            raise ValueError('Completed profile required')
        c['profile_report'] = bind(a.profile_report)
        pr = json.loads(a.profile_report.read_text())
        c['allocation_minutes'] = pr['recommended_full_minutes']
        c['work_cap_seconds'] = 60*c['allocation_minutes'] - 120
        c['profile_manifest'] = bind(pr['manifest_path'])
        c['profile_checkpoint'] = bind(Path(pr['manifest_path']).parent/'checkpoint.pt')
    if a.flank_context or a.scaffold_bridge:
        from fragment_flank_core import file_stats
        from fragment_inpainting_core import load_training
        import torch
        c['flank_protocol'] = bind(root/'configs/fragment_flank_context_protocol.json')
        c['flank_spec'] = fs = json.loads(Path(c['flank_protocol']).read_text())
        c['context_flank'] = fs['context_flank']
        prior = root/'runs'/fs['baseline']
        for key, path in [('flank_baseline_manifest', prior/'manifest.json'),
                          ('flank_baseline_predictions', prior/'predictions.h5'),
                          ('flank_baseline_report', root/'reports'/(prior.name+'.json')),
                          ('flank_compatible_report', root/'reports/compatible_fragment_50364419.json'),
                          ('flank_refresh_report', root/'reports/context_refresh_50371008.json'),
                          ('flank_closure_protocol', root/'configs/fragment_local_closure_canonical_protocol.json'),
                          ('flank_closure_code', root/'src/latentfold/local_closure.py')]:
            c[key] = bind(path)
        if a.scaffold_bridge:
            c['bridge_protocol'] = bind(root/'configs/fragment_scaffold_bridge_protocol.json')
            c['bridge_spec'] = bs = json.loads(Path(c['bridge_protocol']).read_text())
            previous = root/'runs'/bs['failed_predecessor']
            for key, path in [('bridge_previous_manifest', previous/'manifest.json'),
                              ('bridge_previous_report', root/'reports'/(previous.name+'.json')),
                              ('bridge_reachability', root/'reports/scaffold_bridge_reachability_20261004.json')]:
                c[key] = bind(path)
        before = file_stats(c)
        cache = a.output.with_suffix('.training.pt')
        if cache.exists(): raise FileExistsError(cache)
        torch.save(load_training(c), cache)
        if file_stats(c) != before: raise ValueError('Sources changed during CPU data preparation')
        c['flank_training_cache'] = bind(cache)
        before = file_stats(c)
        audit(c)
        if file_stats(c) != before: raise ValueError('Sources changed during CPU content verification')
        c['cpu_verified_file_stats'] = before
    else:
        audit(c)
    with a.output.open('x') as f:
        json.dump(c, f, indent=2)
    print('profile' if a.profile else 'full', c['updates'], len(c['training_ids']), c['allocation_minutes'])


if __name__ == '__main__':
    main()
