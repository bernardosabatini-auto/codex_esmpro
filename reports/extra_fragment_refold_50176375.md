# Additional-family same-refold assay

```json
{
  "status": "complete",
  "manifest_sha256": "e22c23d998ceaa9392a1214f619e37023f526478444b3be3404fa5198a91ecfd",
  "refolded_sha256": "f15628f2ba433ab946ec5045f49290daeaac3cf3da925b4223ddec5541b43a82",
  "generation_inventory_sha256": "16dea89f77f25a56beee3c4b1a212d50a38217a2fad03467d80ce7feb708f434",
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
  "completed_refolds": 240,
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
      "arm": "all",
      "target_id": "4eyt_A",
      "successful_backbones": 1,
      "pairs": []
    },
    {
      "arm": "all",
      "target_id": "7tgh_R",
      "successful_backbones": 3,
      "pairs": [
        {
          "left_slot": 1,
          "right_slot": 2,
          "left_sequence": 0,
          "right_sequence": 2,
          "global_tm": 0.26839,
          "scaffold_tm": 0.24463,
          "motif_aligned_scaffold_rmsd": 23.82858770419231
        },
        {
          "left_slot": 1,
          "right_slot": 3,
          "left_sequence": 0,
          "right_sequence": 0,
          "global_tm": 0.2531,
          "scaffold_tm": 0.29076,
          "motif_aligned_scaffold_rmsd": 33.6110740170156
        },
        {
          "left_slot": 2,
          "right_slot": 3,
          "left_sequence": 2,
          "right_sequence": 0,
          "global_tm": 0.22045,
          "scaffold_tm": 0.1914,
          "motif_aligned_scaffold_rmsd": 21.16986403458386
        }
      ]
    },
    {
      "arm": "motif",
      "target_id": "4eyt_A",
      "successful_backbones": 2,
      "pairs": [
        {
          "left_slot": 0,
          "right_slot": 1,
          "left_sequence": 0,
          "right_sequence": 1,
          "global_tm": 0.30919,
          "scaffold_tm": 0.27548,
          "motif_aligned_scaffold_rmsd": 13.50280165347817
        }
      ]
    },
    {
      "arm": "motif",
      "target_id": "7tgh_R",
      "successful_backbones": 3,
      "pairs": [
        {
          "left_slot": 1,
          "right_slot": 2,
          "left_sequence": 1,
          "right_sequence": 0,
          "global_tm": 0.26457,
          "scaffold_tm": 0.28668,
          "motif_aligned_scaffold_rmsd": 20.3686974290729
        },
        {
          "left_slot": 1,
          "right_slot": 3,
          "left_sequence": 1,
          "right_sequence": 4,
          "global_tm": 0.23621,
          "scaffold_tm": 0.27405,
          "motif_aligned_scaffold_rmsd": 33.09544026293784
        },
        {
          "left_slot": 2,
          "right_slot": 3,
          "left_sequence": 0,
          "right_sequence": 4,
          "global_tm": 0.20083,
          "scaffold_tm": 0.18844,
          "motif_aligned_scaffold_rmsd": 24.272899616274167
        }
      ]
    }
  ],
  "elapsed_seconds": 573.882927285973,
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
