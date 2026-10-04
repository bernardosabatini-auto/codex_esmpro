"""Reject incomplete, filtered or physically ineligible wider-mask endpoints."""


def require_quality(report):
    if (report.get('status')!='complete' or report.get('profile_only') is not False
            or report.get('flank_context') is not True or report.get('context_flank')!=8
            or report.get('numerically_qualified') is not True or report.get('updates')!=2000):
        raise ValueError('Complete audited2000update wider-mask endpoint required')
    rows=report['closure_records'];arms=('generated_cond','generated_untrained')
    ids=sorted({r['target_id'] for r in rows});expected={(a,i,k) for a in arms for i in ids for k in range(4)}
    if len(ids)!=32 or len(rows)!=256 or {(r['arm'],r['target_id'],r['generation_slot']) for r in rows}!=expected:
        raise ValueError('All128backbones per arm must be retained')
    counts={}
    for arm in arms:
        rr=[r for r in rows if r['arm']==arm]
        for r in rr:
            eligible=bool(r['qualified_raw'] and r['hidden_flank_bonds']['all_edges_valid'])
            if r['refold_eligible_geometry']!=eligible:raise ValueError('Inconsistent complete physical gate')
        counts[arm]=sum(r['refold_eligible_geometry'] for r in rr)
        summary=[s for s in report['closure_summary'] if s['arm']==arm]
        if len(summary)!=1 or summary[0]['samples']!=128 or summary[0]['refold_eligible_geometry']!=counts[arm]:
            raise ValueError('Geometry summary differs from complete records')
    gate=dict(qualified=counts['generated_cond']>=45,eligible_complete_geometry=counts['generated_cond'],required=45)
    if report.get('refold_eligibility')!=gate or report.get('qualified')!=gate['qualified']:
        raise ValueError('Final physical eligibility disagrees')
    if not gate['qualified']:raise ValueError('Fewer than45physically eligible generated backbones; no refolds')
    return counts
