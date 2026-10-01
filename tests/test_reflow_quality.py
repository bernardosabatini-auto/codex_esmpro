import hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from reflow_quality import native_screen


class QualityGateTests(unittest.TestCase):
    def test_invalid_geometry_cannot_be_rescued_by_higher_accuracy(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'selection.json';p.write_text(json.dumps(dict(tuning=[dict(id=str(i),family=str(i)) for i in range(64)])))
            m=dict(config=dict(selection=str(p),selection_sha256=hashlib.sha256(p.read_bytes()).hexdigest()),scores=[])
            for step,n in ((0,25),(500,10)):
                m['scores'] += [dict(step=step,sampling_steps=n,target_id=str(i),sample=k,ca_lddt=.8 if step==0 else .81,coarse_valid=1.) for i in range(64) for k in range(3)]
            self.assertTrue(native_screen(m,500,10)['passed'])
            for r in m['scores'][-8:]:r['coarse_valid']=0.
            self.assertFalse(native_screen(m,500,10)['passed'])
            m['scores'].pop()
            with self.assertRaisesRegex(ValueError,'incomplete'):native_screen(m,500,10)


if __name__=='__main__':unittest.main()
