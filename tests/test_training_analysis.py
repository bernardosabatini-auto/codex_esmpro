import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from summarize_pilot import validate_training_evaluation


class TrainingAnalysisTests(unittest.TestCase):
 def setUp(self):
  self.training=dict(checkpoint_sha256='trained',config=dict(decoder_checkpoint_sha256='decoder'))
  self.manifest=dict(status='complete',completed_predictions=3,
    config=dict(flow_steps=[25],guidance=[2],samples=3,decoder_steps=3,target_ids=['a']),
    checkpoint=dict(sha256='trained'),decoder_checkpoint=dict(sha256='decoder'),
    precision=dict(flow_precision='fp32',decoder_precision='fp32'))
  self.scores=dict(status='complete',usalign=dict(arguments=['-TMscore','1']),
    records=[dict(setting='steps25_cfg2',target_id='a',sample=k,tm_fixed_reference=.5,ca_lddt=.6) for k in range(3)])

 def test_wrong_weights_or_decoder_are_rejected(self):
  validate_training_evaluation(self.training,self.manifest,self.scores)
  for key in ['checkpoint','decoder_checkpoint']:
   changed=copy.deepcopy(self.manifest);changed[key]['sha256']='another-model'
   with self.assertRaises(ValueError):validate_training_evaluation(self.training,changed,self.scores)

 def test_changed_precision_or_correspondence_are_rejected(self):
  changed=copy.deepcopy(self.manifest);changed['precision']['flow_precision']='fp16'
  with self.assertRaises(ValueError):validate_training_evaluation(self.training,changed,self.scores)
  changed=copy.deepcopy(self.scores);changed['usalign']['arguments']=[]
  with self.assertRaises(ValueError):validate_training_evaluation(self.training,self.manifest,changed)
