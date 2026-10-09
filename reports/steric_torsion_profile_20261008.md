# Atom-repulsion torsion-closure profile

```json
{
  "status": "complete",
  "profile_only": true,
  "protocol_sha256": "7466f7d045203b47b9fdce7ce24b0ef9a81a32e7053d2e6326dd1ce12a919c2c",
  "baseline_report_sha256": "18dced564834de25b4f33a7d85c870c490078265f666191ccd697fe68f8815bc",
  "baseline_predictions_sha256": "ace4159e7a323e7df9b91b0ceaf6035a8f34096ef6eceecf50ca98eedc02c0cd",
  "evidence_sha256": {
    "failure_evidence": "e5e3d6ab278df7e2b4fca47574828eb52e89850490c73127d4eceffdf699b9ba",
    "steric_evidence": "7fa98793e42d21133f616f074ad7c6bc93bde6f43667d242c5eb2fb46a9ef83f"
  },
  "sources": {
    "configs/steric_torsion_closure_protocol.json": "7466f7d045203b47b9fdce7ce24b0ef9a81a32e7053d2e6326dd1ce12a919c2c",
    "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/src/latentfold/steric_torsion_closure.py": "5b4df49c862a276f31b046c117f7061dd6e4ac21b79926ca82a62716316152de",
    "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/src/latentfold/backbone_sterics.py": "b4942561788f0d77870a6f23087da3627395cc640d5a8d13e1d4f083524f0230",
    "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/scripts/profile_steric_torsion_closure.py": "35acd186a40dc5eb7c4f92ffb71ca129ad25316f5944fd2bdcd71e61868f617c"
  },
  "controls": [
    {
      "arm": "generated_cond",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "noop_exact": true,
      "noop_calls": 0,
      "repeat_exact": true,
      "pose_max_abs": 9.769962616701378e-15
    },
    {
      "arm": "native_cond",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "noop_exact": true,
      "noop_calls": 0,
      "repeat_exact": true,
      "pose_max_abs": 5.861977570020827e-14
    },
    {
      "arm": "generated_cond",
      "target_id": "AF-A0A673FGJ2-F1-model_v6",
      "noop_exact": true,
      "noop_calls": 0,
      "repeat_exact": true,
      "pose_max_abs": 2.1316282072803006e-14
    },
    {
      "arm": "native_cond",
      "target_id": "AF-A0A673FGJ2-F1-model_v6",
      "noop_exact": true,
      "noop_calls": 0,
      "repeat_exact": true,
      "pose_max_abs": 5.750955267558311e-14
    },
    {
      "arm": "generated_cond",
      "target_id": "AF-A0AAE1HAL9-F1-model_v6",
      "noop_exact": true,
      "noop_calls": 0,
      "repeat_exact": true,
      "pose_max_abs": 1.4210854715202004e-14
    },
    {
      "arm": "native_cond",
      "target_id": "AF-A0AAE1HAL9-F1-model_v6",
      "noop_exact": true,
      "noop_calls": 0,
      "repeat_exact": true,
      "pose_max_abs": 3.730349362740526e-14
    },
    {
      "arm": "generated_cond",
      "target_id": "AF-A0A6C0DXI0-F1-model_v6",
      "noop_exact": true,
      "noop_calls": 0,
      "repeat_exact": true,
      "pose_max_abs": 2.4868995751603507e-14
    },
    {
      "arm": "native_cond",
      "target_id": "AF-A0A6C0DXI0-F1-model_v6",
      "noop_exact": true,
      "noop_calls": 0,
      "repeat_exact": true,
      "pose_max_abs": 1.2878587085651816e-14
    }
  ],
  "summary": [
    {
      "arm": "generated_cond",
      "samples": 16,
      "physical": 12,
      "overlap_cases": 5,
      "baseline_overlap_cases": 7,
      "steric_eligible": 11
    },
    {
      "arm": "native_cond",
      "samples": 16,
      "physical": 16,
      "overlap_cases": 0,
      "baseline_overlap_cases": 0,
      "steric_eligible": 16
    }
  ],
  "qualified": false,
  "seconds": 147.5680026700138,
  "predictions_sha256": "f382511e57fd426116bbbaed9a94a2ee5645dcde951a7e087b56d8ff73712d33",
  "run": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/steric_torsion_profile_20261008",
  "manifest_sha256": "3418c0f0560ebba4a00d2a11a9e0c7b24967b0c7b36f973b2a255af514752212"
}
```
