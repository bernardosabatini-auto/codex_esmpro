import itertools,unittest
import torch
from latentfold.conditional_coupling import couple_targets

class ConditionalCouplingTests(unittest.TestCase):
    def test_exact_assignment_matches_brute_force_and_preserves_targets(self):
        g=torch.Generator().manual_seed(13);x=torch.randn(4,3,8,generator=g);z=torch.randn(4,3,8,generator=g);mask=torch.ones(4,3,dtype=torch.bool)
        actual,info=couple_targets(x,z,mask,['p']*4,group_size=4,arm='optimal')
        brute=min(float((x-z[list(p)]).square().mean()) for p in itertools.permutations(range(4)))
        self.assertAlmostEqual(float((x-actual).square().mean()),brute,places=6)
        self.assertEqual(sorted(info['permutation']),list(range(4)));self.assertTrue(torch.equal(actual,z[info['permutation']]))
        plain,_=couple_targets(x,z,mask,['p']*4,group_size=4,arm='independent');self.assertTrue(torch.equal(plain,z))
    def test_conditions_never_exchange_labels_and_padding_cannot_choose_match(self):
        g=torch.Generator().manual_seed(17);x=torch.randn(8,4,8,generator=g);z=torch.randn(8,4,8,generator=g);mask=torch.ones(8,4,dtype=torch.bool);mask[:,3]=False;ids=['a']*4+['b']*4
        _,left=couple_targets(x,z,mask,ids,group_size=4,arm='optimal');x[:,3]*=1000;z[:,3]*=-1000;_,right=couple_targets(x,z,mask,ids,group_size=4,arm='optimal')
        self.assertEqual(left,right);self.assertEqual(sorted(left['permutation'][:4]),list(range(4)));self.assertEqual(sorted(left['permutation'][4:]),list(range(4,8)))
        with self.assertRaises(ValueError):couple_targets(x,z,mask,['a','b']*4,group_size=4,arm='optimal')
    def test_invalid_values_and_masks_rejected(self):
        x=torch.zeros(4,2,8);z=x.clone();mask=torch.ones(4,2,dtype=torch.bool);mask[0,1]=False
        with self.assertRaises(ValueError):couple_targets(x,z,mask,['p']*4,group_size=4,arm='optimal')
        mask[:]=True;x[0,0,0]=float('nan')
        with self.assertRaises(ValueError):couple_targets(x,z,mask,['p']*4,group_size=4,arm='optimal')

    def test_flow_keeps_identical_time_dropout_and_noise_draws(self):
        from latentfold.flow import flow_loss,FlowConfig
        from latentfold.pair_model import PairFlowNet
        torch.manual_seed(25);net=PairFlowNet(d_model=16,n_layers=2,n_heads=2,d_cond=12,d_pair=4,n_pair_blocks=1,max_len=16).train()
        with torch.no_grad():
            for p in net.parameters():p.copy_(torch.randn_like(p)*.1)
        x=torch.randn(4,5,8);z=torch.randn_like(x);mask=torch.ones(4,5,dtype=torch.bool);esm=torch.randn(1,5,12).expand(4,-1,-1);states=[];rngs=[]
        for arm in ('independent','optimal'):
            target,_=couple_targets(x,z,mask,['a']*4,group_size=4,arm=arm);g=torch.Generator().manual_seed(31);net.zero_grad(set_to_none=True)
            loss,info=flow_loss(net,target,esm,mask,FlowConfig(),generator=g,initial_noise=x,return_state=True);loss.backward()
            self.assertTrue(all(torch.isfinite(p.grad).all() for p in net.parameters() if p.grad is not None));state=info['state'];t=state['t'][:,None,None]
            torch.testing.assert_close((state['x']-t*target)/(1-t),x,atol=1e-5,rtol=1e-5);states.append(state);rngs.append(g.get_state())
        torch.testing.assert_close(states[0]['t'],states[1]['t'],atol=0,rtol=0);self.assertTrue(torch.equal(states[0]['dropped'],states[1]['dropped']));self.assertTrue(torch.equal(rngs[0],rngs[1]))

if __name__=='__main__':unittest.main()
