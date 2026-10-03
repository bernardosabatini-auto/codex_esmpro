import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from fragment_fixed_coverage import collect_covered


class NativeBudgetTests(unittest.TestCase):
    def test_new_native_budget_prevents_historical_native_attempt_pooling(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'config.json';path.write_text(json.dumps({}));reused=[]
            for arm in ('control','candidate'):
                source=dict(arm=arm,config=str(path),run=arm,native_run='forbidden_old_native')
                reused.append((source,dict(target_id='shared',slot=1),None))
            def complete(run,current):
                self.assertNotEqual(run,'forbidden_old_native')
                return Path(run),{'config':{}},{}
            c=dict(entries=[dict(arm='native',target_id='shared')],usalign='unused')
            with patch('fragment_fixed_coverage.split_coverage',return_value=({},reused)),patch('fragment_fixed_coverage._completed_source',side_effect=complete) as called,patch('fragment_fixed_coverage._record',side_effect=lambda *args:dict(arm=args[4])):
                records=collect_covered(c,{})
            self.assertEqual([r['arm'] for r in records],['control','candidate']);self.assertEqual(called.call_count,2)
