import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_oracle_transport import oracle_sample


def test_single_teacher_endpoint_is_exact():
    rng=np.random.default_rng(3);y=rng.normal(size=(1,8));noise=rng.normal(size=(32,8))
    for steps in (1,5,25):np.testing.assert_allclose(oracle_sample(y,noise,steps),np.repeat(y,32,axis=0),atol=1e-6)


def test_oracle_transport_respects_latent_orthogonal_transform():
    rng=np.random.default_rng(8);y=rng.normal(size=(4,2));noise=rng.normal(size=(32,2));rotation=np.array([[0,-1],[1,0]])
    np.testing.assert_allclose(oracle_sample(y@rotation,noise@rotation,10),oracle_sample(y,noise,10)@rotation,atol=1e-5)
