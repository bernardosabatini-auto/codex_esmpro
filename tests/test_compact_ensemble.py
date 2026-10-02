import unittest
from prepare_compact_ensemble import validate_reference


class ReferenceTests(unittest.TestCase):
    def test_same_pipeline_except_compact(self):
        c=dict(checkpoint_sha256='abc',primary_guidance=1,flow_steps=25,checkpoint_selection=dict(step=500));h=dict(checkpoint_sha256='abc')
        validate_reference(c,h)
        for key,value in [('checkpoint_sha256','other'),('primary_guidance',2),('flow_steps',22),('flow_solver','midpoint'),('flow_time_power',.75),('compact_condition',True),('checkpoint_selection',dict(step=2000))]:
            with self.subTest(key=key),self.assertRaises(ValueError):validate_reference(dict(c,**{key:value}),h)


if __name__=='__main__':unittest.main()
