import unittest
from evaluate_movable_motif_full import summarize
from movable_motif_refolding import require_quality


class MovableMotifRefoldGateTests(unittest.TestCase):
    def fixture(self):
        rows=[]
        for pose in ('fixed_pose','free_pose'):
            for arm in ('generated_cond','native_cond'):
                for i in range(32):
                    for slot in range(4):
                        overlap=int(pose=='fixed_pose' and arm=='generated_cond' and i==0)
                        rows.append(dict(pose_arm=pose,arm=arm,target_id=str(i),family=str(i),generation_slot=slot,
                            raw_gate_passed=True,local_geometry=dict(valid=True),hidden_flank_bonds=dict(all_edges_valid=True),
                            junctions=dict(valid=True),refold_eligible_geometry=True,steric_eligible=not overlap,
                            nonbonded=dict(pairs_below_threshold=overlap),far_exact=True,motif_rigid_rmsd=0.,
                            motif_pair_distance_max_error=0.,solver=dict(motif_displacement_rmsd=0.,torsion_rms_degrees=0.)))
        summary,pairs,qualified=summarize(rows)
        d=dict(status='complete',profile_only=False,qualified=qualified,records=rows,
               selected=[dict(id=str(i)) for i in range(32)],summary=summary,paired=pairs)
        a=dict(status='complete',qualified=True,records=512,replay_max_abs=0,matched_profile_outputs=64,
               provenance_passed=True,rescore_passed=True)
        return d,a

    def test_reject_profile_filtered_and_duplicate_outputs(self):
        d,a=self.fixture();self.assertEqual(require_quality(d,a),128)
        d['profile_only']=True
        with self.assertRaises(ValueError):require_quality(d,a)
        d,a=self.fixture();d['records'].pop()
        with self.assertRaises(ValueError):require_quality(d,a)
        d,a=self.fixture();d['records'][0]=d['records'][1]
        with self.assertRaises(ValueError):require_quality(d,a)

    def test_geometry_cannot_hide_atomic_overlap_or_motif_deformation(self):
        d,a=self.fixture();d['records'][-1]['nonbonded']['pairs_below_threshold']=1
        with self.assertRaises(ValueError):require_quality(d,a)
        d,a=self.fixture();d['records'][-1]['motif_rigid_rmsd']=.1
        with self.assertRaises(ValueError):require_quality(d,a)
        d,a=self.fixture();a['replay_max_abs']=1e-5
        with self.assertRaises(ValueError):require_quality(d,a)


if __name__=='__main__':unittest.main()
