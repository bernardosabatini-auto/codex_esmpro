"""Stream the teacher's frozen ESM layer projection without its structure trunk."""
import hashlib
import json
from pathlib import Path
import torch
from safetensors import safe_open
from latentfold.embedding import FinalESMC


def load_adapter(path):
    from transformers.models.esmfold2.configuration_esmfold2 import EsmFold2Config
    from transformers.models.esmfold2.modeling_esmfold2 import EsmFold2LanguageModelEncoder
    path=Path(path);config=EsmFold2Config.from_pretrained(path,local_files_only=True)
    adapter=EsmFold2LanguageModelEncoder(config)
    index=json.loads((path/'model.safetensors.index.json').read_text())['weight_map']
    state={};identities={}
    for key in adapter.state_dict():
        name='language_model.'+key
        with safe_open(str(path/index[name]),framework='pt',device='cpu') as f:tensor=f.get_tensor(name).float()
        state[key]=tensor;identities[name]=hashlib.sha256(tensor.numpy().tobytes()).hexdigest()
    adapter.load_state_dict(state,strict=True)
    return adapter.eval().requires_grad_(False),identities


class StreamedSummary:
    """The final hidden tuple member is normalized; do not use raw last-block output."""
    def __init__(self, embedding, adapter):
        self.embedding=embedding;self.adapter=adapter

    @torch.no_grad()
    def __call__(self,sequences,length):
        model=self.embedding.model;depth=len(model.layers);weights=self.adapter.layer_weights.softmax(0)
        if len(weights)!=depth+1:raise ValueError('teacher/student LM layer mismatch')
        total=None;seen=[];handles=[]
        def accumulate(x,index):
            nonlocal total
            if x.ndim!=3 or x.shape[1]!=length or x.shape[-1]!=self.adapter.pair_proj.in_features:raise ValueError('unexpected LM hook shape')
            value=self.adapter.pair_proj(self.adapter.pair_input_norm(x.float()))*weights[index]
            if total is None:total=value
            else:total.add_(value)
            seen.append(index)
        def callback(index):
            def capture(module,args,output):accumulate(output[:,1:length+1],index)
            return capture
        try:
            handles.append(model.embed_tokens.register_forward_hook(callback(0)))
            for i,layer in enumerate(model.layers[:-1],1):handles.append(layer.register_forward_hook(callback(i)))
            final=self.embedding(sequences,length)
            if seen!=list(range(depth)):raise ValueError('LM hooks missing, duplicated, or out of order')
            accumulate(final,depth)
        finally:
            for handle in handles:handle.remove()
        mask=torch.arange(length,device=final.device)[None]<torch.tensor([len(s) for s in sequences],device=final.device)[:,None]
        total=total*mask[...,None]
        if not torch.isfinite(total).all():raise FloatingPointError('nonfinite frozen teacher summary')
        return final,total


@torch.no_grad()
def full_summary(embedding,sequences,length,adapter):
    """Reference: actual installed teacher adapter, stopped before pair construction."""
    enc=embedding.tokenizer(sequences,return_tensors='pt',padding='max_length',max_length=length+2,truncation=False)
    if enc['input_ids'].shape!=(len(sequences),length+2):raise ValueError('invalid reference tokenization')
    inputs={k:enc[k].to(embedding.device) for k in ('input_ids','attention_mask')}
    output=embedding.model(**inputs,output_hidden_states=True)
    hidden=torch.stack(output.hidden_states,dim=2)[:,1:length+1]
    captured={}
    class SummaryReady(Exception):pass
    def stop(module,args):captured['summary']=args[0];raise SummaryReady()
    handle=adapter.single_to_pair.register_forward_pre_hook(stop)
    try:
        try:adapter(hidden)
        except SummaryReady:pass
    finally:handle.remove()
    if set(captured)!={'summary'}:raise ValueError('teacher summary capture failed')
    mask=torch.arange(length,device=hidden.device)[None]<torch.tensor([len(s) for s in sequences],device=hidden.device)[:,None]
    return output.last_hidden_state[:,1:length+1]*mask[...,None],captured['summary']*mask[...,None]
