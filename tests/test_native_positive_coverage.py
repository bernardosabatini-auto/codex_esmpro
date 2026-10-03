import copy
import unittest
from latentfold.fragment_designability import same_refold_success
from native_positive_coverage import qualify_sources


class PositiveCoverageTests(unittest.TestCase):
    def inputs(self):
        selected=[dict(id='short',length=100,bucket=128),dict(id='long',length=300,bucket=384)];records=[];generation=[]
        for source in selected:
            for slot in (0,1):
                raw=dict(coarse_valid=True,motif_ca_rmsd=.2,motif_drms=.2);refolds=[dict(raw,sc_tm=.8,scaffold_tm=.8) for _ in range(8)]
                r=dict(target_id=source['id'],generation_slot=slot,raw=raw,refolds=refolds,**same_refold_success(raw,refolds),scaffold_successful_refold_indices=list(range(8)),scaffold_joint_success=True)
                records.append(r);generation.append(dict(target_id=source['id'],generation_slot=slot,raw_gate_passed=True,full_native_ca_rmsd=.2))
        return records,generation,selected,dict(minimum_new_qualified=2,minimum_buckets=2,minimum_new_long_qualified=1)

    def test_both_decodes_and_full_reference_required(self):
        args=self.inputs();gate,rows=qualify_sources(*args);self.assertTrue(gate['qualified'])
        args[1][-1]['full_native_ca_rmsd']=1.01;gate,rows=qualify_sources(*args)
        self.assertFalse(gate['qualified']);self.assertEqual(gate['new_qualified'],1)

    def test_no_cross_decoder_pooling(self):
        args=self.inputs();r=args[0][-1]
        for refold in r['refolds']:refold['motif_ca_rmsd']=2.
        r.update(same_refold_success(r['raw'],r['refolds']),scaffold_successful_refold_indices=[],scaffold_joint_success=False)
        gate,rows=qualify_sources(*args);self.assertFalse(gate['qualified']);self.assertFalse(rows[-1]['qualified'])

    def test_missing_attempts_or_decodes_fail(self):
        args=self.inputs();args[0][-1]['refolds'].pop()
        with self.assertRaises(ValueError):qualify_sources(*args)
        args=self.inputs();args[0].pop()
        with self.assertRaises(ValueError):qualify_sources(*args)


if __name__=='__main__':unittest.main()
