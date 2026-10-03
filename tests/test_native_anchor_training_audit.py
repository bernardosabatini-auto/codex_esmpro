import copy
import os
from pathlib import Path
import subprocess
import sys
import unittest
from compare_native_anchor_training import check_draws


class NativeTrainingAuditTests(unittest.TestCase):
    def test_only_objective_outcomes_may_differ(self):
        row=dict(step=1,length=128,batch=2,ids=['a','b'],learning_rate_factor=.05,
                 positive_sha256='p',negative_sha256='n',noise_sha256='noise',time_sha256='time',rng_sha256='rng',self_conditioned=True,loss=1.)
        other=dict(row,loss=3.);check_draws([row],[other])
        for key,value in [('negative_sha256','changed'),('noise_sha256','other'),('ids',['b','a']),('self_conditioned',False)]:
            with self.assertRaises(ValueError):check_draws([row],[dict(other,**{key:value})])

    def test_watcher_import_is_lightweight(self):
        root=Path(__file__).resolve().parents[1]
        env=dict(os.environ,PYTHONPATH=str(root/'scripts'))
        code='from pathlib import Path; from compare_native_anchor_training import ready_command; import tempfile; t=tempfile.TemporaryDirectory(); assert ready_command(Path(t.name)) is None'
        subprocess.run([sys.executable,'-c',code],cwd='/tmp',env=env,check=True)


if __name__=='__main__':unittest.main()
