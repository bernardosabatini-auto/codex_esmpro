from types import SimpleNamespace
import unittest
import torch
from torch import nn
from latentfold.embedding import FinalESMC


class Block(nn.Module):
    def forward(self,x):return x+1


class FakeModel(nn.Module):
    def __init__(self):
        super().__init__();self.layers=nn.ModuleList([Block() for _ in range(80)]);self.config=SimpleNamespace(num_hidden_layers=80);self.fail=False
    def forward(self,input_ids,attention_mask,output_hidden_states):
        x=torch.zeros(*input_ids.shape,2560)
        for i,layer in enumerate(self.layers):
            x=layer(x)
            if self.fail and i==21:raise RuntimeError('injected model failure')
        return SimpleNamespace(last_hidden_state=x*3)


class SelectedLayersTests(unittest.TestCase):
    def extractor(self):
        e=FinalESMC.__new__(FinalESMC);e.model=FakeModel();e.device='cpu';e.precision='fp32'
        def tokenizer(sequences,**kwargs):
            length=kwargs['max_length'];mask=torch.zeros(len(sequences),length,dtype=torch.long)
            for i,s in enumerate(sequences):mask[i,:len(s)+2]=1
            return dict(input_ids=mask.clone(),attention_mask=mask)
        e.tokenizer=tokenizer
        return e
    def test_layer_numbering_final_normalization_and_padding(self):
        e=self.extractor();out=e(['ABC','ABCDE'],5,layers=(20,40,60,80))
        for k,expected in ((20,20),(40,40),(60,60),(80,240)):
            self.assertTrue(torch.all(out[k][0,:3]==expected));self.assertTrue(torch.all(out[k][0,3:]==0))
        self.assertTrue(torch.equal(out[80],e(['ABC','ABCDE'],5)))
        self.assertFalse(any(m._forward_hooks for m in e.model.layers))
    def test_hooks_removed_after_failure(self):
        e=self.extractor();e.model.fail=True
        with self.assertRaises(RuntimeError):e(['ABC'],3,layers=(20,40,80))
        self.assertFalse(any(m._forward_hooks for m in e.model.layers))


if __name__=='__main__':unittest.main()
