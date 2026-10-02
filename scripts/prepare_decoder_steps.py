"""Freeze a complete broader native evaluation for paired decoder diagnostics."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from summarize_expanded_native import analyze


def main():
    p=argparse.ArgumentParser();p.add_argument('--native',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    path=a.native/'manifest.json';m=json.loads(path.read_text())
    if m['status']!='complete':raise ValueError('native screen incomplete')
    analyze(m);c=m['config'].copy()
    for h in c['heads']:
        for field in ('checkpoint','training_manifest'):
            if h.get(field) and sha(h[field])!=h[field+'_sha256']:raise ValueError('changed '+field)
    protocol=root/'configs/decoder_steps_protocol.json';predictions=a.native/'predictions.h5'
    c.update(source_native_manifest=str(path.resolve()),source_native_manifest_sha256=sha(path),source_native_predictions=str(predictions.resolve()),source_native_predictions_sha256=sha(predictions),protocol=str(protocol),protocol_sha256=sha(protocol),work_cap_seconds=1080)
    a.output.write_text(json.dumps(c,indent=2)+'\n');print('Frozen all five source heads and all64 tuning families')


if __name__=='__main__':main()
