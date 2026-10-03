import unittest
from unittest.mock import patch
import numpy as np
from prepare_fragment_extra_development import read_observed_backbone


class ExperimentalMappingTests(unittest.TestCase):
    def columns(self):
        rows=[]
        for k,res in enumerate(('ALA','CYS','ASP'),2):
            for atom in ('N','CA','C','O'):
                rows.append(dict(auth_asym_id='A',label_seq_id=str(k),label_atom_id=atom,label_comp_id=res,label_alt_id='.',Cartn_x=str(k),Cartn_y=str(('N','CA','C','O').index(atom)),Cartn_z='0',auth_seq_id=str(k+10),pdbx_PDB_ins_code='?',pdbx_PDB_model_num='1'))
        return {'_atom_site.'+key:[r[key] for r in rows] for key in rows[0]}

    def test_terminally_trimmed_contiguous_construct_has_explicit_atom_order(self):
        with patch('prepare_fragment_extra_development.MMCIF2Dict',return_value=self.columns()):
            bb,mapping=read_observed_backbone('unused','A','ACD')
        self.assertEqual(bb.shape,(3,4,3));self.assertEqual([r['label_seq_id'] for r in mapping],[2,3,4]);np.testing.assert_array_equal(bb[0,:,1],[0,1,2,3])

    def test_missing_internal_atom_cannot_be_hidden_by_residue_compression(self):
        columns=self.columns()
        for key in columns:columns[key].pop(7)
        with patch('prepare_fragment_extra_development.MMCIF2Dict',return_value=columns),self.assertRaises(ValueError):read_observed_backbone('unused','A','ACD')

    def test_sequence_change_or_ambiguous_atom_is_rejected(self):
        with patch('prepare_fragment_extra_development.MMCIF2Dict',return_value=self.columns()),self.assertRaises(ValueError):read_observed_backbone('unused','A','ACE')
        columns=self.columns()
        for key in columns:columns[key].append(columns[key][0])
        columns['_atom_site.Cartn_x'][-1]='999'
        with patch('prepare_fragment_extra_development.MMCIF2Dict',return_value=columns),self.assertRaises(ValueError):read_observed_backbone('unused','A','ACD')
