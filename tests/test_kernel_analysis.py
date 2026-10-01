import sqlite3,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from summarize_kernels import kernel_summary


class KernelAnalysisTests(unittest.TestCase):
    def test_async_kernel_is_attributed_by_launch_not_execution_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'trace.sqlite';con=sqlite3.connect(path)
            con.executescript('''
              create table NVTX_EVENTS(start integer,end integer,text text);
              create table CUPTI_ACTIVITY_KIND_KERNEL(start integer,end integer,demangledName integer,correlationId integer);
              create table CUPTI_ACTIVITY_KIND_RUNTIME(start integer,correlationId integer);
              create table StringIds(id integer,value text);
              insert into NVTX_EVENTS values(0,1000,'training_kernels::test');
              insert into NVTX_EVENTS values(0,100,'component::test::forward');
              insert into NVTX_EVENTS values(100,600,'component::test::backward_clip');
              insert into CUPTI_ACTIVITY_KIND_KERNEL values(250,350,1,1),(350,400,2,2),(1100,1500,1,3);
              insert into CUPTI_ACTIVITY_KIND_RUNTIME values(50,1),(150,2),(1050,3);
              insert into StringIds values(1,'forward kernel'),(2,'backward kernel');
            ''');con.commit();con.close()
            rows=[dict(length=128,batch=128,self_condition=False,batches=[dict(nvtx_range='training_kernels::test')])]
            result=kernel_summary(path,rows)[0]
            self.assertEqual(result['kernel_count'],2)
            self.assertAlmostEqual(result['stage_kernel_fraction']['forward'],2/3)
            self.assertAlmostEqual(result['stage_kernel_fraction']['backward_clip'],1/3)
            rows[0]['batches'].append(dict(nvtx_range='missing'))
            with self.assertRaisesRegex(ValueError,'coverage'):kernel_summary(path,rows)


if __name__=='__main__':unittest.main()
