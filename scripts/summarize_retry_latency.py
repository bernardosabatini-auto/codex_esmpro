"""Audit fixed-panel retry-inclusive timings and report paired speed ratios."""
import json
from pathlib import Path
import numpy as np
from prepare_overfit import sha
from summarize_ensemble_latency import speed_ratio


def analyze(m):
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error','Incomplete timing'))
    c=m['config'];kinds=['original','compact500','reflow10','teacher'];ids=c['target_ids']
    for key in ('protocol','panel','quality_report','previous_timing_manifest'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    if not json.loads(Path(c['quality_report']).read_text())['sampling_quality_gate_passed']:raise ValueError('Unqualified external result')
    expected={(k,i,n,r) for k in kinds for i in ids for n in (1,8,32) for r in range(3)};rows=m['rows'];controls=m['controls']
    if len(ids)!=8 or len(set(ids))!=8 or len(rows)!=288 or {(r['model'],r['target_id'],r['samples'],r['repeat']) for r in rows}!=expected:raise ValueError('Missing/duplicate timing records')
    if len(controls)!=32 or {(r['model'],r['target_id']) for r in controls}!={(k,i) for k in kinds for i in ids}:raise ValueError('Missing controls')
    for r in controls:
        teacher=r['model']=='teacher'
        if not np.isfinite(r['ca_rmsd']) or not np.isfinite(r['ca_lddt']) or r['ca_rmsd']>(.01 if teacher else .2) or r['ca_lddt']<(.999 if teacher else .99):raise ValueError('Failed output controls')
        if not teacher and (r['prefixes']!=[1,8,32] or not r['selected_indices_identical']):raise ValueError('Retry prefix control missing')
    for r in rows:
        if any(not np.isfinite(r[k]) or r[k]<=0 for k in ('seconds','peak_reserved_bytes')) or not r['samples']<=r['attempts']<=4*r['samples'] or not 0<=r['exhausted']<=r['samples']:raise ValueError('Invalid timing/accounting')
        if len(r['selected_draws'])!=r['samples'] or any(type(d) is not int or d not in [k+32*a for a in range(4)] for k,d in enumerate(r['selected_draws'])):raise ValueError('Wrong retry address')
    per={k:{str(n):{i:float(np.median([r['seconds'] for r in rows if (r['model'],r['target_id'],r['samples'])==(k,i,n)])) for i in ids} for n in (1,8,32)} for k in kinds}
    ratios={k:{str(n):speed_ratio(per[k][str(n)],per['reflow10'][str(n)]) for n in (1,8,32)} for k in kinds if k!='reflow10'}
    return dict(status='complete',scope=m['scope'],device_name=m['device_name'],protocol_sha256=c['protocol_sha256'],quality_report_sha256=c['quality_report_sha256'],per_target=per,means={k:{n:float(np.mean(list(v.values()))) for n,v in counts.items()} for k,counts in per.items()},paired_speedup=ratios,speed_thresholds_passed=bool(ratios['original']['32']['reference_seconds_over_candidate']>=2 and ratios['compact500']['32']['reference_seconds_over_candidate']>=1.25),max_reserved_gib={k:max(r['peak_reserved_bytes'] for r in rows if r['model']==k)/1024**3 for k in kinds},attempts_per_output={k:sum(r['attempts'] for r in rows if r['model']==k)/sum(r['samples'] for r in rows if r['model']==k) for k in kinds},exhausted={k:sum(r['exhausted'] for r in rows if r['model']==k) for k in kinds})


def summarize(m,output):
    d=analyze(m);output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');lines=['# Matched retry-inclusive sequence-to-backbone latency','',f"Status:{d['status']}."]
    if d['status']=='complete':
        lines+=['',d['scope'],'','Same eight development families, three repeats, rotating K1/8/32 order. Report average of each family median and paired-family bootstrap intervals. Raw teacher has no geometry rejection; student pipelines use the fixed four-attempt rule. This comparison does not equalize quality or diversity.','','| Pipeline | K1 seconds | K8 seconds | K32 seconds | Peak GiB | Attempts/output |','|---|---:|---:|---:|---:|---:|']
        for k,r in d['means'].items():lines.append(f"| {k} | {r['1']:.4f} | {r['8']:.4f} | {r['32']:.4f} | {d['max_reserved_gib'][k]:.2f} | {d['attempts_per_output'][k]:.5f} |")
        lines+=['','Ratios above one favor reflow10. All selected student output indices and geometry decisions match the audited external K32 prefixes. Timed repeats preserve the same decisions.','','| Comparator/reflow10 | K | Ratio |95% family interval |','|---|---:|---:|---|']
        for k,counts in d['paired_speedup'].items():
            for n,r in counts.items():lines.append(f"| {k} | {n} | {r['reference_seconds_over_candidate']:.4f} | {r['ci95']} |")
        lines+=['',f"Prespecified K32 speed thresholds (>=2x original and>=1.25x compact):{d['speed_thresholds_passed']}. Same device:{d['device_name']}. Intervals do not capture between-device variation.",'','Native reflow10 noninferiority to compact500 was not established; external noninferiority passed, without increased state coverage. The teacher covers more experimental states in the larger diagnostic. No cold-start, confidence-ranking, multi-sequence-throughput, equilibrium or independent-test claim.']
    else:lines+=['',d['error']]
    output.with_suffix('.md').write_text('\n'.join(lines)+'\n')
