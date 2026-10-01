"""Reference-frame invariant ensemble features with explicit units and masks."""
import numpy as np


def md_features(ca_angstrom, *, trim=2):
    """BioEmu benchmark contact projection inputs; source definition pinned in runs.

    Input [samples,residues,3] is in Angstrom. The published distance scale is
    0.8 nm; immediate sequence neighbours are set to distance zero, hence feature
    one. Upper triangle includes the diagonal. No alignment is needed.
    """
    x=np.asarray(ca_angstrom)
    if x.ndim!=3 or x.shape[-1]!=3 or not np.isfinite(x).all() or trim<0 or x.shape[1]<=2*trim:raise ValueError('invalid complete CA ensemble')
    x=x[:,trim:x.shape[1]-trim]/10
    distance=np.linalg.norm(x[:,:,None]-x[:,None,:],axis=-1)
    index=np.arange(x.shape[1]);distance[:,np.abs(index[:,None]-index[None,:])<=2]=0
    values=np.minimum(np.exp(-distance/.8),1.)
    i,j=np.triu_indices(x.shape[1]);return values[:,i,j]


def project_md(ca_angstrom, mean, transform):
    features=md_features(ca_angstrom)
    if features.shape[-1]!=len(mean) or transform.shape[0]!=len(mean):raise ValueError('projection dimension differs from full sequence')
    return (features-mean)@transform


def sliced_wasserstein_2d(samples, reference, *, directions=64):
    """Deterministic mean 1-Wasserstein distance along evenly spaced 2D axes."""
    from scipy.stats import wasserstein_distance
    x,y=np.asarray(samples),np.asarray(reference)
    if x.ndim!=2 or y.ndim!=2 or x.shape[1]!=2 or y.shape[1]!=2 or not len(x) or not len(y):raise ValueError('expected two nonempty 2D ensembles')
    theta=np.arange(directions)*np.pi/directions;axes=np.stack((np.cos(theta),np.sin(theta)),axis=1)
    return float(np.mean([wasserstein_distance(x@axis,y@axis) for axis in axes]))


def backbone_geometry(backbones):
    """Continuous diagnostics plus a predeclared coarse validity filter.

    This does not certify physical or thermodynamic plausibility. All sequence
    neighbours are genuine peptide neighbours because input is full sequence.
    """
    bb=np.asarray(backbones)
    if bb.ndim!=4 or bb.shape[2:]!=(4,3) or not np.isfinite(bb).all():raise ValueError('invalid backbone ensemble')
    peptide=np.linalg.norm(bb[:,:-1,2]-bb[:,1:,0],axis=-1)
    peptide_bad=((peptide<1.1)|(peptide>1.6)).mean(1)
    ca=bb[:,:,1];distance=np.linalg.norm(ca[:,:,None]-ca[:,None,:],axis=-1);idx=np.arange(ca.shape[1]);nonlocal_pair=np.abs(idx[:,None]-idx[None,:])>2
    clashes=((distance<2.5)&nonlocal_pair).any(2).mean(1)
    ca_gap=(np.linalg.norm(np.diff(ca,axis=1),axis=-1)>4.5).mean(1)
    return dict(peptide_outlier_fraction=peptide_bad,ca_clashing_residue_fraction=clashes,ca_gap_fraction=ca_gap,coarse_valid=(peptide_bad<=.05)&(clashes<=.01)&(ca_gap<=.01))
