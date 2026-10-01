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


def test_paired_change_is_candidate_minus_reference():
    from latentfold.teacher_states import paired_change
    result=paired_change({'a':.75,'b':.5},{'a':.5,'b':.25})
    assert result['difference']==.25
    assert result['ci95']==[.25,.25]


def test_bridge_posterior_noise_and_endpoint_limits():
    from latentfold.teacher_states import bridge_posterior
    z=np.array([[-1.],[1.]])
    at_noise=bridge_posterior(z,[0,1],[0,1],np.zeros((2,1)),0.)
    assert at_noise['true_state_posterior']==.5
    assert at_noise['state_entropy_bits']==1
    assert at_noise['oracle_velocity_mse_floor']==1
    near_endpoint=bridge_posterior(z,[0,1],[0,1],np.zeros((2,1)),.99)
    assert near_endpoint['oracle_state_accuracy']==1
    assert near_endpoint['oracle_velocity_mse_floor']==0
