import unittest,torch
from latentfold.model import LatentFlowNet
from latentfold.tensor_linears import tensor_core_linears,tensor_linear,_TensorLinear


class ContextTests(unittest.TestCase):
    def test_weights_modules_and_state_names_restored_on_error(self):
        model=LatentFlowNet(d_model=8,n_layers=1,n_heads=2,d_cond=4).eval()
        state={k:v.clone() for k,v in model.state_dict().items()};module=model.blocks[0].mlp[0]
        with self.assertRaisesRegex(RuntimeError,'body failure'):
            with tensor_core_linears(model):
                self.assertIsInstance(model.blocks[0].mlp[0],_TensorLinear)
                self.assertIs(model.blocks[0].mlp[0].inner,module)
                with self.assertRaises(ValueError):
                    with tensor_core_linears(model):pass
                raise RuntimeError('body failure')
        self.assertIs(model.blocks[0].mlp[0],module);self.assertEqual(set(state),set(model.state_dict()))
        for k,v in model.state_dict().items():self.assertTrue(torch.equal(v,state[k]))

    def test_training_cpu_and_bad_shapes_rejected(self):
        model=LatentFlowNet(d_model=8,n_layers=1,n_heads=2,d_cond=4)
        with self.assertRaises(ValueError):
            with tensor_core_linears(model):pass
        with self.assertRaises(ValueError):tensor_linear(torch.ones(2,4),torch.ones(8,4))
        with self.assertRaises(ValueError):tensor_linear(torch.ones(2,4),torch.ones(8,3))


if __name__=='__main__':unittest.main()
