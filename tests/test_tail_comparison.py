import copy,unittest
import test_expanded_comparison as fixture_module
from compare_tail import compare

class TailComparisonTests(unittest.TestCase):
    def setUp(self):
        fixture=fixture_module.ExpandedTests();fixture.setUp();self.addCleanup(fixture.temp.cleanup)
        self.full=[copy.deepcopy(fixture.runs[i]) for i in (1,3)]
        for m in self.full:
            c=m['config']
            for key in ('followup_protocol','profile_report'):
                c[key]=c['protocol'];c[key+'_sha256']=c['protocol_sha256']
            for r in m['training']:r['label_choices_sha256']='same-labels'
        self.tail=copy.deepcopy(self.full)
        for m in self.tail:
            m['config']['trainable_tail_blocks']=4
            m['training_subset']=dict(verified_update=500,frozen_unchanged=True,initial_frozen_sha256='fixed',final_frozen_sha256='fixed',ema_frozen_sha256='fixed')

    def test_matched_zero_difference(self):
        d=compare(self.full,self.tail,500)
        self.assertTrue(d['matched'])
        self.assertEqual(d['comparisons']['11_tail_all122_vs_full']['coverage32']['difference'],0)
        self.assertEqual(d['comparisons']['21_tail_additional90_vs_initial']['coverage32']['families'],90)

    def test_confounds_and_missing_evidence_rejected(self):
        for kind in ('config','labels','initial','frozen','hash','seed','missing'):
            tails=copy.deepcopy(self.tail)
            if kind=='config':tails[0]['config']['learning_rate']=.001
            if kind=='labels':tails[0]['training'][0]['label_choices_sha256']='different'
            if kind=='initial':tails[0]['scores'][0]['teacher_ca_lddt']=.1
            if kind=='frozen':tails[0]['training_subset']['frozen_unchanged']=False
            if kind=='hash':tails[0]['training_subset']['ema_frozen_sha256']='changed'
            if kind=='seed':tails.pop()
            if kind=='missing':tails[0]['scores'].pop()
            with self.subTest(kind=kind),self.assertRaises(ValueError):compare(self.full,tails,500)

if __name__=='__main__':unittest.main()
