import unittest
from gpu_real_utilization import parse_dcgm

H='#Entity GRACT SMACT TENSO DRAMA\n'
class CompositeTests(unittest.TestCase):
    def test_formula_and_memory_is_bandwidth(self):
        d=parse_dcgm(H+'GPU 2 1 .8 .2 .5\n'*10,2)
        self.assertAlmostEqual(d['real_utilization_percent'],55.)
        self.assertEqual(d['means']['dram_active'],.5)
    def test_missing_counters_are_not_zeros(self):
        self.assertEqual(parse_dcgm(H+'GPU 2 N/A N/A N/A N/A\n',2)['status'],'unavailable')
        d=parse_dcgm(H+'GPU 2 1 1 1 1\n'*10+'GPU 2 N/A 1 1 1\n'*2,2)
        self.assertEqual(d['status'],'insufficient_coverage');self.assertNotIn('real_utilization_percent',d)
    def test_reject_unbound_device_or_fields(self):
        for text in [H+'GPU 3 1 1 1 1\n','GPU 2 1 1 1 1\n','#Entity SMACT GRACT TENSO DRAMA\n']:
            with self.assertRaises(ValueError):parse_dcgm(text,2)
    def test_nonfinite_or_dcgm_sentinels_invalid(self):
        d=parse_dcgm(H+'GPU 2 nan 1 1 1\nGPU 2 1 1 1 9223372036854775807\n',2)
        self.assertEqual(d['status'],'unavailable');self.assertEqual(d['invalid_samples'],2)

class ScopedIdentityTests(unittest.TestCase):
    def test_use_physical_slurm_index_not_cgroup_zero(self):
        from scoped_gpu_counters import physical_gpu
        self.assertEqual(physical_gpu('JobId=1 GRES=gpu:nvidia_rtx:1(IDX:4) '),'4')
        for text in ['GRES=gpu:x:2(IDX:0-1)','GRES=gpu:x:2(IDX:0,1)','GRES=gpu:x:1','GRES=gpu:x:1(IDX:0) GRES=gpu:x:1(IDX:4)']:
            with self.assertRaises(ValueError):physical_gpu(text)

    def test_unregistered_job_fails_before_any_query(self):
        import json,tempfile
        from pathlib import Path
        from unittest.mock import patch
        from scoped_gpu_counters import assigned_dcgm_gpu
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/'runs').mkdir();(root/'runs/jobs.json').write_text('{"jobs":[]}')
            with patch('scoped_gpu_counters.subprocess.run') as run:
                with self.assertRaises(ValueError):assigned_dcgm_gpu(root,'999','GPU-abcd','dcgmi')
                run.assert_not_called()

    def test_uuid_mismatch_rejected_and_exact_own_selection(self):
        import json,tempfile
        from pathlib import Path
        from unittest.mock import patch
        from types import SimpleNamespace
        from scoped_gpu_counters import assigned_dcgm_gpu
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/'runs').mkdir();(root/'runs/jobs.json').write_text(json.dumps(dict(jobs=[dict(id='1',gpus=1)])))
            values=[SimpleNamespace(stdout='JobId=1 GRES=gpu:rtx:1(IDX:4)'),SimpleNamespace(stdout='Device UUID: GPU-abcd')]
            with patch('scoped_gpu_counters.subprocess.run',side_effect=values) as run:
                self.assertEqual(assigned_dcgm_gpu(root,'1','GPU-abcd','dcgmi')[0],'4')
                self.assertEqual(run.call_args_list[0].args[0][-1],'1')
                self.assertEqual(run.call_args_list[1].args[0],['dcgmi','discovery','--gpuid','4','--info','a'])
            with patch('scoped_gpu_counters.subprocess.run',side_effect=values):
                with self.assertRaises(ValueError):assigned_dcgm_gpu(root,'1','GPU-ffff','dcgmi')

if __name__=='__main__':unittest.main()
