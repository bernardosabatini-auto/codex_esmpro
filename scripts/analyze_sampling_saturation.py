"""Describe sample-count gains on identical frozen experimental-state families."""
import argparse,json,math
from pathlib import Path
from prepare_overfit import sha
from latentfold.teacher_states import paired_change


def analyze(sources):
    settings=dict(original='cfg2/latent',candidate='cfg1/latent',teacher='steps50',teacher128='steps50')
    selected={}
    for name,d in sources.items():
        if d['status']!='complete':raise ValueError('incomplete state scores')
        rows=[r for r in d['rows'] if r['setting']==settings[name] and r.get('contact_state_count',0)>1 and 'coverage' in r]
        if len(rows)!=16 or len({r['target_id'] for r in rows})!=16 or len({r['family'] for r in rows})!=16:raise ValueError('expected16 eligible families')
        selected[name]={r['target_id']:r for r in rows}
    ids=set(selected['original']);families={i:r['family'] for i,r in selected['original'].items()}
    for name,rows in selected.items():
        if set(rows)!=ids or {i:r['family'] for i,r in rows.items()}!=families:raise ValueError('unmatched state families')
        for i in ids:
            if sources[name]['definitions'][i]!=sources['original']['definitions'][i]:raise ValueError('state definitions changed')
            counts=(1,4,16,32,128) if name=='teacher128' else (1,4,16,32)
            values=[rows[i]['coverage']['2.0'][str(k)] for k in counts]
            if any(not math.isfinite(v) or not 0<=v<=1 for v in values) or values!=sorted(values):raise ValueError('invalid prefix coverage')
    for i in ids:
        if any(selected['teacher'][i]['coverage']['2.0'][str(k)]!=selected['teacher128'][i]['coverage']['2.0'][str(k)] for k in (1,4,16,32)):raise ValueError('teacher extension prefix differs')
    d=dict(families=16,curves={},increments={})
    for name,rows in selected.items():
        counts=(1,4,16,32,128) if name=='teacher128' else (1,4,16,32)
        values={str(k):{i:rows[i]['coverage']['2.0'][str(k)] for i in sorted(ids)} for k in counts}
        d['curves'][name]={k:sum(v.values())/len(v) for k,v in values.items()}
        d['increments'][name]={f'{a}_to_{b}':paired_change(values[str(b)],values[str(a)],families=families) for a,b in zip(counts[:-1],counts[1:])}
    d['candidate_minus_original']={str(k):paired_change({i:selected['candidate'][i]['coverage']['2.0'][str(k)] for i in ids},{i:selected['original'][i]['coverage']['2.0'][str(k)] for i in ids},families=families) for k in (1,4,16,32)}
    return d


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('original','candidate','teacher','teacher128','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();paths={k:getattr(a,k) for k in ('original','candidate','teacher','teacher128')};d=analyze({k:json.loads(p.read_text()) for k,p in paths.items()});d['sources']={k:dict(path=str(p),sha256=sha(p)) for k,p in paths.items()}
    lines=['# Sampling saturation on frozen experimental states','','All16 eligible development families, unchanged contact-state definitions, valid2A hits and fixed sample prefixes. No sample filtering, state redefinition, or independent-test scoring. These conditional prefix curves do not measure equilibrium populations.','','| Pipeline | K1 | K4 | K16 | K32 | K128 |','|---|---:|---:|---:|---:|---:|']
    for name,curve in d['curves'].items():lines.append('| '+name+' | '+' | '.join(f'{curve[str(k)]:.5f}' if str(k) in curve else 'not run' for k in (1,4,16,32,128))+' |')
    for name,rows in d['increments'].items():
        key='32_to_128' if name=='teacher128' else '16_to_32';r=rows[key];lines+=['',f"{name} {key}: coverage increment {r['difference']:+.5f}, unadjusted paired-family95% interval {r['ci95']}."]
    plateau=all(d['curves'][name]['32']==d['curves'][name]['16'] for name in ('original','candidate'))
    if plateau and d['curves']['teacher128']['128']>d['curves']['teacher128']['32']:
        lines+=['','The original and candidate students gain no additional observed states between16 and32 samples in these prefixes, while the teacher continues gaining through128. This supports prioritizing changes to the student distribution over a blind student sample-count expansion. Zero observed prefix gain does not prove that larger student ensembles can never reach additional states.']
    lines+=['','Do not divide these16-family coverage means by the latency benchmark’s different eight-sequence mean; a coverage-per-time comparison requires matched targets and budgets.','', 'Sources: '+', '.join(f'{k}: {p}' for k,p in paths.items())]
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
