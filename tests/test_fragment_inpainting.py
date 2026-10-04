import unittest
from types import SimpleNamespace
import torch
from latentfold.decoder import DifferentiableDecoder
from latentfold.fragment_conditioning import fragment_features
from latentfold.fragment_geometry_conditioning import fragment_coordinates
from latentfold.fragment_inpainting import (place_fragment, constrain_state, tangent_velocity,
    denoising_state, inpainting_loss, FragmentInpaintingDecoder)
from test_fragment_decoder import TinyDecoder


class InpaintingTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(24)
        self.target = torch.randn(2, 8, 4, 3)*10
        self.noise = torch.randn(2, 32, 3)
        self.keep = torch.zeros(2, 8, dtype=torch.bool); self.keep[:, 2:5] = True
        self.t = torch.tensor([.3, .9]); self.dropped = torch.tensor([False, True])

    def model_inputs(self):
        ae = SimpleNamespace(decoder=TinyDecoder(), fm=SimpleNamespace(scale_ref=1.),
                             cfg_exp=SimpleNamespace(model=SimpleNamespace(target_pred='v')))
        codec = DifferentiableDecoder(ae, n_steps=3)
        model = FragmentInpaintingDecoder(codec, seed=24, token_width=16, pair_width=8)
        f, _ = fragment_features(torch.randn(3, 8), 'ACD', length=8, start=2)
        features = f[None].repeat(2, 1, 1)
        coords = fragment_coordinates(self.target[0, 2:5], length=8, start=2)[None].repeat(2, 1, 1)
        z = torch.randn(2, 8, 8); mask = torch.ones(2, 8, dtype=torch.bool)
        anchors = place_fragment(self.target[0, 2:5], self.target, 2)
        return codec, model, z, features, mask, coords, anchors

    def test_placement_is_proper_pose_invariant_and_sparse(self):
        fragment = self.target[0, 2:5].double()
        rotation = torch.tensor([[0., -1, 0], [1., 0, 0], [0, 0, 1]], dtype=torch.float64)
        a = place_fragment(fragment, self.target.double(), 2)
        b = place_fragment(fragment @ rotation+23, self.target.double(), 2)
        torch.testing.assert_close(a, b, atol=1e-10, rtol=0)
        self.assertTrue((a[~self.keep] == 0).all())
        centered = self.target.double()-self.target.double().mean((1, 2), keepdim=True)
        torch.testing.assert_close(a[0, 2:5], centered[0, 2:5], atol=1e-10, rtol=0)
        # An input mirror image cannot be perfectly fitted by an improper transform.
        mirrored = fragment.clone(); mirrored[..., 0] *= -1
        c = place_fragment(mirrored, self.target.double(), 2)
        self.assertGreater(float((c[0, 2:5]-a[0, 2:5]).square().mean()), 1.)

    def test_degenerate_placement_rejected(self):
        with self.assertRaises(ValueError): place_fragment(torch.zeros(3, 4, 3), self.target, 2)

    def test_noisy_path_preserves_anchors_and_center(self):
        clean, noisy, anchors, known = denoising_state(self.target, self.noise, self.t, self.keep, self.dropped)
        torch.testing.assert_close(noisy[known], anchors[known], rtol=0, atol=0)
        torch.testing.assert_close(noisy.mean(1), torch.zeros(2, 3), atol=1e-7, rtol=0)
        self.assertFalse(known[1].any())
        initial = constrain_state(self.noise, anchors, known)
        oracle = clean-initial
        predicted = noisy+(1-self.t[:, None, None])*oracle
        torch.testing.assert_close(predicted, clean, atol=1e-6, rtol=0)

    def test_projection_has_correct_tangent_gradient(self):
        known = self.keep.repeat_interleave(4, 1)
        v = self.noise.clone().requires_grad_()
        projected = tangent_velocity(v, known)
        self.assertTrue((projected[known] == 0).all())
        torch.testing.assert_close(projected.sum(1), torch.zeros(2, 3), atol=1e-6, rtol=0)
        projected.square().sum().backward()
        self.assertTrue((v.grad[known] == 0).all())
        torch.testing.assert_close(v.grad.sum(1), torch.zeros(2, 3), atol=2e-6, rtol=0)

    def test_forward_holds_atoms_at_every_network_call_and_step(self):
        _, model, z, features, mask, coords, anchors = self.model_inputs()
        seen=[]
        hook=model.decoder.register_forward_pre_hook(lambda module,args: seen.append(args[0]['x_t'].detach().clone()))
        out=model(z,features,self.keep,mask,coords,anchors=anchors,noise=self.noise)
        hook.remove()
        torch.testing.assert_close(out[self.keep],anchors[self.keep],atol=2e-6,rtol=0)
        torch.testing.assert_close(out.mean((1,2)),torch.zeros(2,3),atol=2e-6,rtol=0)
        self.assertEqual(len(seen),3)
        for x in seen:
            torch.testing.assert_close(x.reshape(2,8,4,3)[self.keep],anchors[self.keep]/10,atol=0,rtol=0)

    def test_dropout_and_hidden_codes_cannot_leak(self):
        _, model, z, features, mask, coords, anchors = self.model_inputs()
        a=model(z,features,self.keep,mask,coords,anchors=anchors,noise=self.noise,drop_fragment=True)
        features[:,2:5,:28]+=13; coords[:,2:5]+=17; anchors[:,2:5]+=19; z[self.keep]+=90
        b=model(z,features,self.keep,mask,coords,anchors=anchors,noise=self.noise,drop_fragment=True)
        torch.testing.assert_close(a,b,rtol=0,atol=0)

    def test_conditioned_path_ignores_hidden_codes_and_known_noise(self):
        _, model, z, features, mask, coords, anchors = self.model_inputs()
        a=model(z,features,self.keep,mask,coords,anchors=anchors,noise=self.noise)
        z[self.keep]+=90
        noise=self.noise.clone();noise[self.keep.repeat_interleave(4,1)]+=100
        b=model(z,features,self.keep,mask,coords,anchors=anchors,noise=noise)
        torch.testing.assert_close(a,b,rtol=0,atol=0)

    def test_invalid_anchor_support_and_complete_clamp_rejected(self):
        known=self.keep.repeat_interleave(4,1)
        with self.assertRaises(ValueError):constrain_state(self.noise,torch.ones_like(self.noise),known)
        with self.assertRaises(ValueError):constrain_state(self.noise,self.noise,torch.ones_like(known))

    def test_checkpoint_gradients_match_and_original_is_frozen(self):
        codec, model, z, features, mask, coords, _ = self.model_inputs()
        snapshots=[]
        for checkpointed in (False,True):
            model.zero_grad(set_to_none=True)
            loss,parts,pred=inpainting_loss(model,z,self.target,features,self.keep,mask,coords,
                noise=self.noise,t=self.t,dropped=self.dropped,checkpointed=checkpointed)
            loss.backward()
            snapshots.append((loss.detach(),pred.detach(),{k:p.grad.clone() for k,p in model.named_parameters() if p.grad is not None}))
            torch.testing.assert_close(parts['unknown_fm'],loss)
        for a,b in zip(snapshots[0][:2],snapshots[1][:2]):torch.testing.assert_close(a,b,rtol=0,atol=0)
        self.assertEqual(set(snapshots[0][2]),set(snapshots[1][2]))
        for k in snapshots[0][2]:torch.testing.assert_close(snapshots[0][2][k],snapshots[1][2][k],atol=1e-7,rtol=0)
        self.assertTrue(all(p.grad is None and not p.requires_grad for p in codec.parameters()))
        self.assertGreater(float(model.decoder.latent.weight.grad.norm()),0)


if __name__=='__main__':unittest.main()
