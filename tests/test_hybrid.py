import unittest
import torch
from latentfold.model import LatentFlowNet
from latentfold.precision import hybrid_modules, _FP16Module


class HybridTests(unittest.TestCase):
    def model(self):
        return LatentFlowNet(d_model=32, n_layers=1, n_heads=4, d_cond=16).eval()

    def test_targeted_precision_and_residual_dtype(self):
        model = self.model()
        x = torch.randn(2, 7, 32)
        mlp, qkv = model.blocks[0].mlp, model.blocks[0].attn.qkv
        expected = mlp(x)
        with hybrid_modules(model, 'fp16_mlp'):
            self.assertIsInstance(model.blocks[0].mlp, _FP16Module)
            self.assertIs(model.blocks[0].attn.qkv, qkv)
            actual = model.blocks[0].mlp(x)
            self.assertEqual(actual.dtype, torch.float32)
            torch.testing.assert_close(actual, expected, atol=.001, rtol=.02)
        self.assertIs(model.blocks[0].mlp, mlp)

    def test_restores_checkpoint_keys_after_exception(self):
        model = self.model()
        names = list(model.state_dict())
        original = model.blocks[0].attn.qkv
        with self.assertRaisesRegex(RuntimeError, 'stop'):
            with hybrid_modules(model, 'fp16_linear'):
                self.assertIsInstance(model.blocks[0].attn.qkv, _FP16Module)
                raise RuntimeError('stop')
        self.assertIs(model.blocks[0].attn.qkv, original)
        self.assertEqual(list(model.state_dict()), names)

    def test_training_and_unknown_modes_rejected(self):
        for model, mode in [(self.model().train(), 'fp16_mlp'), (self.model(), 'unknown')]:
            with self.assertRaises(ValueError):
                with hybrid_modules(model, mode):
                    pass
