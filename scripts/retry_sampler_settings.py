"""Step counts must be explicit in both head and frozen protocol."""


def native_steps(head,protocol):
    actual=head.get('sampling_steps',25);expected=protocol.get('sampling_steps_by_head',{}).get(head['name'],25)
    if type(actual) is not int or actual<1 or actual!=expected:raise ValueError('Head step count differs from frozen protocol')
    return actual


def external_steps(config,protocol):
    actual=config.get('flow_steps',25)
    native_steps(dict(name=config['name'],sampling_steps=actual),protocol)
    if config.get('flow_solver','euler')!='euler' or config.get('flow_time_power',1)!=1:raise ValueError('Unsupported retry integration recipe')
    return actual
