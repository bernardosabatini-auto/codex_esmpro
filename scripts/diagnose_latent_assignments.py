"""Compare permissive latent nearest-label identities with decoded contact hits."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from scipy.spatial.distance import cdist
from latentfold.teacher_states import audited_families
from prepare_overfit import sha


def nearest(z,bank):
    if z.ndim!=3 or bank.ndim!=3 or z.shape[1:]!=bank.shape[1:] or not np.isfinite(z).all() or not np.isfinite(bank).all():raise ValueError('invalid latent arrays')
    distance=cdist(z.reshape(len(z),-1),bank.reshape(len(bank),-1))/np.sqrt(np.prod(z.shape[1:]))
    return distance.argmin(1),distance.min(1)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();result={}
    for run in a.runs:
        m=json.loads((run/'manifest.json').read_text());c=m['config'];families=audited_families(c)
        if c['arm'] not in ('aligned_teacher','pca_teacher'):raise ValueError('teacher-trained frame required')
        frame='aligned' if c['arm']=='aligned_teacher' else 'pca';name=c['arm']+'_'+c.get('label_distribution','empirical')
        label_path=Path(c['label_manifest']).parent/'labels.h5'
        if sha(label_path)!=json.loads(Path(c['label_manifest']).read_text())['labels_sha256']:raise ValueError('teacher latent arrays changed')
        with h5py.File(label_path) as labels:
            for step in (0,500,2000):
                rows=[r for r in m['scores'] if r['step']==step and r['guidance']==1]
                if len(rows)!=32 or {r['target_id'] for r in rows}!=set(families):raise ValueError('complete CFG1 evaluation required')
                values=[]
                with h5py.File(run/f'evaluation_{step}.h5') as predictions:
                    for r in rows:
                        ident=r['target_id'];g=labels[ident];state=json.loads(g.attrs['state_definition']);clusters=np.asarray(state['clusters']);bank=g['teacher_z_'+frame][:][state['teacher_indices']]
                        control,errors=nearest(bank,bank)
                        if not np.array_equal(clusters[control],clusters) or errors.max()!=0:raise ValueError('teacher self-assignment failed')
                        z=predictions[ident]['cfg1/z'][:];idx,errors=nearest(z,bank);latent=clusters[idx];decoded=np.asarray(r['assignments']);states=int(state['states']);rare=np.flatnonzero(np.bincount(clusters)==1)
                        if len(z)!=32 or len(decoded)!=32:raise ValueError('incomplete sample coverage')
                        latent_hits=set(latent);decoded_hits=set(decoded)-{-1}
                        values.append(dict(target=ident,latent_recall=len(latent_hits)/states,decoded_recall=len(decoded_hits)/states,agreement=float(np.mean(latent==decoded)),mean_nearest_rmse=float(errors.mean()),rare_states=len(rare),latent_rare_hits=sum(i in latent_hits for i in rare),decoded_rare_hits=sum(i in decoded_hits for i in rare),rare_latent_only=sum(i in latent_hits and i not in decoded_hits for i in rare),rare_decoded_only=sum(i not in latent_hits and i in decoded_hits for i in rare)))
                result[f'{name}_{step}']=dict(frame=frame,targets=values,summary={**{k:float(np.mean([r[k] for r in values])) for k in ('latent_recall','decoded_recall','agreement','mean_nearest_rmse')},**{k:sum(r[k] for r in values) for k in ('rare_states','latent_rare_hits','decoded_rare_hits','rare_latent_only','rare_decoded_only')}})
    lines=['# Latent identity versus decoded state diagnostic','',
           'Primary CFG1; same32 training proteins and generated samples. Each model is compared with teacher latents in its own training frame. Latent identity is a permissive nearest-label assignment with no distance or validity threshold; it is not a valid-state hit or a substitute for structural evaluation. Coordinate pose can dominate latent distance, including for the same decoded shape. Consequently latent recalls cannot establish decoder causality or be compared across frames as quality scores. Teacher self-assignment is checked in each frame.','',
           '| Model / update | Latent nearest-label recall | Decoded valid recall | Identity agreement | Latent nearest RMSE | Latent singleton hits | Decoded singleton hits | Latent-only singletons | Decoded-only singletons |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for key,value in result.items():
        r=value['summary'];lines.append(f"| {key} | {r['latent_recall']:.5f} | {r['decoded_recall']:.5f} | {r['agreement']:.5f} | {r['mean_nearest_rmse']:.5f} | {r['latent_rare_hits']}/{r['rare_states']} | {r['decoded_rare_hits']}/{r['rare_states']} | {r['rare_latent_only']} | {r['rare_decoded_only']} |")
    lines+=['','A state missing among32 samples has not been shown to have zero model probability. For a specified state with zero hits in32 independent draws, the exact one-sided95% upper bound is about0.0894, which exceeds the empirical singleton prior1/16. More samples would be needed to separate extremely low probability from zero. The matched32-sample coverage loss remains the relevant efficiency failure.']
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
