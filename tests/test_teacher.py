import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import torch
from latentfold.teacher import load_fast_model,fast_features


class Fake(torch.nn.Module):
    def __init__(self):
        super().__init__();self.config=SimpleNamespace(msa_encoder=SimpleNamespace(enabled=False));self.msa_encoder=torch.nn.Identity()
    def cuda(self):return self


class TeacherTests(unittest.TestCase):
    def test_missing_unused_weights_logged_but_execution_forbidden(self):
        m=Fake();info=dict(missing_keys={'msa_encoder.weight'},unexpected_keys=set(),mismatched_keys=set(),error_msgs=[])
        with patch('transformers.models.esmfold2.modeling_esmfold2.EsmFold2Model.from_pretrained',return_value=(m,info)):
            model,metadata=load_fast_model('unused');json.dumps(metadata)
        with self.assertRaisesRegex(RuntimeError,'disabled uninitialized'):model.msa_encoder(torch.ones(1))
    def test_missing_active_weight_rejected(self):
        with patch('transformers.models.esmfold2.modeling_esmfold2.EsmFold2Model.from_pretrained',return_value=(Fake(),dict(missing_keys={'structure_head.weight'}))):
            with self.assertRaisesRegex(ValueError,'loading mismatch'):load_fast_model('unused')
    def test_no_msa_inputs(self):
        f=fast_features('ACDEFGHIKLMNPQRSTVWY',device='cpu')
        for k in ('msa','msa_attention_mask','has_deletion','deletion_value'):self.assertIsNone(f[k])
        self.assertFalse(bool(f['deletion_mean'].any()))


if __name__=='__main__':unittest.main()
