import unittest
import torch
from latentfold.fragment_objective import proper_motif_mse


class FragmentObjectiveTests(unittest.TestCase):
    def test_proper_pose_and_scaffold_independence(self):
        torch.manual_seed(44);ref=torch.randn(2,9,3,dtype=torch.float64);keep=torch.zeros(2,9,dtype=torch.bool);keep[:,2:7]=True;rotation=ref.new_tensor([[0,-1,0],[1,0,0],[0,0,1]]);pred=ref@rotation+13;pred[~keep]=999
        self.assertLess(proper_motif_mse(pred,ref,keep),1e-20)
        mirror=ref.clone();mirror[...,0]*=-1;self.assertGreater(proper_motif_mse(mirror,ref,keep),.01)

    def test_alignment_envelope_gradient_matches_finite_differences(self):
        torch.manual_seed(45);ref=torch.randn(1,7,3,dtype=torch.float64);keep=torch.ones(1,7,dtype=torch.bool);pred=(ref+.2*torch.randn_like(ref)).requires_grad_()
        self.assertTrue(torch.autograd.gradcheck(lambda x:proper_motif_mse(x,ref,keep),(pred,),eps=1e-6,atol=1e-5,rtol=1e-4))
        loss=proper_motif_mse(pred,ref,keep);grad=torch.autograd.grad(loss,pred)[0];self.assertLess(proper_motif_mse(pred-.1*grad,ref,keep),loss)

    def test_endpoint_subset_noise_and_velocity_gradient(self):
        from types import SimpleNamespace
        from latentfold.fragment_objective import endpoint_fragment_objective
        class Decoder:
            fm=SimpleNamespace(scale_ref=1.)
            def __call__(self,z,mask,noise):return z[...,:3]*3+noise.reshape(len(z),z.shape[1],4,3)[:,:,1]
        torch.manual_seed(48);velocity=torch.randn(3,9,8,requires_grad=True);state=dict(x=torch.randn_like(velocity),velocity=velocity,t=torch.tensor([.5,.5,.9]),dropped=torch.zeros(3,dtype=torch.bool),mask=torch.ones(3,9,dtype=torch.bool));coordinates=torch.randn(3,9,3);keep=torch.zeros(3,9,dtype=torch.bool);keep[:,2:7]=True;before=torch.get_rng_state().clone();loss,stats=endpoint_fragment_objective(Decoder(),state,['same','same','outside'],[9,9,9],coordinates,keep,step=3);self.assertEqual(set(stats['chosen_slots']),{0,1});torch.testing.assert_close(torch.get_rng_state(),before,atol=0,rtol=0)
        loss.backward();self.assertTrue(torch.isfinite(velocity.grad).all());self.assertGreater(velocity.grad[:2].norm(),0);self.assertEqual(velocity.grad[2].norm(),0)

    def test_degenerate_alignment_remains_finite_and_invalid_targets_fail(self):
        ref=torch.zeros(1,5,3);ref[0,:,0]=torch.arange(5);keep=torch.ones(1,5,dtype=torch.bool);pred=(ref+1).requires_grad_();loss=proper_motif_mse(pred,ref,keep);loss.backward();self.assertTrue(torch.isfinite(pred.grad).all())
        with self.assertRaises(ValueError):proper_motif_mse(pred,ref.requires_grad_(),keep)

if __name__=='__main__':unittest.main()
