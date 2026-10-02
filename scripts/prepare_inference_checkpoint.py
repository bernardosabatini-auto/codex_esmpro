"""Export exactly the inherited EMA tensors on CPU, excluding optimizer state."""
import argparse,json
from pathlib import Path
import torch
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--expected-sha256',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();torch.set_num_threads(1)
    if a.output.exists():raise ValueError('do not overwrite a frozen inference checkpoint')
    source_sha=sha(a.source)
    if source_sha!=a.expected_sha256:raise ValueError('source checkpoint changed')
    source=torch.load(a.source,map_location='cpu',weights_only=False,mmap=True)
    output={k:source[k] for k in ('arch','extra_arch','model')};output['ema']={k:v.detach().clone() for k,v in source['ema'].items()};output['source_sha256']=source_sha
    a.output.parent.mkdir(parents=True,exist_ok=True);torch.save(output,a.output);del output
    frozen=torch.load(a.output,map_location='cpu',weights_only=True,mmap=True)
    if set(frozen['ema'])!=set(source['ema']) or any(not torch.equal(v,frozen['ema'][k]) for k,v in source['ema'].items()):raise ValueError('export changed EMA tensors')
    identity=dict(path=str(a.output.resolve()),sha256=sha(a.output),source_path=str(a.source.resolve()),source_sha256=source_sha,bytes=a.output.stat().st_size,source_bytes=a.source.stat().st_size,tensor_values_verified=True,tensors=len(frozen['ema']))
    Path(str(a.output)+'.identity.json').write_text(json.dumps(identity,indent=2)+'\n');print(json.dumps(identity))


if __name__=='__main__':main()
