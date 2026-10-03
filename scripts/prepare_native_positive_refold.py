import argparse
import json
from pathlib import Path
import h5py
from native_positive_coverage import audit_generation,audit_refold
from prepare_fragment_preference_refold import TEACHER_KEYS,make_entry
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--generation',type=Path,required=True);p.add_argument('--output-prefix',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];run=a.generation.resolve()
    gm=json.loads((run/'manifest.json').read_text());gc=gm['config'];spec=audit_generation(gc);d=json.loads((root/'reports'/(run.name+'.json')).read_text())
    if gm['status']!='complete' or d['status']!='complete' or not d['native_generation_gate']:raise ValueError('Native generation gate failed')
    profile=root/'runs'/spec['refold_profile'];pc=json.loads((profile/'manifest.json').read_text())['config']
    for part in range(4):
        path=Path(str(a.output_prefix)+f'_{part}.json').resolve();inputs=path.with_suffix('.h5')
        c={k:pc[k] for k in TEACHER_KEYS};c.update(native_positive_coverage=True,assay='fragment_preference_refold',partition=part,expected_backbones=32,entries=[],allocation_minutes=35,work_cap_seconds=2010,teacher_deterministic_algorithms=True)
        for key,value in [('generation_manifest',run/'manifest.json'),('generation_report',root/'reports'/(run.name+'.json')),('generated_predictions',run/'predictions.h5'),('protocol',gc['protocol']),('teacher_profile_manifest',profile/'manifest.json'),('teacher_profile_report',root/'reports'/(profile.name+'.json')),('teacher_probe',root/'reports/teacher_repeatability_probe_50154738.json')]:
            c[key]=str(value);c[key+'_sha256']=sha(value)
        with h5py.File(gc['fragments']) as fr,h5py.File(run/'predictions.h5') as gen,h5py.File(inputs,'x') as out:
            for row in (r for r in gc['selected'] if r['partition']==part):
                q=fr['train/'+row['id']+'/conditions/c20_center'];out.create_dataset('motifs/'+row['id'],data=q['fragment'][:])
                for slot in range(2):
                    entry=make_entry(row,q,slot,len(c['entries']),arm='native_latent');c['entries'].append(entry);out.create_dataset(entry['dataset'],data=gen['native/'+row['id']+'/backbone'][slot][None])
        c.update(predictions=str(inputs),predictions_sha256=sha(inputs));audit_refold(c)
        with path.open('x') as f:json.dump(c,f,indent=2)
        print(part,len(c['entries']),flush=True)


if __name__=='__main__':main()
