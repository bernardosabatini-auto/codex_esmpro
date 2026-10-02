"""Certify the complete expanded label universe without reconstruction filtering."""
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
import h5py,numpy as np
from expansion_data import reconstruction_summary,capacity_ids
from prepare_overfit import sha
from summarize_expansion_data import summarize


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runs',type=Path,nargs=5,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    oldpath=root/'runs/reliable122_inventory.json';old=json.loads(oldpath.read_text());certificate_path=root/'reports/reliable122_reconstruction_bounds.json';cert=json.loads(certificate_path.read_text())
    if cert['status']!='complete' or not cert['reconstruction_gate_passed'] or cert['inventory_sha256']!=sha(oldpath) or sha(cert['audit'])!=cert['audit_sha256'] or len(old['targets'])!=122:raise ValueError('old122 certificate changed')
    if sha(old['selection'])!=old['selection_sha256']:raise ValueError('old family split changed')
    manifests=[json.loads((path/'manifest.json').read_text()) for path in a.runs]
    profiles=[i for i,m in enumerate(manifests) if m['config']['phase']=='profile']
    if len(profiles)!=1 or {m['config'].get('shard') for m in manifests if m['config']['phase']=='expansion'}!={0,1,2,3}:raise ValueError('expected one profile and four complete shards')
    profile=a.runs[profiles[0]]/'manifest.json';source=manifests[profiles[0]]['config'];selection=json.loads(Path(source['selection']).read_text());candidates={r['id']:r for r in selection['train']}
    if len(candidates)!=1383 or sha(source['selection'])!=source['selection_sha256']:raise ValueError('candidate selection changed')
    seen=set();new=[];audits=[];sources=[];controls=[]
    for path,m in zip(a.runs,manifests):
        c=m['config'];report=summarize(m)
        if not report['generation_qualified']:raise ValueError('unqualified generation shard')
        for key in ('selection','source_audit','native_manifest','native_backbones','protocol'):
            if c[key+'_sha256']!=source[key+'_sha256'] or sha(c[key])!=c[key+'_sha256']:raise ValueError('mismatched source identity')
        if c['phase']=='expansion' and (Path(c['profile_manifest']).resolve()!=profile.resolve() or c['profile_manifest_sha256']!=sha(profile)):raise ValueError('wrong qualifying profile')
        for key in ('labels','embeddings'):
            if sha(path/(key+'.h5'))!=m[key+'_sha256']:raise ValueError('generated arrays changed')
        expected={r['id'] for r in c['targets']};records=[r for r in m['records'] if not r['control']]
        if expected!={r['id'] for r in records} or seen&expected:raise ValueError('missing or repeated new families')
        seen|=expected;audits.extend(records)
        sources.append(dict(manifest=str((path/'manifest.json').resolve()),manifest_sha256=sha(path/'manifest.json'),labels_sha256=m['labels_sha256'],embeddings_sha256=m['embeddings_sha256']))
        controls.append(dict(manifest=str(path),counts=report['control_counts']))
        for r in records:
            if not r['eligible']:continue
            row=dict(candidates[r['id']],source_labels=str((path/'labels.h5').resolve()),source_labels_sha256=m['labels_sha256'],embedding_cache=str((path/'embeddings.h5').resolve()),state_definition=r['state_definition'],mean_teacher_confidence=r['mean_teacher_confidence'],cohort='new')
            new.append(row)
    if seen!=set(candidates):raise ValueError('incomplete1383-family generation')
    newaudit=reconstruction_summary(audits)
    if not newaudit['targets']:raise ValueError('no eligible new families')
    targets=[dict(r,embedding_cache=old['embedding_cache'],cohort='original122') for r in old['targets']]+new
    if len({r['id'] for r in targets})!=len(targets) or len({r['family'] for r in targets})!=len(targets):raise ValueError('old/new family overlap')
    for path,expected in {(r['source_labels'],r['source_labels_sha256']) for r in old['targets']}:
        if sha(path)!=expected:raise ValueError('original122 label arrays changed')
    # Validate actual training tensors, including exact inherited reference_z.
    caches={};labels={}
    try:
        inherited=h5py.File(selection['dataset']);caches['inherited']=inherited
        for r in targets:
            ep=r['embedding_cache'];lp=r['source_labels']
            if ep not in caches:caches[ep]=h5py.File(ep)
            if lp not in labels:labels[lp]=h5py.File(lp)
            e=caches[ep]['train'][r['id']];g=labels[lp][r['id']];n=r['length'];value=e['80'][:]
            if e.attrs['sequence_sha256']!=r['sequence_sha256'] or g.attrs['sequence_sha256']!=r['sequence_sha256'] or value.shape!=(n,2560) or value.dtype!=np.float32 or not np.isfinite(value).all():raise ValueError('embedding/label identity mismatch')
            r['embedding_array_sha256']=hashlib.sha256(value.tobytes()).hexdigest()
            if not np.array_equal(g['reference_z'][:],inherited['train'][r['id']]['z'][:]):raise ValueError('cached reference_z changed')
            if g['teacher_z'].shape!=(16,n,8) or g['teacher_backbone'].shape!=(16,n,4,3) or not np.array_equal(np.flatnonzero(g['coarse_valid'][:]),r['state_definition']['teacher_indices']):raise ValueError('label/state mismatch')
            if not np.isfinite(g['teacher_z'][:]).all() or not np.isfinite(g['teacher_backbone'][:]).all():raise ValueError('nonfinite training label')
    finally:
        for handle in list(caches.values())+list(labels.values()):handle.close()
    combined={};count=len(targets);oldsummary=cert['summary']['all']
    for prior in ('empirical','balanced'):
        combined[prior]=dict(ca_lddt_lower=(122*oldsummary['ca_lddt_lower']+len(new)*newaudit['priors'][prior]['ca_lddt'])/count,validity_lower=(122*oldsummary['validity_lower'][prior]+len(new)*newaudit['priors'][prior]['valid'])/count)
    passed=newaudit['gate_passed'] and all(v['ca_lddt_lower']>=.98 and v['validity_lower']>=.99 for v in combined.values())
    # Fixed training panel: original32 plus32 new, length-stratified and ID
    # ordered. Sparse strata contribute all eligible IDs, then other strata fill.
    panel=list(old['capacity_ids'])+capacity_ids(new)
    d=dict(status='complete',reconstruction_gate_passed=bool(passed),targets=targets,evaluation_ids=panel,new_reconstruction=newaudit,combined_reconstruction_lower=combined,bucket_counts=dict(Counter(r['bucket'] for r in targets)),source_shards=sources,selection=source['selection'],selection_sha256=source['selection_sha256'],old_inventory=str(oldpath),old_inventory_sha256=sha(oldpath),old_reconstruction_certificate=str(certificate_path),old_reconstruction_certificate_sha256=sha(certificate_path),protocol=source['protocol'],protocol_sha256=source['protocol_sha256'],scope='All metadata-eligible new labels plus unchanged122. Every family is training data. Fixed64-family capacity panel is not a held-out test. No reconstruction-outcome filtering; fail the entire corpus if certificate fails.')
    a.output.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(dict(targets=count,new=len(new),buckets=d['bucket_counts'],reconstruction_gate_passed=bool(passed),panel=len(panel),new_reconstruction=newaudit,combined_reconstruction=combined)))


if __name__=='__main__':main()
