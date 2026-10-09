import unittest
from trajectory_guidance_refolding import add_summary


class GuidanceRefoldGateTests(unittest.TestCase):
    def row(self,arm,k,*,strict=False,designable=True,refolds=None):
        return dict(arm=arm,family=str(k%4),raw_gate_passed=True,scaffold_joint_success=strict,valid_designable=designable,complete_strict=strict,refolds=refolds or [dict(coarse_valid=True,sc_tm=.8,scaffold_tm=.8)])

    def result(self):
        return dict(records=[self.row('native',k) for k in range(4)]+[self.row('baseline',k,strict=k==0) for k in range(16)]+[self.row('guided',k,strict=k<4) for k in range(16)])

    def spec(self):
        return dict(advance=dict(minimum_strict_gain=3,minimum_guided_strict_families=2,minimum_native_global_scaffold=3,maximum_designability_loss=0))

    def test_designability_loss_blocks_geometry_gain(self):
        d=self.result();add_summary(d,self.spec());self.assertTrue(d['qualified'])
        d['records'][-1]['valid_designable']=False;add_summary(d,self.spec());self.assertFalse(d['qualified']);self.assertFalse(d['advancement_gates']['designability'])

    def test_native_global_and_scaffold_must_share_refold(self):
        d=self.result()
        for r in d['records'][:2]:r['refolds']=[dict(coarse_valid=True,sc_tm=.8,scaffold_tm=.3),dict(coarse_valid=True,sc_tm=.3,scaffold_tm=.8)]
        add_summary(d,self.spec());self.assertEqual(d['summary']['native']['global_scaffold'],2);self.assertFalse(d['qualified'])
