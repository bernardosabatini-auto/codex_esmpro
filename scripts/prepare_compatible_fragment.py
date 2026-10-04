import argparse,json
from pathlib import Path
from compatible_fragment_core import audit
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    protocol=root/'configs/compatible_fragment_diagnostic_protocol.json';spec=json.loads(protocol.read_text());run=root/'runs'/spec['parent_run']
    gc=json.loads((run/'manifest.json').read_text())['config'];c=dict(spec=spec,selected=gc['selected'],sources=[],work_cap_seconds=480)
    for key,path in [('protocol',protocol),('source_manifest',run/'manifest.json'),('source_report',root/'reports'/(run.name+'.json')),
                     ('source_predictions',run/'predictions.h5'),('checkpoint',run/'checkpoint.pt'),('fragments',gc['fragments']),
                     ('decoder_checkpoint',gc['decoder_checkpoint']),('noise_source',root/'runs/inpainting_integrator_50351369/predictions.h5'),
                     ('closure_report',root/'reports/local_closure_canonical_full_20261004.json'),
                     ('reachability_report',root/'reports/local_closure_reachability_20261004.json'),
                     ('closure_effects_report',root/'reports/local_closure_effects_20261004.json'),
                     ('closure_protocol',root/'configs/fragment_local_closure_canonical_protocol.json'),
                     ('closure_code',root/'src/latentfold/local_closure.py')]:
        path=Path(path).resolve();c[key]=str(path);c['sources'].append(dict(path=str(path),sha256=sha(path)))
    audit(c)
    with a.output.open('x') as f:json.dump(c,f,indent=2)
    print('Frozen32proteins x4noises x4compatible arms; no refolding')


if __name__=='__main__':main()
