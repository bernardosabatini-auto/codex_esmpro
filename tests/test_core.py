import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import h5py
import numpy as np
import torch
from torch import nn
from latentfold.model import LatentFlowNet
from latentfold.pair_model import PairFlowNet
from latentfold.flow import FlowConfig, SampleConfig, flow_loss, sample, target_noise
from latentfold.metrics import paired_comparison, ca_metrics, wilson_interval, usalign_fixed_tm
from latentfold.data import read_record
from latentfold.checkpoints import load_legacy
from latentfold.decoder import DifferentiableDecoder
from latentfold.batching import prediction_batch, requests_by_bucket

torch.set_num_threads(2)


class CoreTests(unittest.TestCase):
    def net(self, pair=False):
        torch.manual_seed(4)
        kwargs = dict(d_model=32, n_layers=2, n_heads=4, d_cond=12, max_len=16)
        net = PairFlowNet(**kwargs, d_pair=8, n_pair_blocks=1) if pair else LatentFlowNet(**kwargs)
        # Nonzero weights exercise all conditioning and attention paths.
        with torch.no_grad():
            for parameter in net.parameters():
                parameter.normal_(0, 0.1)
        return net

    def test_noise_independent_of_batch_order_padding_and_global_rng(self):
        a = target_noise(["a", "b"], [5, 8], 8, seed=7)
        torch.manual_seed(9234)
        b = target_noise(["b", "a"], [8, 5], 8, seed=7)
        c = target_noise(["a"], [5], 8, seed=7)
        torch.testing.assert_close(a[0, :5], b[1, :5], rtol=0, atol=0)
        torch.testing.assert_close(a[0, :5], c[0], rtol=0, atol=0)
        self.assertFalse(torch.equal(c, target_noise(["a"], [5], 8, seed=7, stream="other")))

    def test_repeated_requests_have_stable_noise_and_exact_coverage(self):
        records = [dict(id=name, sequence='A'*n, esm=torch.ones(n, 12),
                        z=torch.zeros(n, 8), ca=torch.zeros(n, 3)) for name, n in [('a', 5), ('b', 9)]]
        buckets = requests_by_bucket(records, [8, 16], 3)
        identities = [(r['id'], k) for requests in buckets.values() for r, k in requests]
        self.assertEqual(len(identities), 6)
        self.assertEqual(len(set(identities)), 6)
        whole = prediction_batch(buckets[8], 8, seed=5, decoder_scale=2)
        single = prediction_batch([buckets[8][1]], 5, seed=5, decoder_scale=2)
        torch.testing.assert_close(whole[2][1, :5], single[2][0], rtol=0, atol=0)
        torch.testing.assert_close(whole[3][1, :20], single[3][0], rtol=0, atol=0)
        self.assertFalse(torch.equal(whole[2][0], whole[2][1]))
        self.assertEqual(float(whole[2][:, 5:].abs().sum()), 0)
        expected = target_noise(['a'], [20], 3, seed=5, sample_index=1, stream='decoder')*2
        torch.testing.assert_close(single[3], expected, rtol=0, atol=0)
        with self.assertRaises(ValueError):
            prediction_batch([buckets[8][0], buckets[8][0]], 8, seed=5, decoder_scale=1)
        with self.assertRaises(ValueError):
            requests_by_bucket(records, [8], 3)

    def test_sampler_batch_padding_invariance(self):
        for pair in (False, True):
            net = self.net(pair).eval()
            esm = torch.randn(2, 8, 12)
            mask = torch.arange(8)[None, :] < torch.tensor([5, 8])[:, None]
            noise = target_noise(["a", "b"], [5, 8], 8, seed=1)
            cfg = SampleConfig(steps=3)
            whole = sample(net, esm, mask, cfg, noise=noise)
            single = sample(net, esm[:1, :5], mask[:1, :5], cfg, noise=noise[:1, :5])
            torch.testing.assert_close(whole[:1, :5], single, atol=2e-5, rtol=2e-5)
            self.assertEqual(float(whole[0, 5:].abs().sum()), 0)

    def test_repeated_loss_and_gradient(self):
        for pair in (False, True):
            net = self.net(pair)
            z, esm, mask = torch.randn(2, 8, 8), torch.randn(2, 8, 12), torch.ones(2, 8, dtype=torch.bool)
            cfg = FlowConfig(repeats=3, self_condition_probability=1)
            loss, used = flow_loss(net, z, esm, mask, cfg, generator=torch.Generator().manual_seed(1))
            self.assertEqual(used["noisy_copies"], 6)
            loss.backward()
            self.assertTrue(torch.isfinite(net.out_proj.weight.grad).all())
            self.assertGreater(float(net.out_proj.weight.grad.norm()), 0)
            if pair:
                self.assertGreater(float(net.pair.left.weight.grad.norm()), 0)

    def test_cached_condition_preserves_samples(self):
        for pair in (False, True):
            net = self.net(pair).eval()
            esm = torch.randn(2, 8, 12)
            mask = torch.arange(8)[None, :] < torch.tensor([5, 8])[:, None]
            noise = target_noise(["a", "b"], [5, 8], 8, seed=2)
            for guidance in (1.0, 2.0):
                cfg = SampleConfig(steps=5, guidance=guidance)
                old = sample(net, esm, mask, cfg, noise=noise, cache_condition=False)
                new = sample(net, esm, mask, cfg, noise=noise, cache_condition=True)
                torch.testing.assert_close(old, new, rtol=0, atol=0)

    def test_empty_and_invalid_config_rejected(self):
        with self.assertRaises(ValueError):
            FlowConfig(repeats=0)
        with self.assertRaises(ValueError):
            SampleConfig(steps=0)
        with self.assertRaises(ValueError):
            sample(self.net().eval(), torch.zeros(1, 5, 12), torch.zeros(1, 5, dtype=torch.bool), SampleConfig(), noise=torch.zeros(1, 5, 8))

    def test_checkpoint_roundtrip_and_architecture_rejection(self):
        for pair in (False, True):
            net = self.net(pair)
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "model.ckpt"
                state = {"ema": {"_orig_mod."+k:v for k,v in net.state_dict().items()},
                         "arch": dict(d_model=32, n_layers=2, n_heads=4, d_cond=12),
                         "model": "PairFlowNet" if pair else "LatentFlowNet",
                         "extra_arch": dict(d_pair=8, n_pair_blocks=1) if pair else {}}
                torch.save(state, path)
                loaded, _ = load_legacy(path)
                self.assertEqual(loaded.pos.num_embeddings, 16)
                for key, value in net.state_dict().items():
                    torch.testing.assert_close(value, loaded.state_dict()[key])
                state["model"] = "RecFlowNet"
                torch.save(state, path)
                with self.assertRaises(ValueError):
                    load_legacy(path)

    def test_geometry_rigid_invariance_and_bad_control(self):
        rng = np.random.default_rng(0)
        xyz = rng.normal(size=(30, 3)) * 5
        rotation, _ = np.linalg.qr(rng.normal(size=(3, 3)))
        good = ca_metrics(xyz @ rotation + 300, xyz)
        self.assertLess(good["ca_rmsd"], 1e-10)
        self.assertAlmostEqual(good["ca_lddt"], 1)
        bad = ca_metrics(xyz + rng.normal(size=xyz.shape)*10, xyz)
        self.assertLess(bad["ca_lddt"], 0.5)
        mirrored = ca_metrics(xyz * [-1, 1, 1], xyz)
        self.assertGreater(mirrored["ca_rmsd"], 1)

    def test_strict_paired_comparison(self):
        a = {"x": 0.2, "y": 0.3}
        b = {"y": 0.4, "x": 0.3}
        out = paired_comparison(a, b, bootstrap=100)
        self.assertAlmostEqual(out["theirs_minus_ours"], 0.1)
        for bad in ({"x": 0.3}, {"x": None, "y": 0.4}, {"x": 3, "y": 0.4}):
            with self.assertRaises(ValueError):
                paired_comparison(a, bad)
        c = paired_comparison(a, b, clusters={"x":"family", "y":"family"}, bootstrap=100)
        self.assertEqual(c["clusters"], 1)
        lo, hi = wilson_interval(44, 64)
        self.assertLess(lo, 0.67)
        self.assertGreater(hi, 0.69)

    def test_usalign_reference_normalization_and_fail_closed(self):
        output = "TM-score= 0.9 (if normalized by length of Chain_1)\nTM-score= 0.7 (if normalized by length of Chain_2)\n"
        with patch("latentfold.metrics.subprocess.run", return_value=SimpleNamespace(stdout=output)) as run:
            self.assertEqual(usalign_fixed_tm("USalign", "p.pdb", "r.pdb"), 0.7)
            self.assertEqual(run.call_args.args[0][-2:], ["-TMscore", "1"])
        with patch("latentfold.metrics.subprocess.run", return_value=SimpleNamespace(stdout="")):
            with self.assertRaises(ValueError):
                usalign_fixed_tm("USalign", "p.pdb", "r.pdb")

    def test_h5_no_truncation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.h5"
            with h5py.File(path, "w") as f:
                g = f.create_group("val/x")
                g.attrs["sequence"] = "ACDEF"
                for key, width in (("esm2_emb",12), ("z",8), ("ca_coords",3)):
                    g[key] = np.zeros((5,width), np.float32)
            self.assertEqual(len(read_record(path, "val", "x")["sequence"]), 5)
            with self.assertRaises(ValueError):
                read_record(path, "val", "x", max_length=4)
            with self.assertRaises(ValueError):
                read_record(path, "val", "x", embedding_dim=1280)

    def test_decoder_noise_and_latent_gradient(self):
        class FakeDecoder(nn.Module):
            def forward(self, batch):
                coords = batch["single_repr"][..., :3].repeat_interleave(4, 1)
                return {"coors_pred": coords}
        ae = SimpleNamespace(decoder=FakeDecoder(), fm=SimpleNamespace(scale_ref=1),
                             cfg_exp=SimpleNamespace(model=SimpleNamespace(target_pred="x_1")))
        dec = DifferentiableDecoder(ae, n_steps=3)
        z, mask = torch.randn(1, 5, 8, requires_grad=True), torch.ones(1, 5, dtype=torch.bool)
        noise = target_noise(["x"], [20], 3, seed=5, stream="decoder")
        ca = dec(z, mask, noise=noise)
        torch.testing.assert_close(ca, dec(z, mask, noise=noise), atol=0, rtol=0)
        ca.sum().backward()
        self.assertGreater(float(z.grad.norm()), 0)


if __name__ == "__main__":
    unittest.main()
