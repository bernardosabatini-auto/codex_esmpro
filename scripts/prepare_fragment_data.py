"""Freeze existing audited training references and isolated development fragments."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from latentfold.teacher_states import audited_families


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    training=root/'runs/overfit_labels_49693246/manifest.json';tm=json.loads(training.read_text());dev=root/'runs/isolated_motif_49864561/manifest.json';dm=json.loads(dev.read_text());selection=Path(dm['config']['selection']);rows=json.loads(selection.read_text())['rows'];families={r['id']:r['family'] for r in tm['config']['targets']}
    if tm['status']!='complete' or not tm['training_gate_passed'] or dm['status']!='complete' or set(families.values())&{r['family'] for r in rows}:raise ValueError('Invalid source or family overlap')
    if len(families)!=32 or len(rows)!=16:raise ValueError('Unexpected source counts')
    c=dict(seed=2026100231,work_cap_seconds=480,training_targets=tm['config']['targets'],development_rows=rows)
    for key,path in [('protocol',root/'configs/fragment_conditioning_protocol.json'),('training_manifest',training),('training_labels',training.parent/'labels.h5'),('development_manifest',dev),('development_predictions',dev.parent/'predictions.h5'),('selection',selection),('decoder_checkpoint',Path(dm['config']['decoder_checkpoint']))]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
    if c['training_labels_sha256']!=tm['labels_sha256']:raise ValueError('Changed training arrays')
    a.output.write_text(json.dumps(c,indent=2)+'\n')


if __name__=='__main__':main()
