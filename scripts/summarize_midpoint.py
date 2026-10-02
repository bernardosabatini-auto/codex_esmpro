"""Paired quality gates for an inference-only solver comparison."""
import argparse,json
from pathlib import Path
import numpy as np
from latentfold.teacher_states import paired_change
from latentfold.flow import sampling_name
from prepare_overfit import sha
from summarize_comparison import hardware


def cross_hardware_quality(m,families):
    """Full paired quality and structural agreement, not exact score identity."""
    c=m['config'];ref=c['cross_hardware_reference']
    if sha(ref['manifest'])!=ref['manifest_sha256']:raise ValueError('hardware reference changed')
    prior=json.loads(Path(ref['manifest']).read_text())
    if prior['status']!='complete' or prior['checkpoint_sha256']!=m['checkpoint_sha256'] or prior['config']['selection_sha256']!=c['selection_sha256'] or prior['config']['evaluation_seed']!=c['evaluation_seed']:raise ValueError('incompatible hardware reference')
    baseline={(r['target_id'],r['sample']):r for r in prior['scores'] if r['setting']=='euler_25_cfg2'}
    current={(r['target_id'],r['sample']):r for r in m['scores'] if r['setting']=='euler_25_cfg2'}
    controls=m['cross_hardware_controls'];expected={(i,k) for i in families for k in range(3)}
    if set(baseline)!=expected or set(current)!=expected or len(controls)!=192 or {(r['target_id'],r['sample']) for r in controls}!=expected:raise ValueError('incomplete hardware comparison')
    if any(not np.isfinite(r[k]) for r in controls for k in ('ca_rmsd','ca_lddt')):raise ValueError('nonfinite hardware controls')
    metrics={key:paired_change({i:np.mean([current[i,k][key] for k in range(3)]) for i in families},{i:np.mean([baseline[i,k][key] for k in range(3)]) for i in families},families=families) for key in ('ca_lddt','coarse_valid')}
    agreement=all(r['ca_rmsd']<=.2 and r['ca_lddt']>=.99 for r in controls)
    return dict(metrics=metrics,max_ca_rmsd=max(r['ca_rmsd'] for r in controls),minimum_pair_ca_lddt=min(r['ca_lddt'] for r in controls),structural_agreement=agreement,passed=bool(agreement and metrics['ca_lddt']['ci95'][0]>-.005 and metrics['coarse_valid']['difference']>=-.01))


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0];path=run/'manifest.json'
    m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest');d=dict(status=m['status'],summaries={})
    if m['status']=='complete':
        c=m['config']
        if sha(c['selection'])!=c['selection_sha256'] or sha(c['protocol'])!=c['protocol_sha256']:raise ValueError('changed screen protocol')
        rows=json.loads(Path(c['selection']).read_text())['tuning'];families={r['id']:r['family'] for r in rows};settings=json.loads(Path(c['protocol']).read_text())['settings']
        if len(families)!=64 or len(set(families.values()))!=64 or len(m['scores'])!=len(settings)*192 or len(m['controls'])!=len(settings)*4 or m['training_updates_executed']!=0:raise ValueError('incomplete solver screen')
        def scores(name):
            values=[r for r in m['scores'] if r['setting']==name]
            if len(values)!=192 or {r['target_id'] for r in values}!=set(families) or any(sorted(r['sample'] for r in values if r['target_id']==i)!=[0,1,2] for i in families):raise ValueError('incomplete setting')
            return {k:{i:float(np.mean([r[k] for r in values if r['target_id']==i])) for i in families} for k in ('ca_lddt','coarse_valid')}
        expected_controls={(sampling_name(s),length) for s in settings for length in (128,256,384,512)}
        if {(r['setting'],r['length']) for r in m['controls']}!=expected_controls or any(not np.isfinite(r['ca_rmsd']) or not np.isfinite(r['ca_lddt']) or r['ca_rmsd']>.2 or r['ca_lddt']<.99 for r in m['controls']):raise ValueError('missing or failed batching controls')
        if any(not np.isfinite(r[k]) for r in m['scores'] for k in ('ca_lddt','coarse_valid')):raise ValueError('nonfinite quality scores')
        baseline=scores('euler_25_cfg2')
        for setting in settings:
            name=sampling_name(setting);values=scores(name)
            comparisons={k:paired_change(values[k],baseline[k],families=families) for k in values}
            nfe=setting['steps']*(2 if setting['solver']=='midpoint' else 1)
            d['summaries'][name]=dict(**setting,velocity_evaluations=nfe,network_forwards=nfe*(2 if setting['guidance']!=1 else 1),metrics=comparisons,passed=bool(comparisons['ca_lddt']['ci95'][0]>-.005 and comparisons['coarse_valid']['difference']>=-.01),measured_batch_seconds=sum(r['seconds'] for r in m['batches'] if r['setting']==name))
        d['max_reserved_gib']=max(r['peak_reserved_bytes'] for r in m['batches'])/1024**3
        if c.get('cross_hardware_reference'):d['cross_hardware']=cross_hardware_quality(m,families)
        try:d['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as error:d['hardware']=dict(status='unavailable',error=str(error))
    else:d['error']=m.get('error','Incomplete solver screen')
    lines=['# Inference-only numerical-solver screen','',f"Status: {d['status']}.",'',
           'Same original weights,64 tuning families,three paired seeds,strict FP32 and3-step decoding. References are AFDB predictions. Euler25 CFG2 must reproduce the earlier baseline. All settings and geometry failures remain included.','',
           '| Setting | Velocity evaluations | Network forwards | CA-lDDT | Delta | Paired 95% interval | Valid fraction | Validity delta | Gate |',
           '|---|---:|---:|---:|---:|---|---:|---:|---|']
    for name,r in d['summaries'].items():
        ca=r['metrics']['ca_lddt'];v=r['metrics']['coarse_valid'];lines.append(f"| {name} | {r['velocity_evaluations']} | {r['network_forwards']} | {ca['candidate']:.5f} | {ca['difference']:+.5f} | {ca['ci95']} | {v['candidate']:.5f} | {v['difference']:+.5f} | {r['passed']} |")
    if 'error' in d:lines+=['',d['error']]
    if 'cross_hardware' in d:
        r=d['cross_hardware'];ca=r['metrics']['ca_lddt'];v=r['metrics']['coarse_valid']
        lines+=['','This is a cross-hardware qualification, not an exact-score reproduction pass. The preceding solver table compares this run with itself and is not its hardware gate.',f"Against the frozen H200 outputs: maximum paired CA-RMSD{r['max_ca_rmsd']:.6f}A, minimum paired CA-lDDT{r['minimum_pair_ca_lddt']:.6f}; reference CA-lDDT delta{ca['difference']:+.6f},95% interval{ca['ci95']}; validity delta{v['difference']:+.6f}. All192 structural controls plus the existing quality margins passed: {r['passed']}.",'The earlier strict1e-6 score-identity failure remains a failure. This separate analysis uses the preexisting0.2A/0.99 structural agreement and-0.005/-0.01 reference-quality margins; it does not establish training or latency equivalence.']
        lines[4]='Same original weights,64 tuning families,three paired seeds,strict FP32 and3-step decoding. References are AFDB predictions. Cross-hardware differences are fully assessed below. All settings and geometry failures remain included.'
    lines+=['','Intervals are unadjusted family bootstraps. Nominal evaluation savings are not measured end-to-end speedups. Passing this screen only permits ensemble quality/diversity and matched resident-latency tests.']
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
