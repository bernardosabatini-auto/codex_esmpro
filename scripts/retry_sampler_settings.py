"""Step counts must be explicit in both head and frozen protocol."""


def native_steps(head,protocol):
    actual=head.get('sampling_steps',25);expected=protocol.get('sampling_steps_by_head',{}).get(head['name'],25)
    if type(actual) is not int or actual<1 or actual!=expected:raise ValueError('Head step count differs from frozen protocol')
    return actual
