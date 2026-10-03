import tempfile,unittest
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.teacher_endpoint_pool import TeacherEndpointPool
from latentfold.fragment_conditioning import FragmentAdapter,fragment_features,fragment_flow_loss
from test_fragment_latent_weight import ConstantVelocity


class EndpointPoolTests(unittest.TestCase):
    def test_reproducible_mixture_keeps_fallback_and_primary_rng(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'targets.h5'
            with h5py.File(path,'w') as f:
                f.create_dataset('protein/teacher_z',data=np.stack([np.ones((4,8)),np.ones((4,8))*2]).astype('f4'));f.create_dataset('protein/retained/eligible',data=[0,1]);f.create_dataset('protein/retained/unsupported',data=np.array([],dtype='i8'))
            ids=['protein']*64;conditions=['eligible']*32+['unsupported']*32;reference=torch.zeros(64,4,8);before=torch.get_rng_state()
            pool=TeacherEndpointPool(path,42);target,selected=pool.draw(ids,conditions,reference)
            duplicate,again=TeacherEndpointPool(path,42).draw(ids,conditions,reference)
            self.assertEqual(selected,again);torch.testing.assert_close(target,duplicate,rtol=0,atol=0);torch.testing.assert_close(before,torch.get_rng_state(),rtol=0,atol=0)
            self.assertTrue(any(k>=0 for k in selected[:32]) and any(k==-1 for k in selected[:32]));self.assertEqual(selected[32:],[-1]*32);self.assertEqual(reference.abs().sum(),0);self.assertEqual(target[32:].abs().sum(),0)
            net,adapter=ConstantVelocity(64,4),FragmentAdapter(16);features,keep=fragment_features(torch.zeros(2,8),'AC',length=4,start=1);features=features[None].expand(64,-1,-1);keep=keep[None].expand(64,-1);mask=torch.ones(64,4,dtype=torch.bool)
            baseline,original=fragment_flow_loss(net,adapter,reference,features,keep,mask,generator=torch.Generator().manual_seed(24))
            loss,info=fragment_flow_loss(net,adapter,target,features,keep,mask,generator=torch.Generator().manual_seed(24),null_target=reference)
            self.assertTrue(info['dropped'].any())
            for key in ['noise','t','dropped']:torch.testing.assert_close(original[key],info[key],rtol=0,atol=0)
            torch.testing.assert_close(info['target'][info['dropped']],reference[info['dropped']],rtol=0,atol=0)
            torch.testing.assert_close(info['target'][~info['dropped']],target[~info['dropped']],rtol=0,atol=0)


if __name__=='__main__':unittest.main()
