import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

from watch_jobs import refresh_analysis_monitoring, run_monitored_analysis


class AnalysisMonitoringTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root/'runs/watch').mkdir(parents=True)
        jobs = [dict(id='10', completion_action='audit'), dict(id='11', tasks=['11_0','11_1']),
                dict(id='12'), dict(id='13', state='COMPLETED')]
        (self.root/'runs/jobs.json').write_text(json.dumps(dict(jobs=jobs)))
        (self.root/'runs/watch/state.json').write_text(json.dumps(dict(jobs={'12': {'handled': True}})))
        self.beat = self.root/'runs/watch/heartbeat.json'
        self.beat.write_text('previous heartbeat')

    def test_only_registered_unhandled_ids_are_polled(self):
        query = Mock(return_value={'10': {'state': 'COMPLETED'}, '11_0': {'state': 'RUNNING'}, '11_1': {'state': 'PENDING'}})
        refresh_analysis_monitoring(self.root, query=query)
        query.assert_called_once_with(['10', '11_0', '11_1'])
        result = json.loads(self.beat.read_text())
        self.assertEqual(result['outstanding_jobs'], ['11_0', '11_1'])
        self.assertEqual(result['status'], 'ok')

    def test_failed_scheduler_query_does_not_refresh_heartbeat(self):
        with self.assertRaises(RuntimeError):
            refresh_analysis_monitoring(self.root, query=Mock(side_effect=RuntimeError('scheduler unavailable')))
        self.assertEqual(self.beat.read_text(), 'previous heartbeat')

    def test_invalid_registered_task_rejected_before_query(self):
        (self.root/'runs/jobs.json').write_text(json.dumps(dict(jobs=[dict(id='11', tasks=['999'])])))
        query = Mock()
        with self.assertRaises(ValueError):
            refresh_analysis_monitoring(self.root, query=query)
        query.assert_not_called()

    def test_long_analysis_keeps_polling_and_preserves_result(self):
        child = MagicMock()
        child.__enter__.return_value = child
        child.wait.side_effect = [subprocess.TimeoutExpired(['audit'], 30), 0]
        child.poll.return_value = 0
        with patch('watch_jobs.subprocess.Popen', return_value=child), patch('watch_jobs.time.monotonic', side_effect=[0, 1, 32]), patch('watch_jobs.refresh_analysis_monitoring') as refresh:
            run_monitored_analysis(['audit'], root=self.root, env={}, log=Mock())
        refresh.assert_called_once_with(self.root)
        self.assertEqual(child.wait.call_count, 2)
        child.kill.assert_not_called()

    def test_monitor_failure_terminates_owned_analysis(self):
        child = MagicMock()
        child.__enter__.return_value = child
        child.wait.side_effect = [subprocess.TimeoutExpired(['audit'], 30), 0]
        child.poll.return_value = None
        with patch('watch_jobs.subprocess.Popen', return_value=child), patch('watch_jobs.time.monotonic', side_effect=[0, 1]), patch('watch_jobs.refresh_analysis_monitoring', side_effect=RuntimeError('scheduler failed')):
            with self.assertRaises(RuntimeError):
                run_monitored_analysis(['audit'], root=self.root, env={}, log=Mock())
        child.kill.assert_called_once()


if __name__ == '__main__':
    unittest.main()
