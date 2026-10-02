import copy,unittest
from prepare_expanded_ensemble import qualified

class ExpandedEnsembleTests(unittest.TestCase):
    def fixture(self):
        capacity=dict(step=2000,matched=True,replicated_capacity_passed=True,capacity_checks={str(s):dict(passed=True) for s in (2026100171,2026100181)})
        transfer=dict(step=2000,summaries={f'seed{s}_balanced_cfg1':dict(quality_passed=True) for s in (2026100171,2026100181)})
        return capacity,transfer
    def test_both_declared_seed_settings_can_qualify(self):
        c,t=self.fixture()
        for s in (2026100171,2026100181):self.assertEqual(qualified(c,t,f'seed{s}_balanced',1,step=2000),f'seed{s}_balanced_cfg1')
    def test_failed_replication_quality_or_endpoint_cannot_advance(self):
        for mode in ('replication','capacity','quality','endpoint','head','guidance'):
            c,t=self.fixture();head='seed2026100171_balanced';guidance=1
            if mode=='replication':c['replicated_capacity_passed']=False
            if mode=='capacity':c['capacity_checks']['2026100171']['passed']=False
            if mode=='quality':t['summaries'][head+'_cfg1']['quality_passed']=False
            if mode=='endpoint':t['step']=500
            if mode=='head':head='seed2026100171_empirical'
            if mode=='guidance':guidance=2
            with self.subTest(mode=mode),self.assertRaises(ValueError):qualified(c,t,head,guidance,step=2000)

if __name__=='__main__':unittest.main()
