"""Generate fixed independent noise replications for the frozen sample selector."""
import argparse
import json
import sys
from pathlib import Path

from analyze_consensus import digest
import collect_comparison


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--task', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text()); task = config['tasks'][args.task]
    if digest(Path(config['checkpoint'])) != config['checkpoint_sha256']:
        raise ValueError('source checkpoint changed')
    evaluation = json.loads(Path(config['evaluation_template']).read_text())
    evaluation.update(seed=task['seed'], flow_steps=[25], guidance=[2], samples=3,
        flow_precision='fp32', decoder_precision='fp32', internal_minutes=18,
        target_manifest=str((Path(config['evaluation_template']).parent/evaluation['target_manifest']).resolve()),
        consensus_protocol=config['consensus_protocol'], consensus_protocol_sha256=config['consensus_protocol_sha256'],
        development_clusters=config['development_clusters'], development_clusters_sha256=config['development_clusters_sha256'],
        reference_run=config['reference_run'])
    evaluation['models'] = {'pair':dict(checkpoint=config['checkpoint'], batches=config['batches'])}
    path = Path(str(args.output)+'_config.json'); path.write_text(json.dumps(evaluation, indent=2)+'\n')
    sys.argv = ['collect_comparison.py', '--source', config['source'], '--config', str(path), '--model', 'pair',
                '--output', str(args.output), '--nsys-metrics', '--allow-gpu', '--score-workers', '1',
                '--usalign', str(Path(__file__).resolve().parents[1]/'runs/tools/USalign/USalign')]
    collect_comparison.main()


if __name__ == '__main__':
    main()
