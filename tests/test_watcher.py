"""Failure, isolation, and completion controls for unattended analysis."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import watch_jobs as watch
from summarize_comparison import validate_scores


class WatcherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'runs/watch').mkdir(parents=True)
        self.job = dict(id='123', tasks=['123_0', '123_1'], state='RUNNING', completion_action='summarize_comparison')
        (self.root/'runs/jobs.json').write_text(json.dumps({'jobs': [self.job]}))

    def rows(self, state='COMPLETED', code='0:0'):
        return {i: dict(state=state, exit_code=code, elapsed='00:01:00', ended='2026-09-30T12:00:00') for i in self.job['tasks']}

    def test_ids_cannot_escape_registered_parent(self):
        for job in [dict(id='123', tasks=['999_0']), dict(id='123,999')]:
            with self.assertRaises(ValueError):
                watch.job_ids(job)

    def test_scheduler_query_and_results_are_scoped(self):
        run = Mock(return_value=Mock(stdout='123_0|COMPLETED|0:0|00:01:00|end\n999|RUNNING|0:0|00:01:00|end\n'))
        self.assertEqual(set(watch.scheduler_states(['123_0'], run)), {'123_0'})
        args = run.call_args.args[0]
        self.assertEqual(args[args.index('-j')+1], '123_0')
        self.assertNotIn('-u', args)

    def test_completion_analysis_once_and_no_more_scheduler_queries(self):
        query, analyze = Mock(return_value=self.rows()), Mock(return_value='report.md')
        first = watch.tick(self.root, {}, query, analyze)
        self.assertEqual(first['jobs']['123']['outcome'], 'analyzed')
        watch.tick(self.root, {}, query, analyze)
        self.assertEqual(query.call_count, 1)
        self.assertEqual(analyze.call_count, 1)
        self.assertEqual(query.call_args.args[0], ['123_0', '123_1'])

    def test_pending_accounting_fallback_is_scoped(self):
        run=Mock(side_effect=[Mock(stdout=''),Mock(stdout='123_0|PENDING|0:00\n999|RUNNING|0:20\n')])
        rows=watch.scheduler_states(['123_0'],run)
        self.assertEqual(set(rows),{'123_0'})
        self.assertEqual(rows['123_0']['state'],'PENDING')
        args=run.call_args.args[0]
        self.assertEqual(args[0],'squeue')
        self.assertEqual(args[args.index('-j')+1],'123_0')
        self.assertNotIn('-u',args)

    def test_missing_or_running_tasks_never_trigger_analysis(self):
        analyze = Mock()
        for rows in [{}, {'123_0': self.rows()['123_0']}, self.rows('RUNNING')]:
            state = watch.tick(self.root, {}, Mock(return_value=rows), analyze)
            self.assertFalse(state['jobs']['123'].get('handled'))
        analyze.assert_not_called()

    def test_failed_job_alerts_without_success_analysis(self):
        analyze = Mock()
        state = watch.tick(self.root, {}, Mock(return_value=self.rows('TIMEOUT', '0:15')), analyze)
        self.assertEqual(state['jobs']['123']['outcome'], 'job_failed')
        self.assertTrue((self.root/'runs/watch/events.jsonl').exists())
        analyze.assert_not_called()

    def test_analysis_failure_is_retryable_and_not_marked_handled(self):
        query, analyze = Mock(return_value=self.rows()), Mock(side_effect=RuntimeError('incomplete export'))
        state = watch.tick(self.root, {}, query, analyze)
        self.assertFalse(state['jobs']['123'].get('handled'))
        self.assertEqual(state['jobs']['123']['attempts'], 1)
        with patch.object(watch.time, 'time', return_value=state['jobs']['123']['retry_after']+1):
            analyze.side_effect = None
            analyze.return_value = 'report.md'
            state = watch.tick(self.root, {}, query, analyze)
        self.assertEqual(state['jobs']['123']['outcome'], 'analyzed')

    def test_score_coverage_rejects_duplicates_and_missing(self):
        manifest = dict(status='complete', completed_predictions=2,
                        config=dict(flow_steps=[25], guidance=[2], target_ids=['a'], samples=2))
        rows = [dict(setting='steps25_cfg2', target_id='a', sample=k, tm_fixed_reference=.5, ca_lddt=.6) for k in range(2)]
        self.assertEqual(validate_scores(manifest, dict(status='complete', records=rows)), ['steps25_cfg2'])
        for invalid in [rows[:1], [rows[0], rows[0]], [dict(rows[0], tm_fixed_reference=float('nan')), rows[1]]]:
            with self.assertRaises(ValueError):
                validate_scores(manifest, dict(status='complete', records=invalid))


if __name__ == '__main__':
    unittest.main()
