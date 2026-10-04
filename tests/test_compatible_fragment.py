import unittest
import torch
from compatible_fragment_core import assemble_inputs
from summarize_compatible_fragment import expected_controls


class CompatibleInputs(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(19);self.reference=torch.randn(4,30,4,3)*10
        self.calls=[]
    def encode(self,fragment):
        self.assertEqual(fragment.shape,(1,20,4,3));self.calls.append(fragment.clone())
        return fragment.flatten(2)[...,:8]

    def test_encoder_sees_only_each_slots_isolated_fragment(self):
        values=assemble_inputs(self.reference,'A'*20,5,self.encode)
        self.assertEqual(len(self.calls),4)
        for i in range(4):torch.testing.assert_close(values['fragment'][i],self.calls[i][0],rtol=0,atol=0)
        self.assertFalse(torch.equal(values['isolated_latent'][0],values['isolated_latent'][1]))
        self.assertTrue((values['features'][~values['keep']]==0).all())
        centered=self.reference-self.reference.mean((1,2),keepdim=True)
        torch.testing.assert_close(values['anchors'][values['keep']],centered[values['keep']],atol=2e-5,rtol=0)

    def test_permutation_of_slots_permutates_all_inputs(self):
        a=assemble_inputs(self.reference,'A'*20,5,self.encode);order=torch.tensor([2,0,3,1])
        b=assemble_inputs(self.reference[order],'A'*20,5,self.encode)
        for key in a:torch.testing.assert_close(a[key][order],b[key],rtol=0,atol=0)

    def test_scaffold_changes_cannot_enter_fragment_features(self):
        a=assemble_inputs(self.reference,'A'*20,5,self.encode)
        altered=self.reference.clone();altered[:,:5]+=100;altered[:,25:]-=80
        b=assemble_inputs(altered,'A'*20,5,self.encode)
        for key in ('fragment','isolated_latent','features','keep','coordinates'):
            torch.testing.assert_close(a[key],b[key],rtol=0,atol=0)

    def test_input_pose_does_not_change_condition(self):
        a=assemble_inputs(self.reference,'A'*20,5,self.encode);b=assemble_inputs(self.reference,'A'*20,5,self.encode,posed=True)
        for key in a:torch.testing.assert_close(a[key],b[key],rtol=0,atol=1e-5)

    def test_complete_control_inventory_is_eighty_groups(self):
        ids=[str(i) for i in range(32)];controls=expected_controls(ids,set(ids[:4]))
        self.assertEqual(len(controls),80)
        self.assertEqual(sum(k[0]=='nonleak' for k in controls),16)


if __name__=='__main__':unittest.main()
