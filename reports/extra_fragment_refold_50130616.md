# Additional-family same-refold assay

```json
{
  "status": "complete",
  "manifest_sha256": "a8a9ad6a1bbbe0b1e0d962e8f207691e00469bdfd8b78679838e2b7bdb8b9537",
  "refolded_sha256": "e85d8116ff22dbd12e8736f92c87fc1e68d8193cff53ac3f62bbc2e20b51020c",
  "generation_inventory_sha256": "fa00f0b764f8413e03454c51ece03ab096e71e909763441eee15ed80f499f4d6",
  "partition": 0,
  "target_ids": [
    "1wv3_A",
    "31ev_V",
    "4eyt_A",
    "6gh8_D",
    "7clu_A",
    "7rsw_A",
    "7tgh_R",
    "8b6h_DU",
    "8har_A",
    "8iuf_AN",
    "8kde_3",
    "8xqx_G",
    "9d93_Sa",
    "9fpm_A",
    "9fzl_3K",
    "9gs0_AA"
  ],
  "completed_refolds": 584,
  "native_controls": {
    "1wv3_A": {
      "strict_joint_success": true,
      "scaffold_joint_success": true,
      "valid_designable": true
    },
    "31ev_V": {
      "strict_joint_success": true,
      "scaffold_joint_success": true,
      "valid_designable": true
    },
    "4eyt_A": {
      "strict_joint_success": true,
      "scaffold_joint_success": true,
      "valid_designable": true
    },
    "6gh8_D": {
      "strict_joint_success": false,
      "scaffold_joint_success": false,
      "valid_designable": true
    },
    "7clu_A": {
      "strict_joint_success": true,
      "scaffold_joint_success": true,
      "valid_designable": true
    },
    "7rsw_A": {
      "strict_joint_success": false,
      "scaffold_joint_success": false,
      "valid_designable": true
    },
    "7tgh_R": {
      "strict_joint_success": true,
      "scaffold_joint_success": true,
      "valid_designable": true
    },
    "8b6h_DU": {
      "strict_joint_success": false,
      "scaffold_joint_success": false,
      "valid_designable": false
    },
    "8har_A": {
      "strict_joint_success": true,
      "scaffold_joint_success": true,
      "valid_designable": true
    },
    "8iuf_AN": {
      "strict_joint_success": false,
      "scaffold_joint_success": false,
      "valid_designable": true
    },
    "8kde_3": {
      "strict_joint_success": false,
      "scaffold_joint_success": false,
      "valid_designable": false
    },
    "8xqx_G": {
      "strict_joint_success": true,
      "scaffold_joint_success": true,
      "valid_designable": true
    },
    "9d93_Sa": {
      "strict_joint_success": true,
      "scaffold_joint_success": true,
      "valid_designable": true
    },
    "9fpm_A": {
      "strict_joint_success": false,
      "scaffold_joint_success": false,
      "valid_designable": true
    },
    "9fzl_3K": {
      "strict_joint_success": false,
      "scaffold_joint_success": false,
      "valid_designable": false
    },
    "9gs0_AA": {
      "strict_joint_success": true,
      "scaffold_joint_success": true,
      "valid_designable": true
    }
  },
  "successful_scaffold_diversity": [
    {
      "arm": "broad_balanced",
      "target_id": "7tgh_R",
      "successful_backbones": 1,
      "pairs": []
    },
    {
      "arm": "broad_weight3",
      "target_id": "4eyt_A",
      "successful_backbones": 1,
      "pairs": []
    },
    {
      "arm": "broad_weight3",
      "target_id": "7tgh_R",
      "successful_backbones": 2,
      "pairs": [
        {
          "left_slot": 0,
          "right_slot": 2,
          "left_sequence": 0,
          "right_sequence": 0,
          "global_tm": 0.27244,
          "scaffold_tm": 0.24725,
          "motif_aligned_scaffold_rmsd": 45.82934601147678
        }
      ]
    },
    {
      "arm": "control_balanced",
      "target_id": "4eyt_A",
      "successful_backbones": 1,
      "pairs": []
    },
    {
      "arm": "control_balanced",
      "target_id": "7tgh_R",
      "successful_backbones": 2,
      "pairs": [
        {
          "left_slot": 0,
          "right_slot": 3,
          "left_sequence": 1,
          "right_sequence": 3,
          "global_tm": 0.20916,
          "scaffold_tm": 0.23025,
          "motif_aligned_scaffold_rmsd": 34.96007707269361
        }
      ]
    },
    {
      "arm": "control_weight3",
      "target_id": "4eyt_A",
      "successful_backbones": 1,
      "pairs": []
    },
    {
      "arm": "control_weight3",
      "target_id": "7tgh_R",
      "successful_backbones": 4,
      "pairs": [
        {
          "left_slot": 0,
          "right_slot": 1,
          "left_sequence": 0,
          "right_sequence": 0,
          "global_tm": 0.30952,
          "scaffold_tm": 0.22875,
          "motif_aligned_scaffold_rmsd": 41.982087702470906
        },
        {
          "left_slot": 0,
          "right_slot": 2,
          "left_sequence": 0,
          "right_sequence": 0,
          "global_tm": 0.24206,
          "scaffold_tm": 0.23141,
          "motif_aligned_scaffold_rmsd": 30.819157537575045
        },
        {
          "left_slot": 0,
          "right_slot": 3,
          "left_sequence": 0,
          "right_sequence": 0,
          "global_tm": 0.21221,
          "scaffold_tm": 0.23358,
          "motif_aligned_scaffold_rmsd": 34.142335581259225
        },
        {
          "left_slot": 1,
          "right_slot": 2,
          "left_sequence": 0,
          "right_sequence": 0,
          "global_tm": 0.27739,
          "scaffold_tm": 0.28213,
          "motif_aligned_scaffold_rmsd": 26.822291629118208
        },
        {
          "left_slot": 1,
          "right_slot": 3,
          "left_sequence": 0,
          "right_sequence": 0,
          "global_tm": 0.25837,
          "scaffold_tm": 0.29731,
          "motif_aligned_scaffold_rmsd": 35.54368462150246
        },
        {
          "left_slot": 2,
          "right_slot": 3,
          "left_sequence": 0,
          "right_sequence": 0,
          "global_tm": 0.29119,
          "scaffold_tm": 0.32251,
          "motif_aligned_scaffold_rmsd": 25.037403506792273
        }
      ]
    }
  ],
  "elapsed_seconds": 1455.7408525706269,
  "scope": "Disjoint16-family partition; eight fixed-motif designs per selected backbone. Primary and stronger scaffold success require the same valid refold. All raw failures remain in the generation denominator. Diversity is across scaffold designs, potentially with different full sequences.",
  "reused_native_source": {
    "manifest": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_50120060/manifest.json",
    "manifest_sha256": "d518fc97c83ba401d12125209374365bfe6228b805522211db69c4966a50b5f7",
    "report": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50120060.json",
    "report_sha256": "f1d63f347fbd71bba5c5c897ba02a5bc4034fe66d33e694aa48f02ce229f4f1c",
    "refolded": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_50120060/refolded.h5",
    "refolded_sha256": "756e8fd2fd0b2624c08038f3d4bf6f0d0dae6ee4eae8d24d7126b75aaf6d2118",
    "predictions": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_short_refold_0.h5",
    "predictions_sha256": "30809a95fcbeae6924995fa2957fc3ae0cd28e749d97a98324df3765f0c31aaa"
  }
}
```
