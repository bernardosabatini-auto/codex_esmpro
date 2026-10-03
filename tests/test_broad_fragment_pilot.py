import copy,json,unittest
from pathlib import Path
from broad_fragment_pilot import qualify


class BroadDataGateTests(unittest.TestCase):
    def setUp(self):
        self.spec=json.loads((Path(__file__).resolve().parents[1]/'configs/fragment_broad_pilot_protocol.json').read_text())
        self.records=[dict(source_ca_error=0.,full_encoding_rmse=0.,source_valid=True,decoded_valid=True,decoded_ca_rmsd=.2,fragments=[dict(motif_ca_rmsd=.2,motif_drms=.2) for _ in range(9)]) for _ in range(64)]
        self.controls=[dict(kind='historical',latent_max_abs=0.) for _ in range(4)]+[dict(kind='pose',latent_max_abs=0.,coordinate_max_abs=0.) for _ in range(64)]+[dict(kind='repeat',ca_rmsd=0.,ca_lddt=1.) for _ in range(4)]

    def test_good_crops_cannot_hide_invalid_full_endpoints(self):
        self.assertTrue(qualify(self.records,self.controls,self.spec)['data_gate_passed'])
        for r in self.records[:7]:r['decoded_valid']=False
        self.assertFalse(qualify(self.records,self.controls,self.spec)['data_gate_passed'])

    def test_bad_source_parity_or_control_rejects_the_pilot(self):
        self.records[0]['full_encoding_rmse']=.051
        with self.assertRaises(ValueError):qualify(self.records,self.controls,self.spec)
        self.records[0]['full_encoding_rmse']=0.
        self.controls[0]['latent_max_abs']=float('nan')
        with self.assertRaises(ValueError):qualify(self.records,self.controls,self.spec)

    def test_missing_fragment_cannot_change_the_denominator(self):
        self.records[0]['fragments'].pop()
        with self.assertRaises(ValueError):qualify(self.records,self.controls,self.spec)
