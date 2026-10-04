import unittest
from threading import Event
from ordered_cpu_scoring import OrderedCPUScoring

class ScoringTests(unittest.TestCase):
    def test_order_and_identical_serial_results(self):
        for enabled in (False,True):
            scorer=OrderedCPUScoring(enabled,limit=2);rows=[]
            try:
                for i in range(20):rows.extend(scorer.submit(lambda x:dict(index=x,value=x*x),i))
                rows.extend(scorer.drain(wait=True))
                self.assertEqual(rows,[dict(index=i,value=i*i) for i in range(20)])
            finally:scorer.close()

    def test_submit_does_not_wait_for_first_cpu_result(self):
        gate=Event();scorer=OrderedCPUScoring(True)
        try:
            self.assertEqual(scorer.submit(lambda:gate.wait(2)),[])
            gate.set();self.assertEqual(scorer.drain(wait=True),[True])
        finally:gate.set();scorer.close()

    def test_cpu_failures_propagate(self):
        def fail():raise ValueError('Scorer failed')
        for enabled in (False,True):
            scorer=OrderedCPUScoring(enabled)
            try:
                with self.assertRaisesRegex(ValueError,'Scorer failed'):
                    scorer.submit(fail);scorer.drain(wait=True)
            finally:scorer.close()

if __name__=='__main__':unittest.main()
