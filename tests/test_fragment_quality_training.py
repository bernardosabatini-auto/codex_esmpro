import copy
import unittest
from unittest.mock import patch
from fragment_quality_training import compare_quality_traces


def fixtures():
    r=dict(step=1,length=128,batch=1,ids=['p'],conditions=['c20_left'],learning_rate_factor=.1,
           self_conditioned=True,noise_sha256='n',time_sha256='t',drop_sha256='d',rng_sha256='r',global_rng_sha256='g')
    a=dict(config={},training=[r]);b=copy.deepcopy(a);b['training'][0]['conditions']=['c20_right']
    return dict(control=a,quality=b)


class QualityTraceTests(unittest.TestCase):
    def check(self,manifests):
        with patch('fragment_quality_training.selection_for_config',side_effect=[{'p':'c20_left'},{'p':'c20_right'}]):
            return compare_quality_traces(manifests)

    def test_declared_condition_change(self):self.assertEqual(self.check(fixtures()),1)

    def test_wrong_condition_rejected(self):
        m=fixtures();m['quality']['training'][0]['conditions']=['c20_left']
        with self.assertRaises(ValueError):self.check(m)

    def test_rng_or_protein_change_rejected(self):
        for key,value in [('noise_sha256','changed'),('ids',['other'])]:
            m=fixtures();m['quality']['training'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.check(m)


if __name__=='__main__':unittest.main()
