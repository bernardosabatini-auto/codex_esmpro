"""Completion hook for all four partitions of both isolated-input students."""
import json


def ready_command(root):
    path=root/'runs/repaint_student_model_comparison.json';output=root/'reports/repaint_student_model_comparison_20261004'
    if not path.exists() or output.with_suffix('.json').exists():return None
    plan=json.loads(path.read_text());jobs=plan['jobs']
    if plan.get('repaint_student_comparison') is not True or set(jobs)!={'native_matched','repaint_positive'} or any(len(v)!=4 for v in jobs.values()):raise ValueError('Incomplete student comparison')
    ids=[i for group in jobs.values() for i in group]
    registry={r['id']:r for r in json.loads((root/'runs/jobs.json').read_text())['jobs']}
    if len(set(ids))!=8 or any(i not in registry or registry[i]['completion_action']!='summarize_fragment_preference_refold' for i in ids):raise ValueError('Eight unique registered student refold jobs required')
    paths=[root/f'reports/fragment_preference_refold_{i}.json' for i in ids]
    if not all(p.exists() and json.loads(p.read_text())['status']=='complete' for p in paths):return None
    return [str(root/'scripts/compare_native_anchor_models.py'),'--plan',str(path),'--output',str(output)]
