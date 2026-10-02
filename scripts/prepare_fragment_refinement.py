"""Bind two selected, already audited failures to a prospective repair pilot."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from fragment_refinement_core import audit_config


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];protocol=root/'configs/fragment_refinement_protocol.json'
    spec=json.loads(protocol.read_text());report_path=root/'reports'/(spec['initial_report']+'.json')
    report=json.loads(report_path.read_text());train=root/'runs'/spec['parent_training']
    tm=json.loads((train/'manifest.json').read_text());c=dict(spec=spec,protocol=str(protocol),cases=[],sources=[])
    if report['status']!='complete' or tm['status']!='complete' or tm['updates']!=2000 or not all(report['native_strict_controls'].values()):raise ValueError('Unqualified parent')
    def bind(path):
        path=Path(path).resolve();row=dict(path=str(path),sha256=sha(path))
        if row not in c['sources']:c['sources'].append(row)
        return str(path)
    bind(protocol);bind(report_path);bind(train/'manifest.json')
    c['checkpoint']=bind(train/'ema_2000.ckpt');c['fragments']=bind(tm['config']['fragments'])
    c['decoder_checkpoint']=bind(tm['config']['decoder_checkpoint']);c['native_predictions']=bind(tm['config']['initial_predictions'])
    c['historical_predictions']=bind(train/'evaluation_2000.h5')
    for ident in spec['cases']:
        r=next(x for x in report['records'] if x['arm']=='weighted128' and x['target_id']==ident)
        if not r['raw_gate_passed'] or r['strict_joint_success'] or not r['valid_designable']:raise ValueError('Changed selection')
        run=Path(r.get('reused_from',root/'runs'/spec['initial_report']));manifest=run/'manifest.json'
        m=json.loads(manifest.read_text());name=r.get('source_name',r['name']);entry=next(x for x in m['config']['entries'] if x['name']==name)
        if m['status']!='complete' or sha(manifest)!=r.get('source_manifest_sha256',report['manifest_sha256']):raise ValueError('Changed initial refold parent')
        c['cases'].append(dict(target_id=ident,initial=r,source_name=name,source_dataset=entry['dataset'],source_slot=entry['slot'],
            source_manifest=bind(manifest),source_refolds=bind(run/'refolded.h5'),source_raw=bind(m['config']['predictions']),
            motif_start=entry['motif_start'],fixed_sequence=entry['fixed_sequence'],length=entry['length']))
    c['teacher_recipe']={k:m['config'][k] for k in ('num_sequences','temperature','mpnn_seed','seed','mpnn','dependencies','teacher_artifacts','precision','usalign','usalign_sha256')}
    audit_config(c);a.output.write_text(json.dumps(c,indent=2)+'\n')

if __name__=='__main__':main()
