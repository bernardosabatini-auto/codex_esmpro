import copy
import unittest
import torch
from latentfold.continuation import restore_adam_state, validate_saved_state


class ContinuationTests(unittest.TestCase):
    def test_restored_next_update_matches_original_and_keeps_new_lr(self):
        torch.manual_seed(42)
        original=torch.nn.Linear(4,2)
        opt=torch.optim.AdamW(original.parameters(),lr=.001,betas=(.9,.95),foreach=False)
        x=torch.ones(3,4)
        for _ in range(3):
            opt.zero_grad();original(x).square().sum().backward();opt.step()
        saved=copy.deepcopy(dict(net=original.state_dict(),ema=original.state_dict(),opt=opt.state_dict(),step=3))
        model=copy.deepcopy(original);validate_saved_state(model,saved)
        resumed=torch.optim.AdamW(model.parameters(),lr=.0001,betas=(.9,.95),foreach=False)
        restore_adam_state(resumed,saved['opt'])
        self.assertEqual(resumed.param_groups[0]['lr'],.0001)
        self.assertFalse(resumed.param_groups[0]['foreach'])
        opt.param_groups[0]['lr']=.0001
        for m,o in [(original,opt),(model,resumed)]:
            o.zero_grad();m(x).square().sum().backward();o.step()
        for a,b in zip(original.parameters(),model.parameters()):
            torch.testing.assert_close(a,b,rtol=0,atol=0)
        self.assertTrue(all(float(s['step'])==3 for s in saved['opt']['state'].values()))
        incompatible=torch.optim.AdamW(model.parameters(),betas=(.9,.999))
        with self.assertRaisesRegex(ValueError,'betas'):restore_adam_state(incompatible,saved['opt'])
        reordered=copy.deepcopy(saved);reordered['net']=dict(reversed(list(saved['net'].items())))
        with self.assertRaisesRegex(ValueError,'ordering'):validate_saved_state(model,reordered)


if __name__=='__main__':unittest.main()
