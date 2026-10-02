import copy,unittest
from analyze_sampling_saturation import analyze

class SaturationTests(unittest.TestCase):
    def fixture(self):
        settings=dict(original='cfg2/latent',candidate='cfg1/latent',teacher='steps50',teacher128='steps50')
        sources={}
        for name,setting in settings.items():
            curve={'1':.25,'4':.5,'16':.5,'32':.5 if name in ('original','candidate') else .75}
            if name=='teacher128':curve['128']=1.
            sources[name]=dict(status='complete',definitions={str(i):{'fixed':i} for i in range(16)},rows=[dict(target_id=str(i),family=str(i),setting=setting,contact_state_count=4,coverage={'2.0':dict(curve)}) for i in range(16)])
        return sources
    def test_plateau_and_extension(self):
        d=analyze(self.fixture())
        self.assertEqual(d['increments']['candidate']['16_to_32']['ci95'],[0,0])
        self.assertEqual(d['increments']['teacher128']['32_to_128']['difference'],.25)
    def test_changed_definitions_prefix_or_coverage_rejected(self):
        for mode in ('definition','prefix','family','nonmonotonic'):
            d=copy.deepcopy(self.fixture())
            if mode=='definition':d['candidate']['definitions']['0']['fixed']=99
            if mode=='prefix':d['teacher128']['rows'][0]['coverage']['2.0']['32']=.8
            if mode=='family':d['candidate']['rows'].pop()
            if mode=='nonmonotonic':d['candidate']['rows'][0]['coverage']['2.0']['32']=.25
            with self.subTest(mode=mode),self.assertRaises(ValueError):analyze(d)

if __name__=='__main__':unittest.main()
