import copy
import json
from pathlib import Path
import unittest
from test_tail_comparison import TailComparisonTests
from compare_local_geometry import compare
from prepare_overfit import sha


class GeometryComparisonTests(unittest.TestCase):
    def setUp(self):
        fixture = TailComparisonTests(); fixture.setUp(); self.addCleanup(fixture.doCleanups)
        self.full = fixture.full; self.candidates = copy.deepcopy(self.full)
        source = Path(self.full[0]['config']['protocol'])
        recipe = json.loads(source.read_text()); recipe['local_geometry'] = dict(weight=1., maximum_gradient_ratio=.1)
        path = source.with_name('local_recipe.json'); path.write_text(json.dumps(recipe))
        for m in self.candidates:
            m['config']['local_geometry'] = recipe['local_geometry']
            for key in ('protocol', 'followup_protocol'):
                m['config'][key] = str(path); m['config'][key+'_sha256'] = sha(path)
            m['local_geometry_updates'] = [dict(step=i, flow_parameter_grad_norm=1., aux_parameter_grad_norm=2., effective_geometry_weight=.05, aux_to_flow_ratio=.1, geometry_loss=.5) for i in range(1,501)]

    def test_matched_and_retained(self):
        d = compare(self.full, self.candidates, 500)
        self.assertTrue(d['matched']); self.assertTrue(d['replicated_capacity_retained'])
        self.assertEqual(d['comparisons']['11_geometry_all122_vs_full']['coverage32']['difference'], 0)

    def test_confounds_and_bad_gradients_rejected(self):
        for kind in ('gradient','missing','recipe','labels','seed','initial'):
            c = copy.deepcopy(self.candidates)
            if kind == 'gradient': c[0]['local_geometry_updates'][0]['aux_to_flow_ratio'] = .11
            if kind == 'missing': c[0]['local_geometry_updates'].pop()
            if kind == 'recipe': c[0]['config']['local_geometry']['weight'] = 2.
            if kind == 'labels': c[0]['training'][0]['label_choices_sha256'] = 'changed'
            if kind == 'seed': c.pop()
            if kind == 'initial': c[0]['scores'][0]['teacher_ca_lddt'] = .1
            with self.subTest(kind=kind), self.assertRaises(ValueError): compare(self.full, c, 500)


if __name__ == '__main__': unittest.main()
