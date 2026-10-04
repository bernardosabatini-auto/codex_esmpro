# Internal-coordinate bridge preflight

```json
{
  "status": "complete",
  "qualified": true,
  "seconds": 16.46261026104912,
  "protocol_sha256": "cde5405a895172cb6dcc6fd653b38836c76564a1ad9009ea59fad3fc8d684654",
  "source_report_sha256": "d6b769b04f62c606e7c90c0c232167ae15cbfb573db5ee766d45e6fa2ff9403d",
  "predictions_sha256": "92ada2b59853f85b44c1bd8b5ccf1d34193c85fc2919c1a16672fa04a4869757",
  "code_sha256": "54174f21bfdb70a7094ac59c85aebfc79c7a29a30d67b41ca5e25d4680736aff",
  "script_sha256": "a3482d64d137c7ced128937d245a74968a38a2d1451d83d087d8c436178c6443",
  "summary": [
    {
      "dtype": "float64",
      "bridges": 512,
      "passed": 512,
      "roundtrip_max_abs": 2.4868995751603507e-14,
      "roundtrip_endpoint_max_abs": 3.019806626980426e-14,
      "proper_pose_max_abs": 1.7319479184152442e-13,
      "proper_pose_endpoint_max_abs": 1.9062529332813938e-13,
      "max_bond_delta": 4.218847493575595e-15,
      "max_angle_delta": 2.2737367544323206e-13,
      "max_peptide_torsion_delta": 3.410605131648481e-13,
      "median_perturbed_endpoint_rmsd": 6.762572273420181
    },
    {
      "dtype": "float32",
      "bridges": 512,
      "passed": 512,
      "roundtrip_max_abs": 1.52587890625e-05,
      "roundtrip_endpoint_max_abs": 1.5974044799804688e-05,
      "proper_pose_max_abs": 7.62939453125e-05,
      "proper_pose_endpoint_max_abs": 8.58306884765625e-05,
      "max_bond_delta": 2.1561436291950287e-06,
      "max_angle_delta": 0.0001288781288053542,
      "max_peptide_torsion_delta": 0.00016654489709821974,
      "median_perturbed_endpoint_rmsd": 6.7625696659088135
    }
  ],
  "scope": "Original32 training-diagnostic families, no locked-test access. A representation test, not learned capacity, conformational validity or designability. Source parents retain their imperfections. Endpoint, steric and same-refold gates remain necessary."
}
```
