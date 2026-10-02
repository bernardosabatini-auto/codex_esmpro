import unittest
from prepare_reflow_retry_native import normalized_scores
from retry_sampler_settings import native_steps

class ReflowRetryTests(unittest.TestCase):
    def test_normalization_keeps_every_archived_value(self):
        ids=[str(i) for i in range(64)];rows=[dict(step=2000,sampling_steps=10,target_id=i,sample=k,ca_lddt=.8,coarse_valid=float(k!=2)) for i in ids for k in range(3)]
        m=dict(status='complete',updates=2000,config=dict(arm='reflow_paired'),scores=rows)
        result=normalized_scores(m,ids)
        for original,normalized in zip(rows,result):self.assertEqual(original,{k:normalized[k] for k in original})
        with self.assertRaises(ValueError):normalized_scores({**m,'scores':rows[:-1]},ids)
        with self.assertRaises(ValueError):normalized_scores({**m,'config':dict(arm='reflow_independent')},ids)
    def test_step_count_must_be_declared_twice(self):
        p=dict(sampling_steps_by_head={'reflow10':10})
        self.assertEqual(native_steps(dict(name='original'),p),25)
        self.assertEqual(native_steps(dict(name='reflow10',sampling_steps=10),p),10)
        with self.assertRaises(ValueError):native_steps(dict(name='reflow10'),p)
        with self.assertRaises(ValueError):native_steps(dict(name='original',sampling_steps=10),p)

if __name__=='__main__':unittest.main()
