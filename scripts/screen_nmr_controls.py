"""Screen experimental model dispersion without interpreting NMR model populations."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request
import numpy as np
from latentfold.metrics import ca_metrics
from map_ensemble_references import parse_reference


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--metadata',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=True)
    protocol=dict(minimum_models=10,maximum_models_evaluated=16,minimum_common_coverage=.95,maximum_mean_pairwise_ca_rmsd=1.,maximum_90th_percentile_ca_rmsd=1.5,selection='Evenly spaced model indices; thresholds frozen before model ensemble predictions',interpretation='Low experimental-model dispersion controls; not proof of dynamical rigidity or equilibrium populations')
    report=dict(status='running',protocol=protocol,accepted=[],rejected=[])
    def save():
        temp=a.output/'screen.tmp';temp.write_text(json.dumps(report,indent=2)+'\n');temp.replace(a.output/'screen.json')
    save()
    try:
        for item in json.loads(a.metadata.read_text()):
            try:
                raw=a.output/(item['pdb_id']+'.pdb')
                if not raw.exists():
                    with urllib.request.urlopen('https://files.rcsb.org/download/'+item['pdb_id']+'.pdb',timeout=30) as response:data=response.read(32*1024**2+1)
                    if len(data)>32*1024**2:raise ValueError('reference exceeds 32 MiB cap')
                    raw.write_bytes(data)
                models=[];current=[]
                for line in raw.read_text().splitlines():
                    if line.startswith('MODEL'):current=[]
                    elif line.startswith('ENDMDL'):
                        models.append(current);current=[]
                    elif line.startswith('ATOM') and line[21]==item['chains'][0]:current.append(line)
                if len(models)<10:raise ValueError('fewer than 10 experimental models')
                selected=np.linspace(0,len(models)-1,min(16,len(models)),dtype=int).tolist()
                folder=a.output/item['id'];folder.mkdir(exist_ok=True);refs=[]
                for index in selected:
                    path=folder/f'model_{index}.pdb';path.write_text('\n'.join(models[index])+ '\nEND\n')
                    refs.append(parse_reference(path,item['sequence']))
                common=sorted(set.intersection(*[set(r['observed_indices']) for r in refs]))
                if len(common)/len(item['sequence'])<.95:raise ValueError('less than 95 percent common backbone coverage')
                coords=[np.asarray(r['backbone'])[[r['observed_indices'].index(i) for i in common],1] for r in refs]
                rmsds=[ca_metrics(coords[i],coords[j])['ca_rmsd'] for i in range(len(coords)) for j in range(i)]
                mean=float(np.mean(rmsds));upper=float(np.quantile(rmsds,.9))
                if mean>1. or upper>1.5:raise ValueError(f'experimental dispersion too high: mean={mean:.4f}, p90={upper:.4f}')
                report['accepted'].append(dict(**item,source_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),source_url='https://files.rcsb.org/download/'+item['pdb_id']+'.pdb',total_models=len(models),selected_models=selected,references=refs,common_indices=common,mean_pairwise_ca_rmsd=mean,p90_pairwise_ca_rmsd=upper))
            except Exception as error:report['rejected'].append(dict(id=item['id'],reason=f'{type(error).__name__}: {error}'))
            save();print('NMR screened',len(report['accepted'])+len(report['rejected']),'accepted',len(report['accepted']),flush=True)
        report['status']='complete'
    except BaseException as error:report.update(status='failed',error=str(error));raise
    finally:save()


if __name__=='__main__':main()
