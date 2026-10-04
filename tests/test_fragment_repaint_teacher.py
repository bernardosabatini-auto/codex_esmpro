import unittest
import torch
from test_generative import GenerativeTests
from latentfold.generative import sample_unconditional
from fragment_repaint_teacher_core import eligibility


class TeacherInputs(GenerativeTests):
    def test_scaffold_codes_do_not_enter_sampler(self):
        keep=torch.zeros_like(self.mask);keep[:,1:3]=True
        motif=torch.randn_like(self.noise);other=torch.where(keep[...,None],motif,torch.ones_like(motif)*100)
        eps=torch.randn_like(self.noise)
        kw=dict(noise=self.noise,steps=3,motif_noise=eps,repaint=3,fresh_noise=lambda i,j:eps*(i+j+1))
        a=sample_unconditional(self.net,self.esm,self.mask,fixed=(motif,keep),**kw)
        b=sample_unconditional(self.net,self.esm,self.mask,fixed=(other,keep),**kw)
        torch.testing.assert_close(a,b,rtol=0,atol=0)
        changed=motif.clone();changed[keep]=0
        d=sample_unconditional(self.net,self.esm,self.mask,fixed=(changed,keep),**kw)
        self.assertGreater(float((a-d).abs().max()),0)


class TeacherEligibility(unittest.TestCase):
    def test_logical_upperbounds_require_full_population(self):
        rows=[dict(target_id=str(i//4),generation_slot=i%4,raw_gate_passed=i<9,coarse_valid=i<45) for i in range(128)]
        self.assertTrue(eligibility(rows)['qualified'])
        rows[8]['raw_gate_passed']=False
        self.assertFalse(eligibility(rows)['qualified'])
        with self.assertRaises(ValueError):eligibility(rows[:-1])
        with self.assertRaises(ValueError):eligibility(rows[:-1]+[rows[0]])

class TeacherRefolding(unittest.TestCase):
    def test_ineligible_or_filtered_generation_cannot_refold(self):
        from fragment_repaint_teacher_refolding import require_generation
        rows=[dict(arm='oracle_repaint',target_id=str(i//4),generation_slot=i%4,raw_gate_passed=i<9,coarse_valid=i<45) for i in range(128)]
        d=dict(status='complete',oracle_teacher=True,controls=8,records=rows,refold_eligibility=eligibility(rows))
        require_generation(d)
        for key,value in [('oracle_teacher',False),('controls',7),('records',rows[:-1])]:
            with self.assertRaises(ValueError):require_generation(dict(d,**{key:value}))
        rows[44]['coarse_valid']=False;d['refold_eligibility']=eligibility(rows)
        with self.assertRaises(ValueError):require_generation(d)

    def test_advancement_requires_joint_success_and_designability(self):
        from compare_fragment_repaint_teacher import teacher_gate
        row=dict(strong=9,strong_families=7,designable=45)
        self.assertTrue(teacher_gate(row))
        for key,value in [('strong',8),('strong_families',6),('designable',44)]:
            self.assertFalse(teacher_gate(dict(row,**{key:value})))

    def test_watcher_import_requires_only_standard_library(self):
        import subprocess,sys
        from pathlib import Path
        scripts=Path(__file__).resolve().parents[1]/"scripts"
        subprocess.run([sys.executable,"-I","-S","-c",f"import sys;sys.path.insert(0,{str(scripts)!r});import compare_fragment_repaint_teacher"],check=True,capture_output=True)

    def test_watcher_only_accepts_four_own_completed_jobs(self):
        import json,tempfile
        from pathlib import Path
        from compare_fragment_repaint_teacher import ready_command
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/'runs').mkdir();(root/'reports').mkdir()
            self.assertIsNone(ready_command(root))
            plan=dict(oracle_teacher_comparison=True,jobs=[None]*4);path=root/'runs/fragment_repaint_teacher_comparison.json';path.write_text(json.dumps(plan))
            self.assertIsNone(ready_command(root))
            plan['jobs']=['1','2','3','4'];path.write_text(json.dumps(plan));(root/'runs/jobs.json').write_text('{"jobs":[]}')
            with self.assertRaises(ValueError):ready_command(root)
            (root/'runs/jobs.json').write_text(json.dumps(dict(jobs=[dict(id=i,completion_action='summarize_fragment_preference_refold') for i in plan['jobs']])))
            self.assertIsNone(ready_command(root))
            for i in plan['jobs']:(root/f'reports/fragment_preference_refold_{i}.json').write_text('{"status":"complete"}')
            self.assertIsNotNone(ready_command(root))
            plan['jobs'][-1]='1';path.write_text(json.dumps(plan))
            with self.assertRaises(ValueError):ready_command(root)


if __name__=='__main__':unittest.main()
