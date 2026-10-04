"""Bound bridge training, unchanged parent coordinates and fixed-state audits."""
import json
from pathlib import Path
import h5py,numpy as np,torch
from extra_fragment_validation_core import load_conditions
from fragment_junction_core import DRAW_KEYS
from latentfold.fragment_inpainting import place_fragment,context_mask
from latentfold.scaffold_bridge import coordinate_known,scaffold_anchors
from prepare_overfit import sha


def audit_sources(c):
    bs=json.loads(Path(c['bridge_protocol']).read_text());m=json.loads(Path(c['bridge_previous_manifest']).read_text())
    d=json.loads(Path(c['bridge_previous_report']).read_text());r=json.loads(Path(c['bridge_reachability']).read_text())
    if (bs!=c['bridge_spec'] or bs['context_flank']!=8 or c['context_flank']!=8
            or Path(c['bridge_previous_manifest']).parent.name!=bs['failed_predecessor']
            or m['status']!='complete' or d['status']!='complete' or d['profile_only'] or d['qualified']
            or not d['flank_context'] or not d['numerically_qualified'] or d['manifest_sha256']!=sha(c['bridge_previous_manifest'])
            or any(s['refold_eligible_geometry']!=0 for s in d['closure_summary'])
            or r['status']!='complete' or r['width']!=8 or r['summary'][0]['any_proven_obstruction']!=15
            or r['summary'][1]['any_proven_obstruction']!=0 or r['source_manifest_sha256']!=sha(c['flank_baseline_manifest'])
            or r['source_predictions_sha256']!=sha(c['flank_baseline_predictions'])
            or any(c[k]!=m['config'][k] for k in ('spec','protocol','selected','training_ids','fragments','decoder_checkpoint',
                    'baseline_manifest','baseline_predictions','diagnostic_manifest','diagnostic_predictions','junction_loss','context_flank'))):
        raise ValueError('Unbound failed wider-mask predecessor or bridge prerequisites')
    bound={r['path'] for r in c['sources']}
    if any(v not in bound for k,v in c.items() if k.startswith('bridge_') and k!='bridge_spec'):raise ValueError('Unbound bridge source')
    if not c['profile_only']:
        p=json.loads(Path(c['profile_report']).read_text())
        if not p.get('scaffold_bridge') or p['bridge_protocol_sha256']!=sha(c['bridge_protocol']):raise ValueError('Matching bridge profile required')


def augment_report(d,run,m):
    c=m['config'];before=json.loads(Path(c['bridge_previous_manifest']).read_text())
    if any(a[k]!=b[k] for a,b in zip(m['training'],before['training']) for k in DRAW_KEYS):raise ValueError('Bridge/wider-mask draws differ')
    ids=sorted({r['target_id'] for r in d['records']});items=load_conditions(c['fragments'],ids,'c20_center',cohort='train')
    checks=m['bridge_state_audits']
    if len(checks)!=10*len(ids)+10 or any(r['states']!=4 or r['known_max_abs_nm']>1e-5 or r['center_max_abs_nm']>1e-5 for r in checks):
        raise ValueError('Incomplete runtime fixed-state checks')
    max_fixed=0.;fixed_groups=0
    with h5py.File(run/'predictions.h5') as f,h5py.File(run/'initial_masked.h5') as initial,h5py.File(run/'flank_closed.h5') as closed:
        for ident in ids:
            keep=items[ident]['keep'][None].expand(4,-1);hole=context_mask(keep,8).numpy()
            for kind,parent in (('generated','parent'),('native','native_direct')):
                reference=f[parent+'/'+ident+'/backbone'][:];fragment=torch.from_numpy(items[ident]['fragment'])
                desired=place_fragment(fragment,torch.from_numpy(reference),items[ident]['start'])
                anchors=scaffold_anchors(torch.from_numpy(reference),desired,keep).numpy()
                for suffix in ('initial','cond','null','untrained'):
                    dropped=torch.full((4,),suffix=='null',dtype=torch.bool);known=coordinate_known(keep,dropped).numpy()
                    actual=initial[kind+'/'+ident+'/clamped_backbone'][:] if suffix=='initial' else f[kind+'_'+suffix+'/'+ident+'/backbone'][:]
                    expected=np.where(known[...,None,None],anchors,0)
                    if suffix in ('initial','cond','null'):
                        g=initial[kind+'/'+ident] if suffix=='initial' else f[kind+'_'+suffix+'/'+ident]
                        if not np.array_equal(g['coordinate_known'][:],known) or np.max(np.abs(g['anchors'][:]-expected))>1e-5:
                            raise ValueError('Changed saved coordinate-known mask or scaffold/fragment anchors')
                    error=float(np.max(np.abs(actual[known]-expected[known])));max_fixed=max(max_fixed,error)
                    if error>1e-4:raise ValueError('Motif or far scaffold moved')
                    fixed_groups+=1
                    if kind=='generated' and suffix in ('cond','untrained'):
                        repaired=np.stack([closed[kind+'_'+suffix+'/'+ident+'/'+str(k)][:] for k in range(4)])
                        if not np.array_equal(repaired[known],actual[known]):raise ValueError('CPU closure changed fixed bridge atoms')
                # Only the16flank residues are free in the conditional path.
                if not np.array_equal(~coordinate_known(keep,torch.zeros(4,dtype=torch.bool)).numpy(),hole&~keep.numpy()):
                    raise ValueError('Changed bridge degree of freedom')
    d.update(scaffold_bridge=True,bridge_protocol_sha256=sha(c['bridge_protocol']),bridge_fixed_groups=fixed_groups,
             bridge_fixed_max_abs_angstrom=max_fixed,bridge_runtime_calls=len(checks),paired_wider_mask_updates=len(m['training']))
    d['scope']='Training-only fixed-scaffold bridge flow: original generated far scaffold and requested20residue motif held fixed; eight-residue flanks on each side generated. Native context is oracle-only. Every case,including15proven-obstructed generated pairs,retained. Same2000draws as wider-mask predecessor. Complete geometry/hidden-edge gate licenses separate full matched refolding only; no designability claim from imposed anchors or raw geometry.'
    return d
