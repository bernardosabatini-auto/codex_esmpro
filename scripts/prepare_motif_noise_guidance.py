"""Freeze motif-only selection of the best existing random start for each case."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha
from summarize_noise_guidance import analyze
from summarize_isolated_motif import analyze as fragment_audit
from latentfold.fragment_designability import motif_error


def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];parent=root/'runs/noise_guidance_49863415';fragments=root/'runs/isolated_motif_49864561'
 if analyze(parent)['status']!='complete' or fragment_audit(fragments)['status']!='complete':raise ValueError('Invalid parents')
 m=json.loads((parent/'manifest.json').read_text());old=m['config'];c={k:old[k] for k in ('target_ids','samples','generation_seed','search_seed','steps','max_updates','line_search_steps','finite_difference_eps','random_samples','random_batch')};c.update(work_cap_seconds=780,choices=[])
 rows={r['target_id']:r for r in json.loads(Path(old['selection']).read_text())['rows']}
 with h5py.File(parent/'predictions.h5') as f,h5py.File(fragments/'predictions.h5') as frag:
  for ident in c['target_ids']:
   n=rows[ident]['length'];k=max(8,int(.3*n));st=(n-k)//2;mask=np.zeros(n,bool);mask[st:st+k]=True;ref=np.zeros((n,4,3),np.float32);ref[st:st+k]=frag[ident+'/fragment'][:]
   for slot in range(2):
    tick=time.perf_counter();errors=motif_error(f[f'{ident}/{slot}/random_all'][:],ref,mask);record=next(r for r in m['cases'] if (r['target_id'],r['slot'])==(ident,slot));choice=int(errors.argmin());c['choices'].append(dict(target_id=ident,slot=slot,index=choice,motif_drms=float(errors[choice]),selection_cpu_seconds=time.perf_counter()-tick,search_seconds=record['initial_seconds']+record['random_seconds']))
 for key,path in [('protocol',root/'configs/motif_noise_guidance_protocol.json'),('parent_manifest',parent/'manifest.json'),('parent_predictions',parent/'predictions.h5'),('fragment_manifest',fragments/'manifest.json'),('fragment_predictions',fragments/'predictions.h5'),('selection',Path(old['selection'])),('checkpoint',Path(old['checkpoint'])),('decoder_checkpoint',Path(old['decoder_checkpoint']))]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
 a.output.write_text(json.dumps(c,indent=2)+'\n');print('Frozen8motif-only best random starts')
if __name__=='__main__':main()
