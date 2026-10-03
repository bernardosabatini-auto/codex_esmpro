import unittest
import torch
from latentfold.endpoint_guidance import retract,tangent_gradient,proper_loss


class EndpointGeometryTests(unittest.TestCase):
    def test_retraction_and_tangent_preserve_each_residue_statistics(self):
        gen=torch.Generator().manual_seed(4);z=torch.randn(3,10,8,generator=gen,dtype=torch.float64);g=torch.randn(z.shape,generator=gen,dtype=z.dtype);z[0,0]=2
        tangent=tangent_gradient(g,z);center=z-z.mean(-1,keepdim=True)
        torch.testing.assert_close(tangent.mean(-1),torch.zeros(3,10,dtype=z.dtype),atol=1e-12,rtol=0)
        torch.testing.assert_close((tangent*center).sum(-1),torch.zeros(3,10,dtype=z.dtype),atol=1e-12,rtol=0)
        projected=retract(z-.01*tangent,z)
        torch.testing.assert_close(projected.mean(-1),z.mean(-1),atol=1e-12,rtol=0)
        torch.testing.assert_close(projected.std(-1),z.std(-1),atol=1e-12,rtol=0)
        torch.testing.assert_close(projected[0,0],z[0,0],atol=0,rtol=0)

    def test_proper_loss_rejects_mirrors_and_has_correct_envelope_gradient(self):
        gen=torch.Generator().manual_seed(9);reference=torch.randn(12,4,3,generator=gen,dtype=torch.float64);rotation,_=torch.linalg.qr(torch.randn(3,3,generator=gen,dtype=torch.float64));rotation[:,0]*=torch.linalg.det(rotation)
        exact=reference@rotation+3
        self.assertLess(float(proper_loss(exact[None],reference,0)[0]),1e-20)
        self.assertGreater(float(proper_loss((reference*torch.tensor([-1.,1.,1.]))[None],reference,0)[0]),.1)
        x=(exact+.1*torch.randn(exact.shape,generator=gen,dtype=exact.dtype))[None].requires_grad_();loss=proper_loss(x,reference,0).sum();gradient,=torch.autograd.grad(loss,x);direction=gradient/gradient.norm();eps=1e-5
        fd=(proper_loss(x.detach()+eps*direction,reference,0)-proper_loss(x.detach()-eps*direction,reference,0))/(2*eps)
        torch.testing.assert_close(fd[0],(gradient*direction).sum(),atol=1e-9,rtol=1e-7)
