import unittest
import torch
from latentfold.fragment_inpainting import context_mask, FragmentInpaintingDecoder, inpainting_loss
from test_fragment_inpainting import InpaintingTests


class FlankMaskTests(InpaintingTests):
    def test_dilation_clips_at_termini_and_keeps_known_mask_separate(self):
        keep=torch.zeros(3,50,dtype=torch.bool);keep[0,15:35]=True;keep[1,:20]=True;keep[2,30:]=True
        original=keep.clone();mask=context_mask(keep,8)
        self.assertEqual(mask.sum(1).tolist(),[36,28,28]);self.assertTrue(torch.equal(keep,original))
        self.assertTrue(torch.equal(context_mask(keep,0),keep))
        keep[0,18]=False
        with self.assertRaises(ValueError):context_mask(keep,8)
        with self.assertRaises(ValueError):context_mask(original,-1)

    def test_zero_width_preserves_parameters_and_outputs(self):
        codec,old,z,features,mask,coords,anchors=self.model_inputs()
        new=FragmentInpaintingDecoder(codec,seed=24,token_width=16,pair_width=8,context_flank=0)
        self.assertEqual(set(old.state_dict()),set(new.state_dict()))
        for k in old.state_dict():torch.testing.assert_close(old.state_dict()[k],new.state_dict()[k],rtol=0,atol=0)
        a=old(z,features,self.keep,mask,coords,anchors=anchors,noise=self.noise)
        b=new(z,features,self.keep,mask,coords,anchors=anchors,noise=self.noise)
        torch.testing.assert_close(a,b,rtol=0,atol=0)

    def test_hidden_flanks_cannot_leak_and_only_motif_atoms_are_fixed(self):
        _,model,z,features,mask,coords,anchors=self.model_inputs();model.context_flank=1
        hidden=context_mask(self.keep,1);seen=[]
        def save(module,args):seen.append({k:args[0][k].clone() for k in ('x_t','single_repr')})
        hook=model.decoder.register_forward_pre_hook(save)
        a=model(z,features,self.keep,mask,coords,anchors=anchors,noise=self.noise)
        hook.remove();altered=z.clone();altered[hidden]+=90;noise=self.noise.clone();noise[self.keep.repeat_interleave(4,1)]+=100
        b=model(altered,features,self.keep,mask,coords,anchors=anchors,noise=noise)
        torch.testing.assert_close(a,b,rtol=0,atol=0)
        for values in seen:
            self.assertTrue((values['single_repr'][hidden]==0).all())
            torch.testing.assert_close(values['single_repr'][~hidden],z[~hidden],rtol=0,atol=0)
            state=values['x_t'].reshape(2,8,4,3)
            torch.testing.assert_close(state[self.keep],anchors[self.keep]/10,rtol=0,atol=0)
        self.assertGreater(float((a[hidden & ~self.keep]).abs().sum()),0)
        z=z.requires_grad_();model.zero_grad(set_to_none=True)
        loss,_,_=inpainting_loss(model,z,self.target,features,self.keep,mask,coords,noise=self.noise,t=self.t,dropped=self.dropped,checkpointed=False)
        loss.backward();self.assertTrue((z.grad[hidden]==0).all());self.assertGreater(float(z.grad[~hidden].abs().sum()),0)


if __name__=='__main__':unittest.main()
