"""Compare local MD features to commit-pinned upstream numerical fixtures."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from latentfold.ensemble_metrics import md_features,project_md


def main():
    p=argparse.ArgumentParser();p.add_argument('--assets',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=a.assets/'tests/test_data/md_emulation';prefix=root/'test_cath1_1bl0A02_'
    paths={k:Path(str(prefix)+k+'.npy') for k in ('ca_coordinates','features','projections')};x=np.load(paths['ca_coordinates'])
    # Fixture coordinates already have the two terminal residues removed.
    features=md_features(x*10,trim=0);expected=np.load(paths['features'])
    np.testing.assert_allclose(features,expected,atol=2e-7,rtol=2e-6)
    data=a.assets/'bioemu_benchmarks/assets/md_emulation_benchmark_0.1/md_emulation';key='cath1_1bl0A02'
    with np.load(data/'projections_mean.npz') as means,np.load(data/'projections_sqrt_inv_cov.npz') as transforms:
        projected=(features-means[key])@transforms[key]
    ref=np.load(paths['projections']);np.testing.assert_allclose(projected,ref,atol=2e-5,rtol=2e-5)
    result=dict(status='passed',feature_max_abs=float(np.max(np.abs(features-expected))),projection_max_abs=float(np.max(np.abs(projected-ref))),fixtures={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths.values()})
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':main()
