"""Equal-capacity residual adapters for frozen256D teacher/control features."""
import json
from pathlib import Path
import h5py
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from prepare_overfit import sha


class SummaryAdapter(nn.Module):
    def __init__(self,width=128,bound=.1):
        super().__init__()
        if width<1 or not 0<bound<=1:raise ValueError('invalid residual adapter')
        self.bound=bound
        self.down=nn.Linear(256,width,bias=False)
        self.up=nn.Linear(width,2560,bias=False)
        nn.init.zeros_(self.up.weight)

    def forward(self,final,feature,mask):
        if final.shape!=(*mask.shape,2560) or feature.shape!=(*mask.shape,256) or mask.dtype!=torch.bool:raise ValueError('invalid summary conditioning shapes')
        residual=self.bound*torch.tanh(self.up(F.silu(self.down(F.layer_norm(feature,(256,))))))
        return (final+residual)*mask[...,None]


def load_features(c,records):
    for key in ('summary_protocol','feature_manifest'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('changed '+key)
    protocol=json.loads(Path(c['summary_protocol']).read_text())
    expected=dict(learning_rate=protocol['flow_learning_rate'],warmup_updates=protocol['warmup_updates'],ema_decay=protocol['ema_decay'],batches=protocol['batches'],evaluation_seed=protocol['evaluation_seed'],evaluation_guidance=[1],decoder_steps=3)
    if any(c.get(k)!=v for k,v in expected.items()):raise ValueError('summary recipe changed')
    m=json.loads(Path(c['feature_manifest']).read_text())
    if m['status']!='complete' or not m['qualified'] or c['summary_arm'] not in protocol['arms']:raise ValueError('feature extraction not qualified')
    if m['config']['label_manifest_sha256']!=c['label_manifest_sha256']:raise ValueError('different labels')
    path=Path(c['feature_manifest']).parent/'features.h5'
    if sha(path)!=m['features_sha256']:raise ValueError('changed features')
    with h5py.File(path) as h:
        if set(h)!=set(records):raise ValueError('feature coverage mismatch')
        for ident,r in records.items():
            g=h[ident];value=g[c['summary_arm']][:]
            if g.attrs['sequence_sha256']!=r['sequence_sha256'] or value.shape!=(r['length'],256) or not np.isfinite(value).all():raise ValueError('invalid features')
            r['summary_feature']=torch.from_numpy(value)
    return protocol


def condition(model,records,ids,esm,mask):
    features=esm.new_zeros(len(ids),esm.shape[1],256)
    for i,ident in enumerate(ids):features[i,:records[ident]['length']]=records[ident]['summary_feature'].to(esm.device)
    return model.summary_adapter(esm,features,mask)
