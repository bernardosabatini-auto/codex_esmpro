import copy,json,tempfile,unittest
from pathlib import Path
from compare_functional_replay import validate_pair
from prepare_overfit import sha


class ReplayComparisonTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);root=Path(self.tmp.name)
        protocol=root/'protocol.json';protocol.write_text(json.dumps(dict(replay=dict(maximum_gradient_ratio=.25,maximum_weight=1.))))
        selection=root/'selection.json';selection.write_text('{}')
        c=dict(checkpoint_sha256='same',learning_rate=.00003,seed=2026100171,profile_report='original')
        self.full=dict(config=c,status='complete',updates=2000,initial_checkpoint_sha256='same')
        cc=dict(c,functional_replay=True,replay_protocol=str(protocol),replay_protocol_sha256=sha(protocol),replay_selection=str(selection),replay_selection_sha256=sha(selection),profile_report='new profile')
        self.candidate=dict(config=cc,status='running',updates=501,initial_checkpoint_sha256='same',functional_replay=dict(reference_unchanged=True,verified_update=500,reference_initial_sha256='same reference',reference_final_sha256='same reference',controls=[dict(bucket=b,max_velocity_error=0.,replay_loss=0.) for b in (128,256,384,512)],updates=[dict(step=i,primary_gradient_norm=1.,replay_gradient_norm=.1,replay_to_primary_ratio=.1,effective_weight=1.,replay_loss=.01) for i in range(1,502)]))

    def test_resource_profile_can_differ_but_primary_recipe_cannot(self):
        validate_pair(self.full,self.candidate,500)
        self.candidate['config']['learning_rate']=.00004
        with self.assertRaisesRegex(ValueError,'primary recipe'):validate_pair(self.full,self.candidate,500)

    def test_uncapped_or_unverified_replay_rejected(self):
        candidate=copy.deepcopy(self.candidate);candidate['functional_replay']['updates'][5]['replay_to_primary_ratio']=.251
        with self.assertRaisesRegex(ValueError,'gradient'):validate_pair(self.full,candidate,500)
        candidate=copy.deepcopy(self.candidate);candidate['functional_replay']['reference_final_sha256']='changed'
        with self.assertRaisesRegex(ValueError,'identity'):validate_pair(self.full,candidate,500)


if __name__=='__main__':unittest.main()
