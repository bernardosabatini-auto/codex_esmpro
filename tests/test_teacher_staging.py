import tempfile,unittest
from pathlib import Path
from teacher_staging import stage
from prepare_overfit import sha


class TeacherStagingTests(unittest.TestCase):
    def test_all_files_exact_and_original_untouched(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);records=[]
            for name,text in [('config.json','{}'),('model.safetensors','archived weights'),('tokenizer.json','tokenizer')]:
                p=root/name;p.write_text(text);records.append(dict(path=str(p),sha256=sha(p)))
            result=stage(records,root/'local')
            self.assertEqual(set(p.name for p in result.iterdir()),{Path(r['path']).name for r in records})
            for r in records:
                self.assertEqual(sha(result/Path(r['path']).name),r['sha256']);self.assertEqual(sha(r['path']),r['sha256'])
            with self.assertRaises(FileExistsError):stage(records,root/'local')

    def test_changed_weight_is_not_left_as_usable_copy(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);p=root/'weights';p.write_text('original');r=dict(path=str(p),sha256=sha(p));p.write_text('changed')
            with self.assertRaises(ValueError):stage([r],root/'local')
            self.assertFalse((root/'local/weights').exists());self.assertEqual(p.read_text(),'changed')

    def test_basename_collision_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            with self.assertRaises(ValueError):stage([dict(path='/a/weights'),dict(path='/b/weights')],root/'local')


if __name__=='__main__':unittest.main()
