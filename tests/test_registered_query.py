import unittest
from check_registered_jobs import resolve


class RegisteredQueryTests(unittest.TestCase):
    def setUp(self):self.jobs=[dict(id='123',script='slurm/ours.sbatch'),dict(id='456',tasks=['456_0','456_1'],script='slurm/array.sbatch')]
    def test_exact_registered_id_or_script(self):
        self.assertEqual(resolve(self.jobs,ids=['123','456_0']),['123','456_0'])
        self.assertEqual(resolve(self.jobs,scripts=['slurm/array.sbatch']),['456_0','456_1'])
    def test_typo_and_partial_matching_rejected(self):
        for ids in (['124'],['12'],['123,124'],['456_2']):
            with self.assertRaises(ValueError):resolve(self.jobs,ids=ids)
        with self.assertRaises(ValueError):resolve(self.jobs,scripts=['ours'])
        with self.assertRaises(ValueError):resolve(self.jobs+[self.jobs[0]],scripts=['slurm/ours.sbatch'])


if __name__=='__main__':unittest.main()
