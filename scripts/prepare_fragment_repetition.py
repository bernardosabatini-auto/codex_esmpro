"""Bind the predeclared one-case noise replication to audited model outputs."""
import argparse
import json
from pathlib import Path

from prepare_overfit import sha


SOURCE_KEYS = ('generation_manifest', 'training_report', 'checkpoint', 'fragments',
               'historical_manifest', 'historical_report', 'historical_predictions',
               'decoder_checkpoint', 'protocol')


def audit_config(c):
    for key in SOURCE_KEYS:
        if sha(c[key]) != c[key + '_sha256']:
            raise ValueError('Changed repetition source: ' + key)
    spec = json.loads(Path(c['protocol']).read_text())
    for key in ('target_id', 'condition', 'seed', 'historical_seed', 'samples',
                'guidance', 'steps', 'decoder_steps', 'work_cap_seconds'):
        if c[key] != spec[key]:
            raise ValueError('Changed prospective recipe: ' + key)
    if c.get('batch_size', 16) != spec.get('batch_size', 16):
        raise ValueError('Changed batching recipe')
    if 'original_protocol' in spec:
        root = Path(__file__).resolve().parents[1]
        if sha(root / spec['original_protocol']) != spec['original_protocol_sha256']:
            raise ValueError('Changed original failed protocol')
    for prefix, expected in [('generation', spec['parent_training']),
                             ('historical', spec['historical_screen'])]:
        path = Path(c[prefix + '_manifest'])
        m = json.loads(path.read_text())
        report = json.loads(Path(c['training_report' if prefix == 'generation'
                                       else 'historical_report']).read_text())
        if path.parent.name != expected or m['status'] != 'complete' or report['status'] != 'complete' or report['manifest_sha256'] != sha(path):
            raise ValueError('Unaudited repetition parent')
    training = json.loads(Path(c['generation_manifest']).read_text())
    historical = json.loads(Path(c['historical_manifest']).read_text())
    if (training['updates'] != 2000 or historical['config']['checkpoint_sha256'] != c['checkpoint_sha256']
            or historical['predictions_sha256'] != c['historical_predictions_sha256']
            or historical['config']['fragments_sha256'] != c['fragments_sha256']):
        raise ValueError('Changed model/data lineage')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--batch-four', action='store_true')
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    protocol = root / ('configs/fragment_repetition_batch4_protocol.json' if a.batch_four else 'configs/fragment_repetition_protocol.json')
    spec = json.loads(protocol.read_text())
    train = root / 'runs' / spec['parent_training']
    old = root / 'runs' / spec['historical_screen']
    tc = json.loads((train / 'manifest.json').read_text())['config']
    c = {key: spec[key] for key in ('target_id', 'condition', 'seed', 'historical_seed',
         'samples', 'guidance', 'steps', 'decoder_steps', 'work_cap_seconds')}
    c['batch_size'] = spec.get('batch_size', 16)
    paths = dict(generation_manifest=train / 'manifest.json',
                 training_report=root / 'reports' / (train.name + '.json'),
                 checkpoint=train / 'ema_2000.ckpt', fragments=Path(tc['fragments']),
                 historical_manifest=old / 'manifest.json',
                 historical_report=root / 'reports' / (old.name + '.json'),
                 historical_predictions=old / 'predictions.h5',
                 decoder_checkpoint=Path(tc['decoder_checkpoint']), protocol=protocol)
    for key, path in paths.items():
        c[key], c[key + '_sha256'] = str(path.resolve()), sha(path)
    audit_config(c)
    a.output.write_text(json.dumps(c, indent=2) + '\n')


if __name__ == '__main__':
    main()
