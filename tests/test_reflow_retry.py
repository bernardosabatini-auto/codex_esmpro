import unittest
from prepare_reflow_retry_native import normalized_scores
from retry_sampler_settings import native_steps,external_steps
from compare_reflow_retry_ensemble import matched_settings

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

    def test_external_worker_cannot_silently_ignore_short_steps(self):
        c=dict(name='reflow10',flow_steps=10,flow_solver='euler',flow_time_power=1);p=dict(sampling_steps_by_head={'reflow10':10})
        self.assertEqual(external_steps(c,p),10)
        for change in ({'flow_steps':25},{'flow_steps':10.0},{'flow_solver':'midpoint'},{'flow_time_power':2}):
            with self.assertRaises(ValueError):external_steps({**c,**change},p)
        with self.assertRaises(ValueError):external_steps(c,{})

    def test_external_comparison_allows_only_declared_differences(self):
        common=dict(samples=32,max_attempts=4,noise_arms=['raw','latent'],seed=7,flow_solver='euler',flow_time_power=1,panel_sha256='p',embedding_cache_sha256='e',decoder_checkpoint_sha256='d')
        a=dict(common,name='reflow10',flow_steps=10,primary_guidance=1,compact_condition=False);b=dict(common,name='compact500',flow_steps=25,primary_guidance=1,compact_condition=True);p=dict(sampling_steps_by_head={'reflow10':10,'compact500':25})
        matched_settings(a,b,p)
        for change in ({'seed':8},{'flow_steps':25},{'max_attempts':5},{'panel_sha256':'wrong'},{'compact_condition':True},{'primary_guidance':2},{'latent_noise_scheme':'antithetic'}):
            with self.assertRaises(ValueError):matched_settings({**a,**change},b,p)

if __name__=='__main__':unittest.main()
