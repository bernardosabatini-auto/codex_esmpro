import unittest
import torch
from latentfold.coordinates_only import coordinates_only
from teacher_coordinates_profile_core import selection


class CoordinatesOnlyTests(unittest.TestCase):
    def test_restores_exact_module_even_on_failure(self):
        model=torch.nn.Module().eval();model.confidence_head=torch.nn.Linear(3,3)
        head=model.confidence_head;state={k:v.clone() for k,v in model.state_dict().items()}
        with torch.no_grad():
            with self.assertRaisesRegex(RuntimeError,'failed fold'):
                with coordinates_only(model):
                    self.assertEqual(model.confidence_head(predicted_coords=torch.randn(1,3)),{})
                    raise RuntimeError('failed fold')
        self.assertIs(model.confidence_head,head)
        for key,value in model.state_dict().items():self.assertTrue(torch.equal(value,state[key]))

    def test_rejects_training_gradients_and_nested_context(self):
        model=torch.nn.Module();model.confidence_head=torch.nn.Identity()
        with torch.no_grad(),self.assertRaises(ValueError):
            with coordinates_only(model):pass
        model.eval()
        with self.assertRaises(ValueError):
            with coordinates_only(model):pass
        with torch.no_grad(),coordinates_only(model):
            with self.assertRaises(ValueError):
                with coordinates_only(model):pass

    def test_selection_ignores_scores_and_preserves_archived_seeds(self):
        entries=[dict(name=str(i),bucket=b,length=b-5) for i,b in enumerate((128,128,256,384,512))]
        manifest=dict(config=dict(entries=entries),sequences={e['name']:['A','C'] for e in entries},
                      records=[dict(name=e['name'],sequence_index=i,seed=100+i,sc_tm=i) for e in entries for i in range(2)])
        chosen=selection(manifest)
        self.assertEqual([r['name'] for r in chosen],['0','0','2','2','3','3','4','4'])
        self.assertEqual([r['seed'] for r in chosen],[100,101]*4)


if __name__=='__main__':unittest.main()
