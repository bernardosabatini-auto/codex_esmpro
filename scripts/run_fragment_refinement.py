"""Two bounded refinement rounds; isolate generator and teacher GPU residency."""
import argparse,json,subprocess,sys,time
from pathlib import Path
from fragment_refinement_core import audit_config,score_assay
from prepare_overfit import sha
from profile_gpu import atomic_json


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());audit_config(c);spec=c['spec'];a.output.mkdir(exist_ok=False)
    start=time.monotonic();m=dict(status='running',config=c,rounds=[],training_updates_executed=0)
    atomic_json(a.output/'manifest.json',m)
    feedback={r['target_id']:dict(record=r['initial'],name=r['source_name'],refolds=r['source_refolds'],raw=r['source_raw'],dataset=r['source_dataset'],slot=r['source_slot']) for r in c['cases']}
    def run(script,args):
        remaining=spec['work_cap_seconds']-(time.monotonic()-start)
        if remaining<=0:raise TimeoutError('Refinement campaign cap')
        subprocess.run([sys.executable,'-u','scripts/'+script]+list(map(str,args)),check=True,timeout=remaining)
    try:
        for round_index in spec['rounds']:
            fb=a.output/f'feedback_{round_index}.json';atomic_json(fb,feedback);gen=a.output/f'generation_{round_index}';assay=a.output/f'assay_{round_index}'
            run('generate_fragment_refinement.py',['--source',a.source,'--config',a.config,'--feedback',fb,'--round',round_index,'--output',gen])
            gm=json.loads((gen/'manifest.json').read_text())
            if gm['status']!='complete' or gm['peak_reserved_GiB']>75:raise ValueError('Generation profile failed')
            recipe=dict(c['teacher_recipe'],pilot_config=str(a.config.resolve()),pilot_config_sha256=sha(a.config),assay='fragment_refinement',entries=gm['entries'],expected_backbones=6,work_cap_seconds=480)
            for key,path in [('predictions',gen/'predictions.h5'),('generation_manifest',gen/'manifest.json'),('protocol',Path(c['protocol']))]:recipe[key]=str(path.resolve());recipe[key+'_sha256']=sha(path)
            ac=a.output/f'assay_{round_index}.json';atomic_json(ac,recipe)
            run('evaluate_designability.py',['--source',a.source,'--config',ac,'--output',assay])
            rows=score_assay(assay);summary=dict(round=round_index,records=rows,generation_manifest_sha256=sha(gen/'manifest.json'),assay_manifest_sha256=sha(assay/'manifest.json'),refolded_sha256=sha(assay/'refolded.h5'))
            m['rounds'].append(summary);atomic_json(a.output/'manifest.json',m)
            feedback={r['target_id']:dict(record=r,name=r['name'],refolds=str((assay/'refolded.h5').resolve()),raw=recipe['predictions'],dataset=r['dataset'],slot=0) for r in rows if r['arm']=='feedback'}
            print('Round',round_index,[(arm,sum(r['strict_joint_success'] for r in rows if r['arm']==arm)) for arm in ('feedback','random','native')],flush=True)
        m['status']='complete'
    except BaseException as e:m.update(status='failed',error=f'{type(e).__name__}: {e}');raise
    finally:m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
