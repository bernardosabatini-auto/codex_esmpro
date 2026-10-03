# Additional-family same-refold assay

```json
{
  "status": "complete",
  "manifest_sha256": "f0e4614e023dec2b120ee835894ee6c1a9ee71d8e5a46946b837dd2de5aac40d",
  "refolded_sha256": "003d2e231ec69f19099a1a25037afc6d0f0d26405dff3115828f632f5990da58",
  "generation_inventory_sha256": "21d8bc5434149383c036a9d7b995f3c39e6ef284e18f69ce1d459c254ca3e9ec",
  "partition": 3,
  "target_ids": [
    "3zdo_A",
    "6gf6_A",
    "6hy3_A",
    "7bb3_A",
    "7tgh_P1",
    "8b6h_DT",
    "8cen_h",
    "8f2n_A",
    "8iuf_6B",
    "8r4z_A",
    "9d93_Ja",
    "9e6q_Ae",
    "9fq8_4R",
    "9g6k_LY",
    "9i05_XC",
    "9kz9_Q"
  ],
  "completed_refolds": 240,
  "native_controls": {
    "3zdo_A": {
      "strict_joint_success": false,
      "scaffold_joint_success": false,
      "valid_designable": true
    },
    "6gf6_A": {
      "strict_joint_success": true,
      "scaffold_joint_success": true,
      "valid_designable": true
    },
    "6hy3_A": {
      "strict_joint_success": true,
      "scaffold_joint_success": true,
      "valid_designable": true
    },
    "7bb3_A": {
      "strict_joint_success": true,
      "scaffold_joint_success": false,
      "valid_designable": true
    },
    "7tgh_P1": {
      "strict_joint_success": false,
      "scaffold_joint_success": false,
      "valid_designable": true
    },
    "8b6h_DT": {
      "strict_joint_success": false,
      "scaffold_joint_success": false,
      "valid_designable": false
    },
    "8cen_h": {
      "strict_joint_success": false,
      "scaffold_joint_success": false,
      "valid_designable": false
    },
    "8f2n_A": {
      "strict_joint_success": true,
      "scaffold_joint_success": true,
      "valid_designable": true
    },
    "8iuf_6B": {
      "strict_joint_success": false,
      "scaffold_joint_success": false,
      "valid_designable": false
    },
    "8r4z_A": {
      "strict_joint_success": true,
      "scaffold_joint_success": true,
      "valid_designable": true
    },
    "9d93_Ja": {
      "strict_joint_success": true,
      "scaffold_joint_success": true,
      "valid_designable": true
    },
    "9e6q_Ae": {
      "strict_joint_success": true,
      "scaffold_joint_success": true,
      "valid_designable": true
    },
    "9fq8_4R": {
      "strict_joint_success": false,
      "scaffold_joint_success": false,
      "valid_designable": false
    },
    "9g6k_LY": {
      "strict_joint_success": true,
      "scaffold_joint_success": false,
      "valid_designable": true
    },
    "9i05_XC": {
      "strict_joint_success": true,
      "scaffold_joint_success": true,
      "valid_designable": true
    },
    "9kz9_Q": {
      "strict_joint_success": false,
      "scaffold_joint_success": false,
      "valid_designable": true
    }
  },
  "successful_scaffold_diversity": [
    {
      "arm": "broad_frozen",
      "target_id": "7bb3_A",
      "successful_backbones": 1,
      "pairs": []
    },
    {
      "arm": "broad_frozen",
      "target_id": "9fq8_4R",
      "successful_backbones": 1,
      "pairs": []
    }
  ],
  "elapsed_seconds": 566.6249513085932,
  "scope": "Disjoint16-family partition; eight fixed-motif designs per selected backbone. Primary and stronger scaffold success require the same valid refold. All raw failures remain in the generation denominator. Diversity is across scaffold designs, potentially with different full sequences.",
  "reused_native_source": {
    "manifest": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_50120232/manifest.json",
    "manifest_sha256": "a1ba0de55b8731e94fce70ffdc1f76d0fe51a6a007fd103c4e75ede081417b1c",
    "report": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50120232.json",
    "report_sha256": "aa3bbe70788207c41c05234ea446bce810c50c82ac0f82a7368873a214928ea5",
    "refolded": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_50120232/refolded.h5",
    "refolded_sha256": "e5644955cebbfe3a606a0364deb2e92cf9ef6f3577891de3e65f316556ded509",
    "predictions": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_short_refold_3.h5",
    "predictions_sha256": "aae965831b5487bc3675f197c354905c1e9dfa97c76b9e1a8208324ada8f5dc7"
  },
  "numerical_recovery": {
    "evidence": {
      "failed_manifest": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_50145102/manifest.json",
      "failed_refolded": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_50145102/refolded.h5",
      "probe_manifest": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/teacher_repeatability_probe_50154738/manifest.json",
      "probe_report": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/teacher_repeatability_probe_50154738.json",
      "failed_manifest_sha256": "6e20f2a8ed799328d700d8064d953fc2948ec3d1835e0ecf56ad177226257c6f",
      "failed_refolded_sha256": "bb3f37a6a0dcc3fabb9aefc6d38fc03be78eab45cbd4b1ed7828ad8874f10df8",
      "probe_manifest_sha256": "be13c65f3f648be1c4e7616a7581c74162009b6a5f03575e92b6a75e66b0471c",
      "probe_report_sha256": "56d4e08ae0fe996db5424de8639da32a91934c9ebd10c3cb6fe6e9be41db4179"
    },
    "original_output_parity": {
      "ca_rmsd": 0.007412332574982787,
      "tm_after_kabsch": 0.9999961497525766,
      "ca_lddt": 1.0
    },
    "policy": "Deterministic algorithms; identical eight sequences and seeds; failed run excluded, not pooled."
  }
}
```
