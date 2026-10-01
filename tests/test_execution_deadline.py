"""Standing permission cannot authorize a job beyond the new campaign deadline."""
import datetime
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from submit_registered import policy_deadline


class DeadlineGuardTest(unittest.TestCase):
    def test_late_or_overrunning_jobs_are_rejected(self):
        permission=dict(status='active',mode='experiment_bounded',max_total_gpus=8,deadline_utc='2026-10-02T15:00:00+00:00')
        check=lambda now,minutes:policy_deadline(permission,datetime.datetime.fromisoformat(now),minutes)
        self.assertEqual(check('2026-10-02T12:00:00+00:00',115).hour,15)
        with self.assertRaises(RuntimeError):check('2026-10-02T14:59:00+00:00',1)
        with self.assertRaises(RuntimeError):check('2026-10-02T15:00:01+00:00',1)
        permission['status']='inactive'
        with self.assertRaises(RuntimeError):check('2026-10-02T12:00:00+00:00',1)

if __name__=='__main__':unittest.main()
