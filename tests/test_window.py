import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from close_autonomous_window import window_ids


class WindowTests(unittest.TestCase):
    def test_only_registered_nonterminal_jobs_inside_window(self):
        window=dict(started='2026-10-01T01:30:07Z',deadline='2026-10-01T13:30:07Z')
        jobs=[dict(id='10',submitted='2026-10-01T01:29:00Z',state='RUNNING'),
              dict(id='11',submitted='2026-10-01T02:00:00Z',state='SUBMITTED',tasks=['11_0','11_1']),
              dict(id='12',submitted='2026-10-01T02:00:00Z',state='COMPLETED'),
              dict(id='13',submitted='2026-10-01T14:00:00Z',state='RUNNING')]
        self.assertEqual(window_ids(dict(jobs=jobs),window),['11_0','11_1'])
        jobs[1]['tasks']=['99_0']
        with self.assertRaises(ValueError):window_ids(dict(jobs=jobs),window)
