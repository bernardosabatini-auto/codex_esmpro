import unittest
import torch
from latentfold.anchor_kinematics import encode,decode,prefix_products


class AnchorKinematicsTests(unittest.TestCase):
    def fixture(self,n=20,dtype=torch.float64):
        g=torch.Generator().manual_seed(1804)
        # A non-collinear finite chain; geometric plausibility is separately
        # checked on real archived proteins in the CPU representation assay.
        return torch.randn((2,n,4,3),generator=g,dtype=dtype).cumsum(1)

    def test_whole_chain_roundtrip_at_both_ends_and_center(self):
        x=self.fixture()
        for st,size in ((0,1),(3,5),(19,1)):
            y=decode(encode(x),x[:,st:st+size],st)
            torch.testing.assert_close(y,x,atol=1e-10,rtol=1e-10)
            self.assertTrue(torch.equal(y[:,st:st+size],x[:,st:st+size]))

    def test_rigid_motion_and_fp32(self):
        x=self.fixture();q,_=torch.linalg.qr(torch.randn(3,3,dtype=x.dtype));q[:,-1]*=torch.linalg.det(q)
        shift=x.new_tensor([13.,-4.,7.]);moved=x@q+shift
        y=decode(encode(x),moved[:,6:10],6)
        torch.testing.assert_close(y,moved,atol=1e-10,rtol=1e-10)
        z=decode(encode(x.float()),x.float()[:,6:10],6)
        torch.testing.assert_close(z,x.float(),atol=5e-4,rtol=1e-5)

    def test_prefix_order_matches_sequential_noncommuting_products(self):
        g=torch.Generator().manual_seed(23);a=torch.randn((2,11,4,4),generator=g,dtype=torch.float64)
        expected=[];value=torch.eye(4,dtype=a.dtype)[None].expand(2,-1,-1)
        for i in range(11):value=value@a[:,i];expected.append(value)
        torch.testing.assert_close(prefix_products(a),torch.stack(expected,1),atol=1e-8,rtol=1e-12)

    def test_gradients_match_finite_difference(self):
        x=self.fixture(n=8);p=encode(x);p['torsions']=p['torsions'].detach().requires_grad_(True)
        y=decode(p,x[:,3:5],3);loss=y[:,0,1,2].sum()+y[:,-1,1,0].sum()
        gradient=torch.autograd.grad(loss,p['torsions'])[0];direction=torch.randn_like(gradient);eps=1e-6
        values=[]
        for sign in (-1,1):
            q=dict(p,torsions=p['torsions'].detach()+sign*eps*direction);z=decode(q,x[:,3:5],3)
            values.append(z[:,0,1,2].sum()+z[:,-1,1,0].sum())
        torch.testing.assert_close((values[1]-values[0])/(2*eps),(gradient*direction).sum(),atol=1e-7,rtol=1e-6)


if __name__=='__main__':unittest.main()
