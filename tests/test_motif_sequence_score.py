import unittest
import torch
from latentfold.motif_sequence_score import motif_nll,ALPHABET


class FakeModel:
    def unconditional_probs(self,x,mask,idx,chain):
        logits=x[:,:,1,0,None]*torch.arange(21,dtype=x.dtype)
        return torch.log_softmax(logits,-1)


class MotifSequenceScoreTests(unittest.TestCase):
    def test_only_supplied_indices_enter_loss(self):
        x=torch.arange(2*7*4*3,dtype=torch.float64).reshape(2,7,4,3)/1000;model=FakeModel();seq='ADE';st=2
        value=motif_nll(model,x,seq,st);lp=model.unconditional_probs(x,None,None,None)
        expected=torch.stack([-sum(lp[b,st+k,ALPHABET.index(aa)] for k,aa in enumerate(seq))/len(seq) for b in range(2)])
        torch.testing.assert_close(value,expected,rtol=0,atol=0)
        torch.testing.assert_close(value,torch.cat([motif_nll(model,x[b:b+1],seq,st) for b in range(2)]))

    def test_input_gradient_matches_finite_difference(self):
        x=torch.zeros(1,8,4,3,dtype=torch.float64,requires_grad=True);model=FakeModel();loss=motif_nll(model,x,'AAA',2).sum();g,=torch.autograd.grad(loss,x);direction=g/g.norm();eps=1e-5
        fd=(motif_nll(model,x+eps*direction,'AAA',2)-motif_nll(model,x-eps*direction,'AAA',2))/(2*eps)
        torch.testing.assert_close(fd,(g*direction).sum()[None],atol=1e-7,rtol=1e-7)
