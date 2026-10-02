"""Explicit Gaussian-noise addressing; padding and decoder noise stay unchanged."""


def noise_address(logical_index,scheme='iid'):
    if not isinstance(logical_index,int) or isinstance(logical_index,bool) or logical_index<0:raise ValueError('Nonnegative integer noise index required')
    if scheme=='iid':return logical_index,1
    if scheme=='antithetic':return logical_index//2,1 if logical_index%2==0 else -1
    raise ValueError('Unknown latent noise scheme')


def native_scheme(head,protocol):
    expected='antithetic' if head['name']==protocol.get('antithetic_head') else 'iid'
    if head.get('latent_noise_scheme','iid')!=expected:raise ValueError('Head differs from declared noise scheme')
    return expected


def raw_identity_samples(head,protocol):
    return (0,) if native_scheme(head,protocol)=='antithetic' else (0,1,2)
