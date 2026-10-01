"""Evaluate a predeclared checkpoint with the existing full development protocol."""
import argparse,json,sys
from pathlib import Path
import collect_comparison


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--task',type=int,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    config=json.loads(a.config.read_text());task=config['tasks'][a.task]
    evaluation=json.loads(Path(config['evaluation_template']).read_text())
    evaluation.update(flow_steps=[25],guidance=[2],samples=3,flow_precision='fp32',decoder_precision='fp32',internal_minutes=20,
        target_manifest=str((Path(config['evaluation_template']).parent/evaluation['target_manifest']).resolve()),
        probe=task,reference_run=config['reference_run'],development_clusters=config['development_clusters'],development_clusters_sha256=config['development_clusters_sha256'])
    evaluation['models']={'pair':dict(checkpoint=task['checkpoint'],batches=config['batches'])}
    path=Path(str(a.output)+'_config.json');path.write_text(json.dumps(evaluation,indent=2)+'\n')
    sys.argv=['collect_comparison.py','--source',config['source'],'--config',str(path),'--model','pair','--output',str(a.output),
        '--nsys-metrics','--allow-gpu','--score-workers','1','--usalign',str(Path(__file__).resolve().parents[1]/'runs/tools/USalign/USalign')]
    collect_comparison.main()


if __name__=='__main__':main()
