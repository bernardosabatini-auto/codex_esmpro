"""Frozen full-backbone ProteinMPNN likelihood for supplied motif residues only."""
import importlib.util
import torch

ALPHABET='ACDEFGHIKLMNPQRSTVWYX'


def load_model(utils,weights):
    spec=importlib.util.spec_from_file_location('latentfold_qualified_mpnn',utils);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    ck=torch.load(weights,map_location='cpu',weights_only=False)
    model=module.ProteinMPNN(ca_only=False,num_letters=21,node_features=128,edge_features=128,hidden_dim=128,num_encoder_layers=3,num_decoder_layers=3,augment_eps=0.,k_neighbors=ck['num_edges']).eval().requires_grad_(False)
    model.load_state_dict(ck['model_state_dict'],strict=True)
    return model


def motif_nll(model,backbone,sequence,start):
    b,n=backbone.shape[:2];mask=backbone.new_ones(b,n);idx=torch.arange(n,device=backbone.device)[None].expand(b,-1);chain=torch.ones(b,n,dtype=torch.long,device=backbone.device)
    target=torch.tensor([ALPHABET.index(x) for x in sequence],device=backbone.device)
    lp=model.unconditional_probs(backbone,mask,idx,chain)[:,start:start+len(sequence)]
    return -lp[:,torch.arange(len(sequence),device=backbone.device),target].mean(1)
