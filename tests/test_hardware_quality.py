"""Hardware qualification retains both structural and reference-quality gates."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_overfit import sha
from summarize_midpoint import cross_hardware_quality


class HardwareTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.families={str(i):str(i) for i in range(64)}
        rows=[dict(setting='euler_25_cfg2',target_id=i,sample=k,ca_lddt=.8,coarse_valid=1.) for i in self.families for k in range(3)]
        config=dict(selection_sha256='selection',evaluation_seed=1)
        prior=dict(status='complete',checkpoint_sha256='checkpoint',config=config,scores=rows)
        path=Path(self.tmp.name)/'baseline.json';path.write_text(json.dumps(prior))
        self.m=dict(checkpoint_sha256='checkpoint',config=dict(config,cross_hardware_reference=dict(manifest=str(path),manifest_sha256=sha(path))),scores=copy.deepcopy(rows),cross_hardware_controls=[dict(target_id=i,sample=k,ca_rmsd=.03,ca_lddt=1.) for i in self.families for k in range(3)])

    def test_small_score_difference_with_structural_agreement(self):
        self.m['scores'][0]['ca_lddt']+=.000344
        self.assertTrue(cross_hardware_quality(self.m,self.families)['passed'])

    def test_geometry_quality_and_completeness_all_required(self):
        for kind in ('shape','reference','validity','missing'):
            m=copy.deepcopy(self.m)
            if kind=='shape':m['cross_hardware_controls'][0]['ca_rmsd']=.21
            if kind=='reference':
                for r in m['scores']:r['ca_lddt']-=.02
            if kind=='validity':
                for r in m['scores'][:2]:r['coarse_valid']=0.
            if kind=='missing':
                m['cross_hardware_controls'].pop()
                with self.assertRaises(ValueError):cross_hardware_quality(m,self.families)
            else:self.assertFalse(cross_hardware_quality(m,self.families)['passed'])


if __name__=='__main__':unittest.main()
