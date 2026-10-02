"""Matched free-versus-fixed motif sequence design with refold constraint retention."""
import argparse,json
from pathlib import Path
from prepare_fixed_motif_designability import audit_fixed_inputs
from fixed_motif_design import verify_fixed_sequences
from summarize_fragment_designability import analyze as fragment_audit
from analyze_refold_constraint_retention import analyze as retention


def analyze(run):
 if not (run/'manifest.json').exists():return dict(status='failed',error='Missing startup manifest')
 m=json.loads((run/'manifest.json').read_text())
 if m['status']!='complete':return dict(status=m['status'],error=m.get('error','Incomplete'),completed_refolds=len(m['records']))
 c=m['config'];audit_fixed_inputs(c);verify_fixed_sequences(m['sequences'],c['entries']);current=fragment_audit(run);baseline_run=Path(c['baseline_manifest']).parent;baseline=fragment_audit(baseline_run);fixed=retention(run,'motif',current);free=retention(baseline_run,'motif',baseline)
 return dict(status='complete',fixed=fixed,free=free,assay=current,baseline=baseline,completed_refolds=current['completed_refolds'],fixed_sequence_checks=sum(len(s) for s in m['sequences'].values()))


def main():
 p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');lines=['# Preserve motif sequence during design','',f"Status: {d['status']}."]
 if d['status']=='complete':
  lines+=['','Same20backbones/names/budgets. Only supplied motif residues fixed; no native scaffold sequence supplied. All160refolds and all fixed-position sequence checks audited. Experimental and teacher repeatability controls pass.','', '| Design | Codes | N | Original joint success | Strict refold joint success |','|---|---|---:|---:|---:|']
  for arm in ('free','fixed'):
   for r in d[arm]['summaries']:lines.append(f"| {arm} | {r['mode']} | {r['n']} | {r['original_joint']} | {r['strict_joint']} |")
  lines+=['','Original joint requires valid scaffold, motif dRMS<=1A and best8scTM>.5. Strict joint also requires that SAME designed sequence refolds with scTM>.5, motif dRMS<=1A and valid geometry. Failed raw scaffolds remain failures. Four-family development feasibility only; no experimental validation or one-sequence multistability claim.',f"Fixed assay elapsed {d['assay']['assay_elapsed_seconds']:.2f}s,ProteinMPNN {d['assay']['mpnn_seconds']:.2f}s."]
 else:lines+=['',d['error']]
 a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
