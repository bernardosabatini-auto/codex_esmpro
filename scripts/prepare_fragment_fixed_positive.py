"""Experimental positive controls with only native motif amino acids supplied."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha


def audit_inputs(c):
    for key in ('generation_manifest','predictions','protocol','usalign','baseline_report','reference_predictions','fragments'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    baseline=json.loads(Path(c['generation_manifest']).read_text());report=json.loads(Path(c['baseline_report']).read_text());old=baseline['config'];expected={r['target_id']:r for r in old['entries'] if r['head']=='experimental'}
    if baseline['status']!='complete' or report['status']!='complete' or not report['positive_controls_passed'] or report['manifest_sha256']!=c['generation_manifest_sha256'] or len(c['entries'])!=4 or {r['target_id'] for r in c['entries']}!=set(expected):raise ValueError('Invalid control lineage/coverage')
    for key in ('num_sequences','temperature','mpnn_seed','seed','mpnn','dependencies','teacher_artifacts','precision','usalign_sha256'):
        if c[key]!=old[key]:raise ValueError('Changed control recipe')
    with h5py.File(c['predictions']) as f,h5py.File(c['reference_predictions']) as refs,h5py.File(c['fragments']) as fragments:
        for r in c['entries']:
            ident=r['target_id'];q=fragments['development/'+ident+'/conditions/f30_center'];old=expected[ident]
            if r['head']!='experimental_fixed' or r['mode']!='fixed_positive' or r['slot']!=0 or not r['repeatability_control'] or r['length']!=old['length'] or r['family']!=old['family'] or r['fixed_start']!=int(q.attrs['start']) or r['fixed_sequence']!=q.attrs['sequence']:raise ValueError('Invalid fixed positive')
            if not np.array_equal(f[r['dataset']][0],refs[old['dataset']][:]) or not np.array_equal(f['motifs/'+ident][:],q['fragment'][:]):raise ValueError('Experimental coordinates/motif changed')


def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];manifest=a.baseline/'manifest.json';m=json.loads(manifest.read_text());old=m['config'];c={k:old[k] for k in ('num_sequences','temperature','mpnn_seed','seed','mpnn','dependencies','teacher_artifacts','precision','usalign','usalign_sha256')};entries=[];inputs=a.output.with_suffix('.h5')
    with h5py.File(inputs,'x') as out,h5py.File(old['predictions']) as src,h5py.File(old['fragments']) as fragments:
        for r in old['entries']:
            if r['head']!='experimental':continue
            ident=r['target_id'];q=fragments['development/'+ident+'/conditions/f30_center'];dataset='positive/'+ident;out.create_dataset(dataset,data=src[r['dataset']][:][None]);out.create_dataset('motifs/'+ident,data=q['fragment'][:]);entries.append(dict(r,head='experimental_fixed',mode='fixed_positive',dataset=dataset,slot=0,fixed_start=int(q.attrs['start']),fixed_sequence=str(q.attrs['sequence']),repeatability_control=True))
    c.update(assay='fragment_fixed_positive',entries=entries,work_cap_seconds=480)
    for key,path in [('generation_manifest',manifest),('predictions',inputs),('protocol',root/'configs/fragment_fixed_positive_protocol.json'),('baseline_report',a.report),('reference_predictions',Path(old['predictions'])),('fragments',Path(old['fragments']))]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
    audit_inputs(c);a.output.write_text(json.dumps(c,indent=2)+'\n');print('Prepared4fixed-fragment experimental controls,32refolds')

if __name__=='__main__':main()
