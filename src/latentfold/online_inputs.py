"""Sequence-only online noise inputs and native-free selection of complete trios."""
import torch
from .flow import target_noise
from .selection import ca_lddt_medoid


def sequence_noise_batch(requests, length, *, seed, decoder_scale):
    identities=[(r['id'],k) for r,k in requests]
    lengths=[len(r['sequence']) for r,_ in requests]
    if not requests or len(set(identities))!=len(identities) or any(n<1 or n>length for n in lengths):
        raise ValueError('invalid sequence/noise requests')
    mask=torch.arange(length)[None,:]<torch.tensor(lengths)[:,None]
    noise=torch.zeros(len(requests),length,8);decoder_noise=torch.zeros(len(requests),4*length,3)
    for i,((record,k),n) in enumerate(zip(requests,lengths)):
        noise[i,:n]=target_noise([record['id']],[n],8,seed=seed,sample_index=k)[0]
        decoder_noise[i,:4*n]=target_noise([record['id']],[4*n],3,seed=seed,sample_index=k,stream='decoder')[0]*decoder_scale
    return mask,noise,decoder_noise


def select_trios(identities, lengths, predicted_ca):
    """No native coordinates or scores are accepted by this interface."""
    if len(identities)%3 or len(identities)!=len(lengths) or len(identities)!=len(predicted_ca):
        raise ValueError('selection requires complete adjacent three-sample groups')
    choices={}
    for offset in range(0,len(identities),3):
        name=identities[offset][0];n=lengths[offset]
        if identities[offset:offset+3]!=[(name,k) for k in range(3)] or lengths[offset:offset+3]!=[n]*3 or name in choices:
            raise ValueError('invalid trio ordering or coverage')
        choices[name]=ca_lddt_medoid(predicted_ca[offset:offset+3,:n])[0]
    return choices
