"""Complete the declared four-cell diagnostic, including peptide failure modes."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha
from summarize_generative_pilot import analyze
from latentfold.ensemble_metrics import backbone_geometry


def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--crossover',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();manifests=[]
    for run in (a.parent,a.crossover):
        if analyze(run)['status']!='complete':raise ValueError('Incomplete generation')
        manifests.append(json.loads((run/'manifest.json').read_text()))
    old,new=manifests;c,d=old['config'],new['config']
    if d['parent_manifest_sha256']!=sha(a.parent/'manifest.json'):raise ValueError('Changed parent')
    for k in ('selection_sha256','panel_sha256','embedding_cache_sha256','decoder_checkpoint_sha256','samples','seed','modes','control_ids'):
        if c[k]!=d[k]:raise ValueError('Unmatched '+k)
    heads={h['name']:h for m in manifests for h in m['config']['heads']}
    if set(heads)!={'original50','original10','reflow50','reflow10'} or heads['original50']['checkpoint_sha256']!=heads['original10']['checkpoint_sha256'] or heads['reflow50']['checkpoint_sha256']!=heads['reflow10']['checkpoint_sha256']:raise ValueError('Unmatched weights/steps')
    records=old['records']+new['records'];comparisons=[]
    for mode in c['modes']:
        for candidate,reference in [('original10','original50'),('reflow10','reflow50'),('reflow50','original50'),('reflow10','original10')]:
            families=sorted({r['family'] for r in records});rng=np.random.default_rng(2026100213);ix=rng.integers(0,len(families),(20000,len(families)))
            for metric in ['coarse_valid']+(['motif_drms','motif_under1A'] if mode!='unconditional' else []):
                def mean(head,f):
                    rr=[r for r in records if (r['head'],r['mode'],r['family'])==(head,mode,f)]
                    return np.mean([r['motif_drms']<=1 if metric=='motif_under1A' else r[metric] for r in rr])
                delta=np.array([mean(candidate,f)-mean(reference,f) for f in families]);comparisons.append(dict(mode=mode,candidate=candidate,reference=reference,metric=metric,delta=float(delta.mean()),interval=np.quantile(delta[ix].mean(1),[.025,.975]).tolist()))
    geometry=[]
    for run,m in zip((a.parent,a.crossover),manifests):
        with h5py.File(run/'predictions.h5') as f:
            for h in m['config']['heads']:
                for mode in c['modes']:
                    groups=[backbone_geometry(f[h['name']+'/'+mode+'/'+ident+'/backbone'][:]) for ident in f[h['name']+'/'+mode]]
                    g={k:np.concatenate([r[k] for r in groups]) for k in groups[0]};ca_ok=(g['ca_clashing_residue_fraction']<=.01)&(g['ca_gap_fraction']<=.01)
                    geometry.append(dict(head=h['name'],mode=mode,outputs=len(ca_ok),ca_only_valid=float(ca_ok.mean()),full_coarse_valid=float(g['coarse_valid'].mean()),ca_valid_but_peptide_failed=int((ca_ok&~g['coarse_valid']).sum()),peptide_outlier_mean=float(g['peptide_outlier_fraction'].mean())))
    result=dict(status='complete',comparisons=comparisons,geometry=geometry,sources=[dict(manifest=str(r/'manifest.json'),sha256=sha(r/'manifest.json')) for r in (a.parent,a.crossover)])
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');lines=['# Weights versus integration steps in unconditional generation','','All16 development families/four seeds and all failures retained. Original50/reflow10 plus complementary original10/reflow50. Identical source encodings, noises, decoder and numerical controls. No designability qualification.','', '| Head | Mode | CA-only valid | Full coarse valid | CA-valid peptide failures /64 |','|---|---|---:|---:|---:|']
    for r in geometry:lines.append(f"| {r['head']} | {r['mode']} | {r['ca_only_valid']:.4f} | {r['full_coarse_valid']:.4f} | {r['ca_valid_but_peptide_failed']} |")
    lines+=['','Paired-family differences and95% intervals:']
    for r in comparisons:lines.append(f"- {r['mode']}, {r['candidate']} minus {r['reference']}, {r['metric']}: {r['delta']:+.4f} {r['interval']}.")
    lines+=['','CA-only validity omits peptide C-N distances and is not a substitute for the unchanged full-backbone validity gate. Geometry remains insufficient for designability. The conditional reflow training used zero condition dropout; this experiment tests its unconditional behavior explicitly.']
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
