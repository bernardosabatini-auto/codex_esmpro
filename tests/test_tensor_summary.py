import copy,itertools,unittest
from summarize_tensor_precision import analyze,LAYOUTS,PRECISIONS


def fixture():
    m=dict(status='complete',config=dict(heads=[dict(name=h) for h in ('original','balanced')],targets=[dict(id=str(i)) for i in range(4)]),training_updates_executed=0,micro=[],warmups=[],batches=[],controls=[])
    for shape,bias in [([13,63,117],True),([128,256,256],False),([1024,1024,4096],True)]:
        for precision in ('torch_fp32','tf32','tf32x3'):m['micro'].append(dict(shape=shape,bias=bias,precision=precision,relative_rms=1e-7,max_abs=1e-6))
    for h,t,p,l in itertools.product(('original','balanced'),map(str,range(4)),PRECISIONS,LAYOUTS):
        row=dict(head=h,target_id=t,precision=p,layout=l)
        m['warmups'].append(dict(row,seconds=1))
        for repeat in range(3):m['batches'].append(dict(row,repeat=repeat,seconds=2 if p=='fp32' else 1,peak_reserved_bytes=1000))
        if l!='single_exact':m['controls'].append(dict(row,kind='batching',samples=1,ca_rmsd=.01,ca_lddt=1))
        if p=='tf32x3':m['controls'].append(dict(row,kind='arithmetic',samples=dict(single_exact=1,single_padded=1,batch8=8,batch32=32)[l],ca_rmsd=.01,ca_lddt=1))
    return m


class SummaryTests(unittest.TestCase):
    def test_complete(self):
        d=analyze(fixture());self.assertTrue(d['qualified']);self.assertEqual(d['batch32_speed_ratio'],2)
    def test_failed_long_control_and_micro(self):
        m=fixture();m['controls'][-1]['ca_rmsd']=.201;self.assertFalse(analyze(m)['qualified'])
        m=fixture();m['micro'][-1]['relative_rms']=2e-5;self.assertFalse(analyze(m)['qualified'])
    def test_missing_duplicate_and_nonfinite(self):
        for mode in ('missing','duplicate','nonfinite'):
            m=fixture()
            if mode=='missing':m['batches'].pop()
            elif mode=='duplicate':m['batches'][-1]=copy.deepcopy(m['batches'][-2])
            else:m['controls'][-1]['ca_rmsd']=float('nan')
            with self.assertRaises(ValueError):analyze(m)


if __name__=='__main__':unittest.main()
