"""Frozen final-layer ESMC extraction; explicit padding and no truncation."""
import torch


class FinalESMC:
    def __init__(self, path, device='cuda'):
        from transformers import AutoModel, AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True, trust_remote_code=False)
        self.model = AutoModel.from_pretrained(path, dtype=torch.bfloat16,
            local_files_only=True, trust_remote_code=False).eval().to(device).requires_grad_(False)
        self.device = device
        if self.model.config.hidden_size != 2560:
            raise ValueError('unexpected ESMC conditioner dimensions')

    @torch.no_grad()
    def __call__(self, sequences, length):
        if not sequences or any(not s or len(s)>length for s in sequences):
            raise ValueError('invalid sequence length; truncation is forbidden')
        enc=self.tokenizer(sequences,return_tensors='pt',padding='max_length',max_length=length+2,truncation=False)
        if enc['input_ids'].shape != (len(sequences),length+2) or enc['attention_mask'].sum(1).tolist() != [len(s)+2 for s in sequences]:
            raise ValueError('tokenizer changed residue correspondence')
        inputs={k:enc[k].to(self.device) for k in ('input_ids','attention_mask')}
        with torch.autocast('cuda',dtype=torch.bfloat16):
            value=self.model(**inputs,output_hidden_states=False).last_hidden_state[:,1:length+1].float()
        mask=torch.arange(length,device=value.device)[None]<torch.tensor([len(s) for s in sequences],device=value.device)[:,None]
        value=value*mask[...,None]
        if value.shape!=(len(sequences),length,2560) or not torch.isfinite(value).all():
            raise ValueError('invalid last-layer ESMC output')
        return value
