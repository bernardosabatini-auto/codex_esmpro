import unittest
import torch
from test_fragment_latent_weight import ConstantVelocity
from latentfold.fragment_conditioning import FragmentAdapter,fragment_features,fragment_flow_loss
from fragment_time_shift import matched_traces


class TimeSensitiveVelocity(ConstantVelocity):
    def forward(self,x,t,esm,mask,**kwargs):return self.velocity+x*(1+t[:,None,None])


class ConditionalTimeTests(unittest.TestCase):
    def test_shift_changes_only_present_condition_times_and_preserves_rng(self):
        b,n=64,4;net,adapter=TimeSensitiveVelocity(b,n),FragmentAdapter(16)
        f,k=fragment_features(torch.zeros(2,8),'AC',length=n,start=1);f=f[None].expand(b,-1,-1).clone();k=k[None].expand(b,-1).clone()
        mask=torch.ones(b,n,dtype=torch.bool);target=torch.ones(b,n,8);traces=[];states=[];grads=[];losses=[]
        for kwargs in ({},{'conditional_time_shift':0.},{'conditional_time_shift':-1.}):
            gen=torch.Generator().manual_seed(42);net.zero_grad();loss,info=fragment_flow_loss(net,adapter,target,f,k,mask,generator=gen,motif_weight=3.,**kwargs);loss.backward();traces.append(info);states.append(gen.get_state());grads.append(net.velocity.grad.clone());losses.append(loss.detach())
        torch.testing.assert_close(losses[0],losses[1],rtol=0,atol=0)
        for i in (1,2):
            torch.testing.assert_close(states[0],states[i],rtol=0,atol=0)
            for key in ('noise','dropped'):torch.testing.assert_close(traces[0][key],traces[i][key],rtol=0,atol=0)
            self.assertEqual(traces[0]['self_conditioned'],traces[i]['self_conditioned'])
        original=traces[0]['t'];shifted=traces[2]['t'];present=~traces[0]['dropped']&k.any(1)
        self.assertTrue(present.any() and (~present).any());torch.testing.assert_close(original,traces[1]['t'],rtol=0,atol=0);torch.testing.assert_close(original,traces[2]['base_t'],rtol=0,atol=0)
        torch.testing.assert_close(shifted[~present],original[~present],rtol=0,atol=0)
        torch.testing.assert_close(torch.logit(shifted[present])-torch.logit(original[present]),-torch.ones_like(original[present]),atol=2e-6,rtol=0)
        torch.testing.assert_close(grads[0][~present],grads[2][~present],rtol=0,atol=0)
        self.assertTrue((grads[0][present]!=grads[2][present]).any())

    def test_audit_rejects_changed_noise_null_time_or_missing_shift(self):
        keys=('step','length','batch','ids','conditions','learning_rate_factor','self_conditioned','noise_sha256','drop_sha256','rng_sha256','global_rng_sha256')
        base=[dict({k:i for k in keys},time_sha256=str(i)) for i in range(40)]
        new=[dict(r,time_sha256='shift'+str(i),base_time_sha256=r['time_sha256'],null_time_max_abs=0.,conditioned_examples=1) for i,r in enumerate(base)]
        self.assertEqual(matched_traces(base,new),40)
        all_null=[dict(r) for r in new];all_null[0].update(conditioned_examples=0,time_sha256='0');self.assertEqual(matched_traces(base,all_null),39)
        for key,value in [('noise_sha256','other'),('null_time_max_abs',.01),('base_time_sha256','other'),('time_sha256','0')]:
            changed=[dict(r) for r in new];changed[0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):matched_traces(base,changed)
