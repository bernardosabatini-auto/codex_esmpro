"""Audit cheap sequence ranking against measured refolds, with family clustering."""
import argparse,json,re
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
from prepare_overfit import sha
from summarize_fragment_training import interval


def analyze(runs,reports):
    records=[];sources=[]
    for run,report in zip(runs,reports):
        d=json.loads(report.read_text());m=json.loads((run/'manifest.json').read_text())
        if d['status']!='complete' or not d['interpretation_qualified'] or d['manifest_sha256']!=sha(run/'manifest.json'):raise ValueError('Audited complete assay required')
        sources.append(dict(run=str(run),report_sha256=sha(report),manifest_sha256=sha(run/'manifest.json')))
        for r in d['backbones']:
            if r['mode']!='conditioned':continue
            path=run/'mpnn/seqs'/f"{r['name']}.fa";lines=path.read_text().splitlines();seqs=[]
            for index,line in enumerate(lines):
                if not line.startswith('>T='):continue
                vals=dict(x.strip().split('=',1) for x in line[1:].split(','));slot=int(vals['sample'])-1;sequence=lines[index+1]
                if sequence!=m['sequences'][r['name']][slot]:raise ValueError('MPNN sequence order differs')
                seqs.append(dict(slot=slot,score=float(vals['score']),global_score=float(vals['global_score']),**r['refolds'][slot]))
            if len(seqs)!=8 or {x['slot'] for x in seqs}!=set(range(8)):raise ValueError('Incomplete score coverage')
            within=float(spearmanr([-x['global_score'] for x in seqs],[x['sc_tm'] for x in seqs]).statistic)
            def valid_global(x):return bool(r['raw']['coarse_valid'] and x['coarse_valid'] and x['sc_tm']>.5)
            def joint_final(x):return bool(x['coarse_valid'] and x['sc_tm']>.5 and x['motif_drms']<=1 and x['motif_ca_rmsd']<=1)
            selections={kind:min(seqs,key=lambda x:x[key]) for kind,key in [('first','slot'),('mpnn_global','global_score'),('mpnn_designed','score')]};selections['oracle_global']=max(seqs,key=lambda x:x['sc_tm'])
            records.append(dict(arm=d['arm'],target_id=r['target_id'],family=r['family'],slot=r['slot'],score_file_sha256=sha(path),within_backbone_spearman=within if np.isfinite(within) else None,any_valid_global=any(valid_global(x) for x in seqs),any_joint_final=any(joint_final(x) for x in seqs),any_strict=r['strict_joint_success'],selection={kind:dict(sequence_index=x['slot'],sc_tm=x['sc_tm'],valid_global=valid_global(x),joint_final=joint_final(x),strict_joint=bool(r['raw_gate_passed'] and joint_final(x))) for kind,x in selections.items()}))
    families=sorted({r['family'] for r in records});summary=[]
    for arm in sorted({r['arm'] for r in records})+['all_arms']:
        rr=[r for r in records if arm=='all_arms' or r['arm']==arm];summary.append(dict(arm=arm,backbones=len(rr),mean_within_backbone_spearman=float(np.mean([r['within_backbone_spearman'] for r in rr if r['within_backbone_spearman'] is not None])),any_valid_global=sum(r['any_valid_global'] for r in rr),any_joint_final=sum(r['any_joint_final'] for r in rr),strict=sum(r['any_strict'] for r in rr),selectors={kind:dict(mean_sc_tm=float(np.mean([r['selection'][kind]['sc_tm'] for r in rr])),valid_global=sum(r['selection'][kind]['valid_global'] for r in rr),joint_final=sum(r['selection'][kind]['joint_final'] for r in rr)) for kind in ('first','mpnn_global','mpnn_designed','oracle_global')}))
    comparisons=[]
    for metric in ('sc_tm','valid_global','joint_final'):
        delta=[np.mean([float(r['selection']['mpnn_global'][metric])-float(r['selection']['first'][metric]) for r in records if r['family']==family]) for family in families];comparisons.append(dict(metric=metric,global_score_minus_first=interval(delta)))
    return dict(status='complete',interpretation='Exploratory development diagnostic; three model arms share four families. Sequence ranking costs8MPNN designs but only1refold; oracle requires8refolds and is not deployable. Joint final counts can include sequence-driven motif repair when raw motif failed, so are NOT retention successes. Strict gates unchanged.',sources=sources,summaries=summary,comparisons=comparisons,records=records)


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--reports',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if len(a.runs)!=len(a.reports):raise ValueError('Each run needs a report')
    d=analyze(a.runs,a.reports);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');view={k:v for k,v in d.items() if k!='records'};a.output.with_suffix('.md').write_text('# ProteinMPNN score diagnostic\n\n'+d['interpretation']+'\n\n```json\n'+json.dumps(view,indent=2)+'\n```\n');print(json.dumps(view,indent=2))

if __name__=='__main__':main()
