import unittest
import numpy as np
import torch
from latentfold.fragment_inpainting import junction_atom_weights, inpainting_loss
from fragment_junction_core import flank_bonds, connected_eligibility
from test_fragment_inpainting import InpaintingTests


class JunctionWeights(unittest.TestCase):
    def test_half_mass_clipped_windows_and_dropout(self):
        for n, start in ((64, 0), (128, 52), (256, 234), (512, 492)):
            keep = torch.zeros(2, n, dtype=torch.bool); keep[:, start:start+20] = True
            w = junction_atom_weights(keep, torch.tensor([False, True]), width=4, mass=.5).reshape(2, n, 4)
            flanks = list(range(max(0, start-4), start))+list(range(start+20, min(n, start+24)))
            torch.testing.assert_close(w.sum((1, 2)), torch.ones(2))
            torch.testing.assert_close(w[0, flanks].sum(), torch.tensor(.5))
            self.assertEqual(float(w[0, keep[0]].sum()), 0)
            torch.testing.assert_close(w[1], torch.full((n, 4), 1/(4*n)), rtol=0, atol=0)

    def test_proportional_mass_recovers_uniform_objective_and_gradient(self):
        keep = torch.zeros(2, 64, dtype=torch.bool); keep[:, 22:42] = True
        dropped = torch.tensor([False, True]); known = (keep & ~dropped[:, None]).repeat_interleave(4, 1)
        w = junction_atom_weights(keep, dropped, width=4, mass=8/44)
        error = torch.rand(2, 256, requires_grad=True); time = torch.tensor([.3, .9])
        uniform = ((error*~known).sum(1)/(~known).sum(1)/((1-time).square()+1e-5)).mean()
        weighted = ((error*w).sum(1)/((1-time).square()+1e-5)).mean()
        torch.testing.assert_close(uniform, weighted)
        torch.testing.assert_close(torch.autograd.grad(uniform, error)[0], torch.autograd.grad(weighted, error)[0])

    def test_flank_error_has_exact_half_mass(self):
        keep = torch.zeros(1, 128, dtype=torch.bool); keep[:, 50:70] = True
        w = junction_atom_weights(keep, torch.tensor([False]), width=4, mass=.5)
        error = torch.zeros(1, 128, 4); error[:, 46:50] = 1; error[:, 70:74] = 1
        torch.testing.assert_close((error.flatten(1)*w).sum(), torch.tensor(.5))

    def test_disconnected_motif_and_no_rest_rejected(self):
        keep = torch.zeros(1, 20, dtype=torch.bool); keep[:, 5:10] = True; keep[:, 13] = True
        with self.assertRaises(ValueError): junction_atom_weights(keep, torch.tensor([False]), width=4, mass=.5)
        keep[:, 13] = False
        with self.assertRaises(ValueError): junction_atom_weights(keep, torch.tensor([False]), width=20, mass=.5)

    def test_weighted_checkpoint_gradient_matches(self):
        fixture = InpaintingTests(); fixture.setUp()
        codec, model, z, features, mask, coords, _ = fixture.model_inputs()
        gradients = []
        for checkpointed in (False, True):
            model.zero_grad(set_to_none=True)
            loss, _, _ = inpainting_loss(model, z, fixture.target, features, fixture.keep, mask, coords,
                noise=fixture.noise, t=fixture.t, dropped=fixture.dropped, checkpointed=checkpointed,
                junction_width=1, junction_mass=.5)
            loss.backward()
            gradients.append({k: p.grad.clone() for k, p in model.named_parameters() if p.grad is not None})
        self.assertEqual(set(gradients[0]), set(gradients[1]))
        for k in gradients[0]: torch.testing.assert_close(gradients[0][k], gradients[1][k], atol=1e-7, rtol=0)
        self.assertTrue(all(p.grad is None for p in codec.parameters()))


class JunctionGate(unittest.TestCase):
    def test_outer_flank_edges_are_included(self):
        bb = np.zeros((64, 4, 3)); bb[:, :, 0] = np.arange(64)[:, None]*3.8
        bb[:, 2, 0] += 2.5
        r = flank_bonds(bb, 20, 20, 4)
        self.assertEqual(r['edges'], [15, 16, 17, 18, 19, 39, 40, 41, 42, 43])
        self.assertTrue(r['all_edges_valid'])
        bb[16, 0, 1] += 5
        self.assertFalse(flank_bonds(bb, 20, 20, 4)['all_edges_valid'])

    def test_geometry_cannot_pass_gate_by_retention_alone(self):
        rows = [dict(arm='generated_cond', target_id=str(i//4), generation_slot=i%4,
                     raw_gate_passed=True, junctions=dict(valid=i<44)) for i in range(128)]
        self.assertFalse(connected_eligibility(rows)['qualified'])
        rows[44]['junctions']['valid'] = True
        self.assertTrue(connected_eligibility(rows)['qualified'])
        rows[44]['raw_gate_passed'] = False
        self.assertFalse(connected_eligibility(rows)['qualified'])
        with self.assertRaises(ValueError): connected_eligibility(rows[:-1])


if __name__ == '__main__': unittest.main()
