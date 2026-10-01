import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from compare_overfit_balanced import EXPECTED,scored,validate_runs


class BalancedAnalysisTests(unittest.TestCase):
    def manifests(self):
        result=[]
        for arm,prior in sorted(EXPECTED):
            c=dict(arm=arm,seed=9,evaluation_steps=[2],batches={'128':32})
            if prior=='balanced':c.update(label_distribution=prior,followup_protocol='p',followup_protocol_sha256='sha')
            logs=[dict(step=s,length=128,batch=32,learning_rate=.1,ids_sha256='targets',label_choices_sha256=prior) for s in [1,2]]
            result.append(dict(config=c,status='running',updates=2,initial_checkpoint_sha256='weights',training=logs))
        return result

    def test_accept_intended_prior_change_and_reject_confounding(self):
        good=self.manifests();self.assertEqual(set(validate_runs(good,2)),EXPECTED)
        for mutation in ('seed','weights','target_draw','missing_log','label_draw'):
            bad=copy.deepcopy(good)
            if mutation=='seed':bad[0]['config']['seed']=10
            if mutation=='weights':bad[0]['initial_checkpoint_sha256']='different'
            if mutation=='target_draw':bad[0]['training'][0]['ids_sha256']='different'
            if mutation=='missing_log':bad[0]['training'].pop()
            if mutation=='label_draw':bad[0]['training'][0]['label_choices_sha256']='different'
            with self.assertRaises(ValueError,msg=mutation):validate_runs(bad,2)

    def test_prior_tv_keeps_invalid_mass_and_singletons(self):
        targets={'a':dict(state_definition=dict(clusters=[0,0,0,1]))}
        row=dict(target_id='a',step=2,guidance=1,assignments=[0]*16+[1]*8+[-1]*8,coverage={'32':1.},strict_coverage={'32':.5})
        result=scored(dict(scores=[row]),2,1,targets)['a']
        self.assertEqual(result['balanced_state_tv'],.25)
        self.assertEqual(result['singleton_coverage'],1.)
        row['assignments'].pop()
        with self.assertRaises(ValueError):scored(dict(scores=[row]),2,1,targets)


if __name__=='__main__':unittest.main()
