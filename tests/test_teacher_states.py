import numpy as np
from latentfold.teacher_states import definition,contact_assignments


def test_rigid_pose_does_not_change_contact_assignment():
    rng=np.random.default_rng(31);bb=rng.normal(size=(4,40,4,3)).astype('float32')*5
    state=definition(bb,np.ones(4,dtype=bool),np.ones((4,40)))
    assert state is not None and state['states']>=2
    rotation=np.array([[0,-1,0],[1,0,0],[0,0,1]])
    nearest,errors,labels=contact_assignments(bb@rotation+np.array([13,-7,9]),state,np.ones(4,dtype=bool))
    np.testing.assert_array_equal(nearest,np.arange(4));assert max(errors)<1e-5
    assert len(set(labels))==state['states']
    _,_,invalid=contact_assignments(bb,state,np.zeros(4,dtype=bool));assert (invalid==-1).all()


def test_identical_teachers_do_not_make_distinct_states():
    bb=np.random.default_rng(2).normal(size=(1,40,4,3)).repeat(4,0)
    assert definition(bb,np.ones(4,dtype=bool),np.ones((4,40))) is None
