import json,tempfile,unittest
from pathlib import Path
from fixed_motif_design import fix_parsed_motifs,verify_fixed_sequences

class FixedMotifTests(unittest.TestCase):
 def test_one_based_positions_and_fragment_only_residues(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'parsed';q=Path(t)/'fixed';p.write_text(json.dumps(dict(name='x',seq='A'*10,seq_chain_A='A'*10))+'\n');entries=[dict(name='x',head='original50',length=10,fixed_start=3,fixed_sequence='CDE')];fix_parsed_motifs(p,q,entries);d=json.loads(p.read_text());self.assertEqual(d['seq'],'AAACDEAAAA');self.assertEqual(d['seq'],d['seq_chain_A']);self.assertEqual(json.loads(q.read_text()),{'x':{'A':[4,5,6]}});verify_fixed_sequences({'x':['AAACDEAAAA']*8},entries)
   with self.assertRaisesRegex(ValueError,'Fixed motif'):verify_fixed_sequences({'x':['A'*10]*8},entries)
 def test_controls_remain_free_and_unexpected_sequence_rejected(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'parsed';q=Path(t)/'fixed';entries=[dict(name='x',head='experimental',length=5,fixed_start=0,fixed_sequence='')];p.write_text(json.dumps(dict(name='x',seq='AAAAA',seq_chain_A='AAAAA')));fix_parsed_motifs(p,q,entries);self.assertEqual(json.loads(q.read_text()),{'x':{'A':[]}})
   p.write_text(json.dumps(dict(name='x',seq='ACAAA',seq_chain_A='ACAAA')))
   with self.assertRaisesRegex(ValueError,'Unexpected input sequence'):fix_parsed_motifs(p,q,entries)
if __name__=='__main__':unittest.main()


class ConstraintDispatchTests(unittest.TestCase):
    def test_new_assay_inputs_cannot_silently_omit_constraints(self):
        from fixed_motif_design import requires_fixed_motifs,verify_fixed_sequences
        row=dict(name='new_assay',length=8,head='guided',fixed_start=2,fixed_sequence='CD')
        self.assertTrue(requires_fixed_motifs([row]))
        self.assertFalse(requires_fixed_motifs([dict(name='free',length=8)]))
        with self.assertRaises(ValueError):requires_fixed_motifs([dict(name='bad',fixed_start=2)])
        with self.assertRaises(ValueError):verify_fixed_sequences({'new_assay':['AAAAAAAA']*8},[row])
        verify_fixed_sequences({'new_assay':['AACDAAAA']*8},[row])
