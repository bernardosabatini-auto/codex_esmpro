"""Reuse every frozen noise/panel choice for the complementary weights/steps cells."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from summarize_generative_pilot import analyze


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/generative_crossover_protocol.json';recipe=json.loads(protocol.read_text());run=root/recipe['parent_run']
    if analyze(run)['status']!='complete':raise ValueError('Parent incomplete')
    m=json.loads((run/'manifest.json').read_text());c=m['config'];c.update(protocol=str(protocol),protocol_sha256=sha(protocol),work_cap_seconds=480,parent_manifest=str(run/'manifest.json'),parent_manifest_sha256=sha(run/'manifest.json'))
    for h in c['heads']:
        h['name']='original10' if h['name']=='original50' else 'reflow50';h['steps']=recipe['heads'][h['name']]
    a.output.write_text(json.dumps(c,indent=2)+'\n');print('Frozen complementary weights/steps cells')

if __name__=='__main__':main()
