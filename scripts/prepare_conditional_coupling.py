"""Bind matched coupling arms to the existing audited32-protein corpus."""
import argparse,copy,json,math
from pathlib import Path
from prepare_overfit import sha


def main():
 p=argparse.ArgumentParser();p.add_argument('--profile',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/conditional_coupling_protocol.json';r=json.loads(protocol.read_text());old=json.loads((root/'runs/overfit_49718446/manifest.json').read_text())['config'];c=copy.deepcopy(old)
 c.update(seed=r['seed'],evaluation_seed=r['evaluation_seed'],evaluation_guidance=[1],updates=500,evaluation_steps=[500],work_cap_seconds=1680,maximum_profile_gib=75,profile_only=False,coupling_protocol=str(protocol),coupling_protocol_sha256=sha(protocol))
 for key in ('label_manifest','followup_protocol'):
  if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
 if a.profile is None:
  c.update(updates=40,evaluation_steps=[40],profile_only=True,work_cap_seconds=480,conditional_coupling=dict(group_size=8,arm='optimal'));c.pop('profile_report',None);c.pop('profile_report_sha256',None);a.output.write_text(json.dumps(c,indent=2)+'\n')
 else:
  d=json.loads(a.profile.read_text())
  if d['status']!='complete' or not d['profile_only'] or d['max_reserved_gib']>75 or d['conditional_coupling']['complete_updates']!=40:raise ValueError('Resource profile failed')
  estimate=d['training_seconds']/40*500+240+max(60,d['elapsed_seconds']-d['training_seconds']);minutes=max(10,math.ceil((estimate*1.15+60)/60));c.update(profile_report=str(a.profile.resolve()),profile_report_sha256=sha(a.profile),work_cap_seconds=minutes*60-60)
  for arm in r['arms']:
   c['conditional_coupling']=dict(group_size=8,arm=arm);a.output.with_name(a.output.stem+'_'+arm+'.json').write_text(json.dumps(c,indent=2)+'\n')
  print('Measured allocation minutes',minutes,'estimated full seconds',estimate)
 print('Prepared coupling profile' if a.profile is None else 'Prepared both matched500update arms')
if __name__=='__main__':main()
