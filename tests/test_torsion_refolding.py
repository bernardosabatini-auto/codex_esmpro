import copy,json,tempfile,unittest
from pathlib import Path
from latentfold.connected_refold import connected_outcome
from torsion_closure_refolding import require_quality,BOUND_KEYS,file_stats,config_digest,audit_worker
from prepare_overfit import sha


class ConnectedRefoldTests(unittest.TestCase):
    def setUp(self):
        self.raw=dict(coarse_valid=True,motif_drms=.1,motif_ca_rmsd=.1)
        self.rows=[dict(sequence_index=i,coarse_valid=True,sc_tm=.8,scaffold_tm=.8,
            motif_drms=2.,motif_ca_rmsd=2.,flank_edges_valid=True) for i in range(8)]

    def test_cannot_mix_motif_and_global_success_across_sequences(self):
        self.rows[0].update(sc_tm=.4,motif_drms=.1,motif_ca_rmsd=.1)
        result=connected_outcome(self.raw,self.rows,physical_raw=True)
        self.assertFalse(result['complete_strict']);self.assertTrue(result['complete_connected_designable'])

    def test_cannot_mix_connectivity_and_motif_across_sequences(self):
        self.rows[0].update(flank_edges_valid=False,motif_drms=.1,motif_ca_rmsd=.1)
        self.assertFalse(connected_outcome(self.raw,self.rows,physical_raw=True)['complete_strict'])

    def test_same_refold_and_physical_input_required(self):
        self.rows[3].update(motif_drms=.1,motif_ca_rmsd=.1)
        r=connected_outcome(self.raw,self.rows,physical_raw=True)
        self.assertEqual(r['complete_strict_indices'],[3]);self.assertTrue(r['complete_strict'])
        r=connected_outcome(self.raw,self.rows,physical_raw=False)
        self.assertTrue(r['connected_designable']);self.assertFalse(r['complete_connected_designable']);self.assertFalse(r['complete_strict'])

    def test_scaffold_match_and_all_attempts_required(self):
        for r in self.rows:r.update(scaffold_tm=.4,motif_drms=.1,motif_ca_rmsd=.1)
        self.assertFalse(connected_outcome(self.raw,self.rows,physical_raw=True)['connected_designable'])
        with self.assertRaises(ValueError):connected_outcome(self.raw,self.rows[:-1],physical_raw=True)


class TorsionRefoldGateTests(unittest.TestCase):
    def fixture(self):
        rows=[]
        for a in ('generated_cond','native_cond'):
            for i in range(32):
                for k in range(4):rows.append(dict(arm=a,target_id=str(i),generation_slot=k,raw_gate_passed=True,
                    local_geometry=dict(valid=True),hidden_flank_bonds=dict(all_edges_valid=True),junctions=dict(valid=True),
                    refold_eligible_geometry=True,fixed_exact=True))
        d=dict(status='complete',profile_only=False,qualified=True,records=rows,selected=[dict(id=str(i)) for i in range(32)],summary=[])
        a=dict(status='complete',profile_only=False,qualified=True,samples=256,max_replay_angstrom=0,max_endpoint_replay_angstrom=0,summary=[])
        return d,a

    def test_failed_or_filtered_panel_rejected(self):
        d,a=self.fixture();self.assertEqual(require_quality(d,a),128)
        d['records'].pop()
        with self.assertRaises(ValueError):require_quality(d,a)
        d,a=self.fixture()
        for r in d['records']:
            if r['arm']=='generated_cond' and int(r['target_id'])>=11:r['raw_gate_passed']=r['refold_eligible_geometry']=False
        with self.assertRaises(ValueError):require_quality(d,a)

    def test_forged_physical_summary_rejected(self):
        d,a=self.fixture();d['records'][0]['local_geometry']['valid']=False
        with self.assertRaises(ValueError):require_quality(d,a)

    def test_metadata_guard_detects_config_and_file_change(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'file';p.write_text('verified content')
            c=dict(torsion_closure_refold=True,assay='fragment_preference_refold',dependencies=[],teacher_artifacts=[],entries=[])
            for k in BOUND_KEYS:c[k]=str(p);c[k+'_sha256']=sha(p)
            c['cpu_verified_file_stats']=file_stats(c);c['cpu_verified_config_sha256']=config_digest(c);audit_worker(c)
            changed=copy.deepcopy(c);changed['entries']=[dict(name='different')]
            with self.assertRaises(ValueError):audit_worker(changed)
            p.write_text('modified file content')
            with self.assertRaises(ValueError):audit_worker(c)


if __name__=='__main__':unittest.main()
