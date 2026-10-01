"""Provenance checks for precision and explicit batch-capacity comparisons."""


def validate_online_pair(candidate, reference, *, same_batches=True, same_precision=False):
    for key in ('checkpoint', 'decoder_checkpoint', 'dataset', 'embedding_artifacts',
                'resident_parameters', 'timing_scope'):
        if candidate[key] != reference[key]:
            raise ValueError('online comparison changed '+key)
    keys = ('seed', 'samples', 'target_ids', 'flow_steps', 'guidance')
    for key in keys + (('batches',) if same_batches else ()):
        if candidate['config'][key] != reference['config'][key]:
            raise ValueError('online comparison changed '+key)
    if same_precision and candidate['precision'] != reference['precision']:
        raise ValueError('batch-only comparison changed precision')
    if not same_batches:
        for manifest in (candidate, reference):
            batches = manifest['config']['batches']
            if set(batches) != {'128', '256', '384', '512'} or any(
                    type(n) is not int or n <= 0 or n % 3 for n in batches.values()):
                raise ValueError('invalid three-sample batch sizes')
