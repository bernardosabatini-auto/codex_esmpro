"""Frozen ESMC extraction with bounded optional layer capture.

Intermediate layers are post-block residual streams; the final layer includes
the model final normalization, matching historical conditioning exactly.
"""
import torch
from .precision import inference_precision


class FinalESMC:
    def __init__(self, path, device='cuda', precision='bf16'):
        if precision not in ('bf16','fp16','fp32'):
            raise ValueError('unsupported conditioner precision')
        from transformers import AutoModel, AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True, trust_remote_code=False)
        dtype={'bf16':torch.bfloat16,'fp16':torch.float16,'fp32':torch.float32}[precision]
        self.model = AutoModel.from_pretrained(path, dtype=dtype,
            local_files_only=True, trust_remote_code=False).eval().to(device).requires_grad_(False)
        self.device = device
        self.precision = precision
        if self.model.config.hidden_size != 2560:
            raise ValueError('unexpected ESMC conditioner dimensions')

    @torch.no_grad()
    def __call__(self, sequences, length, *, layers=None):
        if not sequences or any(not s or len(s)>length for s in sequences):
            raise ValueError('invalid sequence length; truncation is forbidden')
        enc=self.tokenizer(sequences,return_tensors='pt',padding='max_length',max_length=length+2,truncation=False)
        if enc['input_ids'].shape != (len(sequences),length+2) or enc['attention_mask'].sum(1).tolist() != [len(s)+2 for s in sequences]:
            raise ValueError('tokenizer changed residue correspondence')
        inputs={k:enc[k].to(self.device) for k in ('input_ids','attention_mask')}
        selected=None if layers is None else tuple(layers)
        depth=self.model.config.num_hidden_layers
        if selected is not None and (not selected or len(set(selected))!=len(selected) or any(type(k) is not int or not 1<=k<=depth for k in selected)):
            raise ValueError('invalid selected transformer layers')
        captured={};handles=[]
        try:
            if selected is not None:
                for index in selected:
                    if index==depth:continue
                    def capture(module,args,output,index=index):
                        if not isinstance(output,torch.Tensor):raise ValueError('unexpected transformer-block output')
                        captured[index]=output[:,1:length+1].detach().float().clone()
                    handles.append(self.model.layers[index-1].register_forward_hook(capture))
            with inference_precision(self.precision):
                value=self.model(**inputs,output_hidden_states=False).last_hidden_state[:,1:length+1].float()
        finally:
            for handle in handles:handle.remove()
        mask=torch.arange(length,device=value.device)[None]<torch.tensor([len(s) for s in sequences],device=value.device)[:,None]
        value=value*mask[...,None]
        if value.shape!=(len(sequences),length,2560) or not torch.isfinite(value).all():
            raise ValueError('invalid last-layer ESMC output')
        if selected is None:return value
        if depth in selected:captured[depth]=value
        if set(captured)!=set(selected):raise ValueError('missing selected-layer output')
        for index in selected:
            captured[index]=captured[index]*mask[...,None]
            if captured[index].shape!=value.shape or not torch.isfinite(captured[index]).all():raise ValueError('invalid intermediate embedding')
        return captured
