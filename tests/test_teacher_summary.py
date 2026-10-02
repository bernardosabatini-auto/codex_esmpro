import unittest
import torch
from transformers import EsmcConfig,EsmcModel
from latentfold.embedding import FinalESMC
from teacher_summary import StreamedSummary,full_summary


class Tokenizer:
    def __call__(self,sequences,**kwargs):
        length=kwargs['max_length'];ids=torch.ones(len(sequences),length,dtype=torch.long);mask=torch.zeros_like(ids)
        for i,s in enumerate(sequences):
            ids[i,0]=0;ids[i,1:len(s)+1]=5;ids[i,len(s)+1]=2;mask[i,:len(s)+2]=1
        return dict(input_ids=ids,attention_mask=mask)


class Adapter(torch.nn.Module):
    def __init__(self):
        super().__init__();self.pair_input_norm=torch.nn.LayerNorm(16);self.pair_proj=torch.nn.Linear(16,7,bias=False);self.layer_weights=torch.nn.Parameter(torch.tensor([-.8,.3,1.1]));self.single_to_pair=torch.nn.Identity()
    def forward(self,x):
        z=self.pair_proj(self.pair_input_norm(x));return self.single_to_pair((self.layer_weights.softmax(0)@z).squeeze(-2))


class TeacherSummaryTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(12);self.e=FinalESMC.__new__(FinalESMC);self.e.device='cpu';self.e.precision='fp32';self.e.tokenizer=Tokenizer()
        self.e.model=EsmcModel(EsmcConfig(hidden_size=16,intermediate_size=32,num_hidden_layers=2,num_attention_heads=2,vocab_size=33)).eval().requires_grad_(False)
        self.a=Adapter().eval().requires_grad_(False)
        # FinalESMC's production width assertion is fixed2560; a tiny equivalent
        # call below preserves the exact tokenizer/normalization/masking semantics.
        class Tiny:
            def __init__(self,e):self.model=e.model;self.tokenizer=e.tokenizer;self.device=e.device
            def __call__(self,sequences,length):
                inputs=self.tokenizer(sequences,max_length=length+2)
                with torch.no_grad():o=self.model(**inputs).last_hidden_state[:,1:length+1]
                mask=torch.arange(length)[None]<torch.tensor([len(s) for s in sequences])[:,None]
                return o*mask[...,None]
        self.e=Tiny(self.e)

    def test_stream_matches_actual_hidden_tuple_and_masks(self):
        runner=StreamedSummary(self.e,self.a)
        for seqs,length in [(['AAAA'],6),(['AA','AAAAA'],7)]:
            x,y=full_summary(self.e,seqs,length,self.a)
            before={id(m):set(m._forward_hooks) for m in self.e.model.modules()}
            a,b=runner(seqs,length)
            self.assertTrue(torch.equal(a,x));self.assertTrue(torch.allclose(b,y,atol=2e-7,rtol=2e-7))
            for i,s in enumerate(seqs):self.assertEqual(float(b[i,len(s):].abs().sum()),0.)
            self.assertEqual(before,{id(m):set(m._forward_hooks) for m in self.e.model.modules()})
        self.assertFalse(self.a.single_to_pair._forward_pre_hooks)

    def test_hooks_restored_when_extraction_raises(self):
        class Failing:
            model=self.e.model
            def __call__(self,*args):raise RuntimeError('expected failure')
        with self.assertRaisesRegex(RuntimeError,'expected failure'):StreamedSummary(Failing(),self.a)(['AA'],4)
        self.assertTrue(all(not m._forward_hooks for m in self.e.model.modules()))


if __name__=='__main__':unittest.main()
