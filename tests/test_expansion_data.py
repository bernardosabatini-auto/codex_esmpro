import unittest
from unittest.mock import patch
import numpy as np
from expansion_data import profile_rows,eligibility,reconstruction_summary
from prepare_expansion_shards import partition


class ExpansionDataTest(unittest.TestCase):
    def test_expansion_partition_excludes_profile_and_is_complete(self):
        rows=[dict(id=f'{b}-{i}',family=f'{b}-{i}',bucket=b,length=b-20+i) for b in (128,256,384,512) for i in range(12)]
        used=[r['id'] for r in profile_rows(rows)];groups=partition(rows,used)
        assigned=[r['id'] for g in groups for r in g]
        self.assertEqual(len(assigned),32);self.assertEqual(len(set(assigned)),32)
        self.assertFalse(set(assigned)&set(used));self.assertEqual(set(assigned)|set(used),{r['id'] for r in rows})
        self.assertEqual(groups,partition(list(reversed(rows)),used))

    def test_profile_selection_is_order_independent_and_spans_bucket(self):
        rows=[dict(id=f'{b}-{i}',family=f'{b}-{i}',bucket=b,length=b-20+i) for b in (128,256,384,512) for i in range(12)]
        selected=profile_rows(rows)
        self.assertEqual(selected,profile_rows(list(reversed(rows))))
        self.assertEqual([r['length'] for r in selected[:4]],[108,111,115,119])
        with self.assertRaises(ValueError):profile_rows(rows+[rows[0]])

    def test_eligibility_retains_original_rule_and_empty_valid_is_excluded(self):
        bb=np.zeros((16,64,4,3));valid=np.ones(16,dtype=bool);conf=np.full((16,64),.9)
        state=dict(states=2,mean_pair_distance=4.)
        with patch('expansion_data.definition',return_value=state):
            self.assertEqual(eligibility(bb,valid,conf),(state,None))
            self.assertEqual(eligibility(bb,valid,conf*.8)[1],'mean_confidence')
            self.assertEqual(eligibility(bb,~valid,conf)[1],'too_few_valid')
        with patch('expansion_data.definition',return_value=dict(states=9,mean_pair_distance=4.)):
            self.assertEqual(eligibility(bb,valid,conf)[1],'too_many_states')

    def test_reconstruction_weights_states_and_retains_failures(self):
        row=dict(eligible=True,state_definition=dict(teacher_indices=list(range(16)),clusters=[0]*15+[1],states=2),reconstruction=dict(ca_lddt=[1.]*16,coarse_valid=[True]*15+[False]))
        summary=reconstruction_summary([row]);self.assertFalse(summary['gate_passed'])
        self.assertAlmostEqual(summary['priors']['empirical']['valid'],15/16)
        self.assertAlmostEqual(summary['priors']['balanced']['valid'],.5)
        self.assertFalse(reconstruction_summary([])['gate_passed'])


if __name__=='__main__':unittest.main()
