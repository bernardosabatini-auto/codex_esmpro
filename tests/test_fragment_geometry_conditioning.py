import unittest
import torch
from latentfold.fragment_geometry_conditioning import FragmentGeometryAdapter,fragment_coordinates


class FragmentGeometryTests(unittest.TestCase):
    def test_zero_initialization_and_only_known_pairs(self):
        torch.manual_seed(3);a=FragmentGeometryAdapter(16,n_layers=2,n_heads=4);fragment=torch.randn(5,4,3);coords=fragment_coordinates(fragment,length=9,start=2)[None];keep=torch.zeros(1,9,dtype=torch.bool);keep[:,2:7]=True;mask=torch.ones_like(keep);drop=torch.zeros(1,dtype=torch.bool)
        self.assertTrue(all(torch.count_nonzero(x)==0 for x in a.pair_biases(coords,keep,mask,drop)))
        with torch.no_grad():a.pair_output.weight.normal_();a.pair_output.bias.fill_(.3)
        delta=torch.cat(a.pair_biases(coords,keep,mask,drop),1);unknown=~(keep[:,:,None]&keep[:,None,:]);self.assertEqual(torch.count_nonzero(delta.masked_select(unknown[:,None])),0);self.assertGreater(delta.abs().sum(),0)
        self.assertTrue(all(torch.count_nonzero(x)==0 for x in a.pair_biases(coords,keep,mask,~drop)))
        altered=coords.clone();altered[0,0]=1
        with self.assertRaises(ValueError):a.pair_biases(altered,keep,mask,drop)

    def test_double_precision_distances_preserve_exact_rigid_pose(self):
        torch.manual_seed(14);a=FragmentGeometryAdapter(16,n_layers=2,n_heads=4,distance_precision='fp64');fragment=torch.randn(20,4,3)*10;coords=fragment_coordinates(fragment,length=24,start=2)[None].double();keep=torch.zeros(1,24,dtype=torch.bool);keep[:,2:22]=True;mask=torch.ones_like(keep);drop=torch.zeros(1,dtype=torch.bool);rotation=torch.tensor([[0.,-1,0],[1,0,0],[0,0,1]],dtype=torch.float64);posed=(coords@rotation+11)*keep[...,None]
        with torch.no_grad():a.pair_output.weight.normal_()
        one=torch.cat(a.pair_biases(coords,keep,mask,drop),1);two=torch.cat(a.pair_biases(posed,keep,mask,drop),1);torch.testing.assert_close(one,two,rtol=0,atol=0)

    def test_generator_parity_dropout_and_geometry_gradient(self):
        from latentfold.pair_model import PairFlowNet
        from latentfold.fragment_conditioning import fragment_features,sample_fragment,fragment_flow_loss
        from latentfold.generative import sample_unconditional
        torch.manual_seed(5);net=PairFlowNet(d_model=16,n_layers=2,n_heads=2,d_cond=12,d_pair=4,n_pair_blocks=1,max_len=12).eval()
        with torch.no_grad():
            for p in net.parameters():p.normal_(0,.1)
        a=FragmentGeometryAdapter(16,n_layers=2,n_heads=2).eval();f,k=fragment_features(torch.randn(5,8),'ACDEF',length=9,start=2);f,k=f[None],k[None];mask=torch.ones_like(k);coords=fragment_coordinates(torch.randn(5,4,3),length=9,start=2)[None];noise=torch.randn(1,9,8)
        original=sample_unconditional(net,torch.zeros(1,9,12),mask,noise=noise,steps=4);actual=sample_fragment(net,a,f,k,mask,noise=noise,steps=4,coordinates=coords);torch.testing.assert_close(original,actual,atol=0,rtol=0)
        net.train().requires_grad_(False);net.checkpoint_blocks=True;a.train();loss,_=fragment_flow_loss(net,a,torch.randn_like(noise),f,k,mask,generator=torch.Generator().manual_seed(31),coordinates=coords);loss.backward();self.assertTrue(torch.isfinite(a.pair_output.weight.grad).all());self.assertGreater(a.pair_output.weight.grad.norm(),0)
        with torch.no_grad():a.pair_output.weight.normal_();a.output.weight.normal_()
        net.eval();a.eval();dropped=sample_fragment(net,a,f,k,mask,noise=noise,steps=4,coordinates=coords,drop_fragment=True);torch.testing.assert_close(dropped,original,atol=0,rtol=0)

    def test_rigid_pose_invariance_and_finite_gradient(self):
        torch.manual_seed(4);a=FragmentGeometryAdapter(16,n_layers=2,n_heads=4);fragment=torch.randn(5,4,3);rotation=torch.tensor([[0.,-1,0],[1,0,0],[0,0,1]]);first=fragment_coordinates(fragment,length=9,start=2)[None];second=fragment_coordinates(fragment@rotation+7,length=9,start=2)[None];keep=torch.zeros(1,9,dtype=torch.bool);keep[:,2:7]=True;mask=torch.ones_like(keep);drop=torch.zeros(1,dtype=torch.bool)
        with torch.no_grad():a.pair_output.weight.normal_()
        one=torch.cat(a.pair_biases(first,keep,mask,drop),1);two=torch.cat(a.pair_biases(second,keep,mask,drop),1);torch.testing.assert_close(one,two,rtol=1e-5,atol=1e-5)
        one.square().mean().backward();self.assertTrue(torch.isfinite(a.pair_output.weight.grad).all());self.assertGreater(a.pair_output.weight.grad.norm(),0)

if __name__=='__main__':unittest.main()
