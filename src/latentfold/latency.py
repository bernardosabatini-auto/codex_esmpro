"""Explicit pipeline roster for same-device timing comparisons."""


def latency_kinds(config):
    if config.get('include_expanded_candidate'):
        if not config.get('candidate_checkpoint') or not config.get('candidate_compact_condition'):
            raise ValueError('expanded comparator requires a compact candidate checkpoint')
        return ('student','expanded_candidate','candidate','teacher')
    return ('student','candidate','teacher') if config.get('candidate_checkpoint') else ('student','teacher')
