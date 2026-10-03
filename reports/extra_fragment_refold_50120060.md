# Additional-family same-refold assay

```json
{
  "status": "complete",
  "manifest_sha256": "d518fc97c83ba401d12125209374365bfe6228b805522211db69c4966a50b5f7",
  "refolded_sha256": "756e8fd2fd0b2624c08038f3d4bf6f0d0dae6ee4eae8d24d7126b75aaf6d2118",
  "generation_inventory_sha256": "e45b5dd3d77d179a9dd969b596fc9d6a91ad1ef46f9d5a82faad9a0fe60a8fc4",
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
  "completed_refolds": 232,
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
      "arm": "control512",
      "target_id": "4eyt_A",
      "successful_backbones": 3,
      "pairs": [
        {
          "left_slot": 0,
          "right_slot": 2,
          "left_sequence": 0,
          "right_sequence": 0,
          "global_tm": 0.2943,
          "scaffold_tm": 0.1822,
          "motif_aligned_scaffold_rmsd": 19.017381465422655
        },
        {
          "left_slot": 0,
          "right_slot": 3,
          "left_sequence": 0,
          "right_sequence": 1,
          "global_tm": 0.27549,
          "scaffold_tm": 0.22928,
          "motif_aligned_scaffold_rmsd": 19.190259339534915
        },
        {
          "left_slot": 2,
          "right_slot": 3,
          "left_sequence": 0,
          "right_sequence": 1,
          "global_tm": 0.2688,
          "scaffold_tm": 0.16568,
          "motif_aligned_scaffold_rmsd": 21.851020193462464
        }
      ]
    },
    {
      "arm": "control512",
      "target_id": "7tgh_R",
      "successful_backbones": 4,
      "pairs": [
        {
          "left_slot": 0,
          "right_slot": 1,
          "left_sequence": 1,
          "right_sequence": 4,
          "global_tm": 0.27559,
          "scaffold_tm": 0.23843,
          "motif_aligned_scaffold_rmsd": 37.980097288890406
        },
        {
          "left_slot": 0,
          "right_slot": 2,
          "left_sequence": 1,
          "right_sequence": 0,
          "global_tm": 0.2699,
          "scaffold_tm": 0.19938,
          "motif_aligned_scaffold_rmsd": 30.997811607328263
        },
        {
          "left_slot": 0,
          "right_slot": 3,
          "left_sequence": 1,
          "right_sequence": 1,
          "global_tm": 0.19228,
          "scaffold_tm": 0.21343,
          "motif_aligned_scaffold_rmsd": 33.285685799972605
        },
        {
          "left_slot": 1,
          "right_slot": 2,
          "left_sequence": 4,
          "right_sequence": 0,
          "global_tm": 0.28245,
          "scaffold_tm": 0.21521,
          "motif_aligned_scaffold_rmsd": 23.236138348021402
        },
        {
          "left_slot": 1,
          "right_slot": 3,
          "left_sequence": 4,
          "right_sequence": 1,
          "global_tm": 0.23057,
          "scaffold_tm": 0.26241,
          "motif_aligned_scaffold_rmsd": 31.001537379583983
        },
        {
          "left_slot": 2,
          "right_slot": 3,
          "left_sequence": 0,
          "right_sequence": 1,
          "global_tm": 0.20846,
          "scaffold_tm": 0.19867,
          "motif_aligned_scaffold_rmsd": 24.46299193933457
        }
      ]
    }
  ],
  "elapsed_seconds": 706.5795046067797,
  "scope": "Disjoint16-family partition; eight fixed-motif designs per selected backbone. Primary and stronger scaffold success require the same valid refold. All raw failures remain in the generation denominator. Diversity is across scaffold designs, potentially with different full sequences."
}
```
