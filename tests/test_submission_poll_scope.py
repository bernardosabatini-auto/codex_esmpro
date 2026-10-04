import copy
import unittest
from submit_registered import jobs_requiring_poll


class SubmissionPollTests(unittest.TestCase):
    def inputs(self):
        jobs=[dict(id='1',state='SUBMITTED',gpus=1),dict(id='2',state='SUBMITTED',gpus=2,tasks=['2_0','2_1']),dict(id='3',state='SUBMITTED',gpus=1)]
        state=dict(jobs={'1':dict(handled=True,tasks={'1':dict(state='COMPLETED')}),
                         '2':dict(handled=True,tasks={'2_0':dict(state='COMPLETED'),'2_1':dict(state='FAILED')})})
        return dict(jobs=jobs),state

    def test_only_fully_handled_terminal_jobs_skipped(self):
        registry,state=self.inputs();self.assertEqual([j['id'] for j in jobs_requiring_poll(registry,state)],['3'])

    def test_completing_unknown_and_missing_tasks_always_live_polled(self):
        registry,state=self.inputs()
        for value in ('COMPLETING','RUNNING','PENDING','UNKNOWN'):
            changed=copy.deepcopy(state);changed['jobs']['2']['tasks']['2_1']['state']=value
            self.assertEqual([j['id'] for j in jobs_requiring_poll(registry,changed)],['2','3'])
        changed=copy.deepcopy(state);del changed['jobs']['2']['tasks']['2_1']
        self.assertEqual([j['id'] for j in jobs_requiring_poll(registry,changed)],['2','3'])

    def test_unhandled_terminal_and_new_registration_live_polled(self):
        registry,state=self.inputs();state['jobs']['1']['handled']=False
        self.assertEqual([j['id'] for j in jobs_requiring_poll(registry,state)],['1','3'])
        self.assertEqual(jobs_requiring_poll(registry,{}),registry['jobs'])

    def test_foreign_cache_does_not_expand_scheduler_scope(self):
        registry,state=self.inputs();state['jobs']['999']=dict(handled=False,tasks={'999':dict(state='RUNNING')})
        self.assertEqual([j['id'] for j in jobs_requiring_poll(registry,state)],['3'])
        registry['jobs'].append(copy.deepcopy(registry['jobs'][0]))
        with self.assertRaises(ValueError):jobs_requiring_poll(registry,state)


if __name__=='__main__':unittest.main()
