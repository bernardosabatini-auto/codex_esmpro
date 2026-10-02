"""Bind training-only cached predictions before the fixed latent-repair probe."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from expanded_corpus import metadata


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    protocol=root/'configs/latent_repair_protocol.json';recipe=json.loads(protocol.read_text());sources=[]
    registry={r['id']:r for r in json.loads((root/'runs/jobs.json').read_text())['jobs']}
    for jid in recipe['training_jobs']:
        if jid not in registry:raise ValueError('unregistered training source')
        manifest=root/f'runs/overfit_{jid}/manifest.json';m=json.loads(manifest.read_text());c=m['config'];inventory=metadata(c)
        if m['status']!='complete' or m['updates']!=2000 or c['label_distribution']!='balanced' or c.get('local_geometry') or c.get('trainable_tail_blocks') is not None:raise ValueError('wrong training-only source')
        predictions=manifest.parent/'evaluation_2000.h5'
        sources.append(dict(job_id=jid,manifest=str(manifest),manifest_sha256=sha(manifest),predictions=str(predictions),predictions_sha256=sha(predictions),evaluation_seed=c['evaluation_seed'],targets=[{k:r[k] for k in ('id','length','bucket','family')} for r in inventory['targets']]))
    a.output.write_text(json.dumps(dict(protocol=str(protocol),protocol_sha256=sha(protocol),sources=sources),indent=2)+'\n')


if __name__=='__main__':main()
