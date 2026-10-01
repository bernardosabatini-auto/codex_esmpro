"""Guard the local HF ESMFold2-Fast port against active missing MSA weights."""


def fast_features(sequence, *, device='cuda'):
    from transformers.models.esmfold2.protein_utils import prepare_protein_features
    features=prepare_protein_features(sequence,device=device)
    # The generic HF helper supplies a depth-one MSA. This installed port ignores
    # msa_encoder.enabled=False and would execute randomly initialized weights.
    # No-MSA profile is identical to the depth-one query profile; zero deletion
    # mean is retained. Biohub's pinned source omits the disabled module entirely.
    for key in ('msa','msa_attention_mask','has_deletion','deletion_value'):features[key]=None
    return features


def load_fast_model(path):
    import torch
    from transformers.models.esmfold2.modeling_esmfold2 import EsmFold2Model
    model,info=EsmFold2Model.from_pretrained(path,dtype=torch.float32,local_files_only=True,output_loading_info=True)
    if getattr(model.config.msa_encoder,'enabled',None) is not False:raise ValueError('expected Fast checkpoint with disabled MSA encoder')
    missing=info.get('missing_keys',[])
    if any(not k.startswith('msa_encoder.') for k in missing) or info.get('unexpected_keys') or info.get('mismatched_keys') or info.get('error_msgs'):raise ValueError('unsupported checkpoint loading mismatch: '+str(info))
    def forbid_active_missing_weights(module,args):raise RuntimeError('disabled uninitialized MSA encoder was called')
    model.msa_encoder.register_forward_pre_hook(forbid_active_missing_weights)
    # Transformers returns sets for some loading fields; keep provenance JSON-safe.
    loading={key:sorted(str(value) for value in info.get(key,[])) for key in ('missing_keys','unexpected_keys','mismatched_keys','error_msgs')}
    return model.eval().cuda().requires_grad_(False),dict(loading=loading,msa_policy='Explicit no-MSA input; runtime guard rejects execution of missing MSA weights',trunk_randomness='Checkpoint enables per-loop LM dropout under eval; fixed-trunk samples condition on one stochastic trunk realization')
