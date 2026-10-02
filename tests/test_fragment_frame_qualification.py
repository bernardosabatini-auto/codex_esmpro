import json,tempfile,unittest
from pathlib import Path
from frame_target_audit import qualify_frame_data
from prepare_overfit import sha


class FrameQualificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.c={'fragments_sha256':'fixed-fragments'}
        self.put('target_frame_protocol',{});self.put('frame_data_manifest',{'status':'complete'})
        self.put('frame_data_report',dict(status='complete',training_gate_passed=False,manifest_sha256=self.c['frame_data_manifest_sha256'],fragments_sha256='fixed-fragments'))

    def put(self,key,value):
        p=self.root/(key+'.json');p.write_text(json.dumps(value));self.c[key]=str(p);self.c[key+'_sha256']=sha(p)

    def confirmation(self):
        self.put('frame_confirmation_protocol',{'limits':'fixed-before-fresh-noise'})
        self.put('frame_confirmation_manifest',dict(status='complete',config=dict(data_manifest_sha256=self.c['frame_data_manifest_sha256'],data_report_sha256=self.c['frame_data_report_sha256'],protocol_sha256=self.c['frame_confirmation_protocol_sha256'])))
        self.put('frame_confirmation_report',dict(status='complete',relative_label_gate_passed=True,original_absolute_gate_passed=False,manifest_sha256=self.c['frame_confirmation_manifest_sha256'],data_manifest_sha256=self.c['frame_data_manifest_sha256'],fragments_sha256='fixed-fragments'))

    def test_failed_original_gate_needs_separate_evidence(self):
        with self.assertRaises(ValueError):qualify_frame_data(self.c)
        self.confirmation();self.assertEqual(qualify_frame_data(self.c),'revised_fresh_noise_relative_gate')
        self.assertFalse(json.loads(Path(self.c['frame_data_report']).read_text())['training_gate_passed'])

    def test_rejects_changed_protocol_and_wrong_corpus(self):
        self.confirmation();Path(self.c['frame_confirmation_protocol']).write_text('{}')
        with self.assertRaises(ValueError):qualify_frame_data(self.c)
        self.confirmation();d=json.loads(Path(self.c['frame_confirmation_report']).read_text());d['fragments_sha256']='other';self.put('frame_confirmation_report',d)
        with self.assertRaises(ValueError):qualify_frame_data(self.c)

    def test_rejects_failed_confirmation(self):
        self.confirmation();d=json.loads(Path(self.c['frame_confirmation_report']).read_text());d['relative_label_gate_passed']=False;self.put('frame_confirmation_report',d)
        with self.assertRaises(ValueError):qualify_frame_data(self.c)


if __name__=='__main__':unittest.main()
