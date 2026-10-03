import copy
import types
import unittest
import torch
from latentfold.native_anchors import decode_native_anchors
from native_anchor_calibration import native_pair


def row(slot,error=1.):
    raw=dict(coarse_valid=True,motif_ca_rmsd=error,motif_drms=error)
    return dict(target_id='protein',generation_slot=slot,full_native_ca_rmsd=.1,raw=raw,
                refolds=[dict(raw,sequence_index=k,sc_tm=.8,scaffold_tm=.8) for k in range(8)])


class NativeAnchorTests(unittest.TestCase):
    def test_two_reproducible_decoder_draws_without_changing_latents(self):
        calls=[]
        def decoder(z,mask,noise,return_backbone):
            calls.append(noise.clone());self.assertEqual(z.shape,(2,12,8));self.assertTrue(mask.all())
            return None,noise.reshape(2,12,4,3)
        decoder.fm=types.SimpleNamespace(scale_ref=2.)
        latent=torch.arange(96).reshape(12,8).float();before=latent.clone()
        z,bb=decode_native_anchors(decoder,latent,target_id='train',seed=2026100415)
        z2,bb2=decode_native_anchors(decoder,latent,target_id='train',seed=2026100415)
        self.assertTrue(torch.equal(latent,before));self.assertTrue(torch.equal(z[0],latent));self.assertTrue(torch.equal(z[1],latent))
        self.assertTrue(torch.equal(bb,bb2));self.assertFalse(torch.equal(bb[0],bb[1]))

    def test_confirmation_uses_other_decoder_and_same_negative(self):
        native=[row(0),row(1)];candidates=[row(k,3+k) for k in range(4)]
        p=native_pair(native,candidates);self.assertTrue(p['confirmed']);self.assertEqual(p['negative_slot'],3)
        for r in candidates[3]['refolds'][4:]:r.update(motif_ca_rmsd=1.,motif_drms=1.)
        candidates[3]['raw'].update(motif_ca_rmsd=1.,motif_drms=1.)
        # Keep discovery weak while confirmation improves; another negative cannot replace it.
        for r in candidates[3]['refolds'][:4]:r.update(motif_ca_rmsd=6.,motif_drms=6.)
        p=native_pair(native,candidates);self.assertEqual(p['negative_slot'],3);self.assertFalse(p['confirmed'])
        p=native_pair([row(0),row(1,1.5)],[row(k,3+k) for k in range(4)])
        self.assertTrue(p['eligible']);self.assertFalse(p['native_both_strict']);self.assertFalse(p['confirmed'])

    def test_both_decodes_must_preserve_full_native(self):
        native=[row(0),row(1)];native[1]['full_native_ca_rmsd']=1.01
        self.assertFalse(native_pair(native,[row(k,3) for k in range(4)])['confirmed'])
        native[1]['full_native_ca_rmsd']=float('nan')
        with self.assertRaises(ValueError):native_pair(native,[row(k,3) for k in range(4)])


if __name__=='__main__':unittest.main()
