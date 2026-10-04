import json,subprocess,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from submission_snapshot import freeze_submission


class SnapshotTests(unittest.TestCase):
    def test_source_and_entry_configuration_survive_later_edits(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in ['scripts','slurm','runs','configs','reports','tests']:(root/name).mkdir()
            (root/'scripts/train.py').write_text('VERSION=1\n')
            (root/'reports/history.md').write_text('Historical result; not a worker input.\n')
            (root/'tests/test_old.py').write_text('assert True\n')
            config=root/'runs/config.json';config.write_text('{"version":1}')
            script=root/'slurm/test.sbatch';script.write_text(f'#!/bin/bash\ncd {root}\npython scripts/train.py --config runs/config.json\n')
            commands=[['git','init','-q'],['git','add','scripts','slurm','reports','tests'],['git','-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','fixture']]
            for cmd in commands:subprocess.run(cmd,cwd=root,check=True,capture_output=True)
            commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
            frozen,snapshot=freeze_submission(root,script,commit)
            (root/'scripts/train.py').write_text('VERSION=2\n');config.write_text('{"version":2}')
            self.assertEqual((snapshot/'scripts/train.py').read_text(),'VERSION=1\n')
            self.assertEqual(json.loads((snapshot/'entry_configs/0.json').read_text())['version'],1)
            self.assertIn('cd '+str(snapshot),frozen.read_text())
            self.assertEqual((snapshot/'runs').resolve(),root/'runs')
            self.assertTrue((snapshot/'reports').is_dir())
            self.assertFalse((snapshot/'reports/history.md').exists())
            self.assertFalse((snapshot/'tests').exists())
