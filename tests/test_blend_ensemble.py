import unittest
from prepare_blend_ensemble import qualified

class BlendEnsembleTests(unittest.TestCase):
    def test_fixed_blend_native_gate(self):
        head='seed2026100171_blend';t=dict(step=2000,blend_effects={},summaries={head+'_cfg1':dict(quality_passed=True)})
        self.assertEqual(qualified(t,head,.5),head+'_cfg1')
        for mode in ('alpha','head','step','quality','scope'):
            x=dict(t);alpha=.5;name=head
            if mode=='alpha':alpha=.75
            if mode=='head':name='seed2026100171_full'
            if mode=='step':x['step']=500
            if mode=='quality':x['summaries']={head+'_cfg1':dict(quality_passed=False)}
            if mode=='scope':x.pop('blend_effects')
            with self.subTest(mode=mode),self.assertRaises(ValueError):qualified(x,name,alpha)

if __name__=='__main__':unittest.main()
