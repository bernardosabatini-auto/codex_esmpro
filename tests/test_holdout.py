import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_holdout import parse_cif

class HoldoutTests(unittest.TestCase):
 def test_label_sequence_mapping_preserves_missing_residues(self):
  cols=('auth_asym_id','label_seq_id','label_atom_id','label_comp_id','label_alt_id','Cartn_x','Cartn_y','Cartn_z','auth_seq_id','pdbx_PDB_ins_code','pdbx_PDB_model_num')
  text='data_test\nloop_\n'+''.join('_atom_site.'+c+'\n' for c in cols)
  text+='\n'.join(f'A {i} CA ALA . {i} 0 0 {i+100} ? 1' for i in range(1,61) if i!=25)+'\n#\n'
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'test.cif';p.write_text(text)
   result=parse_cif(p,'A','A'*60)
   self.assertNotIn(24,result['observed_indices']);self.assertEqual(sum(not x for x in result['adjacent']),1)
   self.assertEqual(result['residue_map'][0]['auth_seq_id'],'101')
   self.assertEqual(result['backbone_complete'],0)
   with self.assertRaises(ValueError):parse_cif(p,'A','G'+'A'*59)
