# Frozen checkpoint diagnostic

Predeclared comparison of original training-selected best EMA and final unaveraged weights against final EMA. All 626 development proteins, three fixed samples, 25 steps, guidance 2, strict FP32 and fixed correspondence. No new training or test-set scoring.

| Checkpoint | TM | Delta vs final EMA [95% cluster CI] | CA lDDT |
|---|---:|---|---:|
| training_selected_best_ema_epoch22 | 0.56767 | -0.00057 [-0.0024900782329381524, 0.0013132227872574165] | 0.67345 |
| final_unaveraged_epoch30 | 0.56465 | -0.00359 [-0.005387007600557707, -0.001824440371473854] | 0.67156 |

Results are checkpoint diagnostics, not independent training-seed replications. No original legacy TM score is treated as comparable to the new scorer.

```json
{
  "status": "complete",
  "runs": {
    "checkpoint_49524706_0": {
      "probe": {
        "name": "training_selected_best_ema_epoch22",
        "checkpoint": "/n/netscratch/bsabatini_lab/Users/bsabatini/esm_proae/data/phase1_dataset/best_pf_459M_p128x8_long512_scratch.pt",
        "checkpoint_sha256": "08c31a7c3a8ba174c68be73d3ddc9dd57208c52e168a2427b0ad41caf43a5487"
      },
      "paired": {
        "tm_fixed_reference": {
          "n": 626,
          "clusters": 606,
          "bootstrap_unit": "cluster",
          "ours": 0.5682384930777423,
          "theirs": 0.567668626198083,
          "theirs_minus_ours": -0.0005698668796592129,
          "ci95": [
            -0.0024900782329381524,
            0.0013132227872574165
          ],
          "ours_wins": 313,
          "ties": 0,
          "coverage": 1.0
        },
        "ca_lddt": {
          "n": 626,
          "clusters": 606,
          "bootstrap_unit": "cluster",
          "ours": 0.6745045193931416,
          "theirs": 0.673452090972876,
          "theirs_minus_ours": -0.0010524284202656888,
          "ci95": [
            -0.002401403355858479,
            0.0003016631246834508
          ],
          "ours_wins": 338,
          "ties": 1,
          "coverage": 1.0
        }
      },
      "geometry": {
        "predicted_ca_gaps_on_reference_short": {
          "n": 626,
          "clusters": 606,
          "bootstrap_unit": "cluster",
          "ours": 0.0013118909803609866,
          "theirs": 0.0015788278723439708,
          "theirs_minus_ours": 0.00026693689198298444,
          "ci95": [
            0.00010070793976002836,
            0.0004429468662880738
          ],
          "ours_wins": 159,
          "ties": 376,
          "coverage": 1.0
        },
        "peptide_length_outliers_on_reference_short": {
          "n": 626,
          "clusters": 606,
          "bootstrap_unit": "cluster",
          "ours": 0.008932701734823516,
          "theirs": 0.0033774240961159147,
          "theirs_minus_ours": -0.0055552776387076015,
          "ci95": [
            -0.0062226793184778275,
            -0.004951499628107897
          ],
          "ours_wins": 506,
          "ties": 62,
          "coverage": 1.0
        }
      },
      "accuracy": {
        "predictions": 1878,
        "targets": 626,
        "mean_ca_lddt": 0.673452090972876,
        "mean_ca_rmsd": 12.674586156877758,
        "diagnostic_mean_tm_after_kabsch": 0.4429492551705545,
        "mean_tm_fixed_reference": 0.5676686261980831
      },
      "hardware": {
        "whole_capture_mean_percent": {
          "SMs Active [Throughput %]": 77.18885215902718,
          "SM Issue [Throughput %]": 60.25443463888315,
          "Tensor Active [Throughput %]": 0.9036480623358224,
          "DRAM Read Bandwidth [Throughput %]": 11.18743543578997,
          "DRAM Write Bandwidth [Throughput %]": 6.537631710988459
        },
        "collection_mean_percent": {
          "SMs Active [Throughput %]": 96.4122013453955,
          "SM Issue [Throughput %]": 75.49887180784884,
          "Tensor Active [Throughput %]": 1.1257248898167478,
          "DRAM Read Bandwidth [Throughput %]": 13.910271820501466,
          "DRAM Write Bandwidth [Throughput %]": 8.000400666371439
        },
        "capture_seconds": 677.610564602,
        "collection_seconds": 474.226721954,
        "counter_period_ns": 10000008.332256017,
        "validated_intervals": 33,
        "caveat": "SM activity includes waiting warps; it is not FLOP efficiency. Whole capture excludes profiler export after collection."
      }
    },
    "checkpoint_49524706_1": {
      "probe": {
        "name": "final_unaveraged_epoch30",
        "checkpoint": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/checkpoint_sources/final_unaveraged.ckpt",
        "checkpoint_sha256": "7c4cb8b339d54c9b3025d1c40b9762906126787c3aeac63c59593631894ee53e",
        "parent_checkpoint_sha256": "241ec496e222fd52a43d88e4eede1b1885027ab70d8f796fcb4a5197800985c0"
      },
      "paired": {
        "tm_fixed_reference": {
          "n": 626,
          "clusters": 606,
          "bootstrap_unit": "cluster",
          "ours": 0.5682384930777423,
          "theirs": 0.5646530244941427,
          "theirs_minus_ours": -0.003585468583599578,
          "ci95": [
            -0.005387007600557707,
            -0.001824440371473854
          ],
          "ours_wins": 370,
          "ties": 0,
          "coverage": 1.0
        },
        "ca_lddt": {
          "n": 626,
          "clusters": 606,
          "bootstrap_unit": "cluster",
          "ours": 0.6745045193931416,
          "theirs": 0.6715627240950733,
          "theirs_minus_ours": -0.0029417952980682347,
          "ci95": [
            -0.00440748113943376,
            -0.0014963046898368642
          ],
          "ours_wins": 373,
          "ties": 2,
          "coverage": 1.0
        }
      },
      "geometry": {
        "predicted_ca_gaps_on_reference_short": {
          "n": 626,
          "clusters": 606,
          "bootstrap_unit": "cluster",
          "ours": 0.0013118909803609866,
          "theirs": 0.0026483606314077206,
          "theirs_minus_ours": 0.001336469651046734,
          "ci95": [
            0.0010503484265652592,
            0.0016316206669077643
          ],
          "ours_wins": 100,
          "ties": 368,
          "coverage": 1.0
        },
        "peptide_length_outliers_on_reference_short": {
          "n": 626,
          "clusters": 606,
          "bootstrap_unit": "cluster",
          "ours": 0.008932701734823516,
          "theirs": 0.00517222554012904,
          "theirs_minus_ours": -0.003760476194694476,
          "ci95": [
            -0.0043993932662153646,
            -0.0031330294472840586
          ],
          "ours_wins": 449,
          "ties": 60,
          "coverage": 1.0
        }
      },
      "accuracy": {
        "predictions": 1878,
        "targets": 626,
        "mean_ca_lddt": 0.6715627240950734,
        "mean_ca_rmsd": 12.71947242131228,
        "diagnostic_mean_tm_after_kabsch": 0.4404297302489063,
        "mean_tm_fixed_reference": 0.5646530244941428
      },
      "hardware": {
        "whole_capture_mean_percent": {
          "SMs Active [Throughput %]": 77.59677371306006,
          "SM Issue [Throughput %]": 60.52518767874166,
          "Tensor Active [Throughput %]": 0.9087076978074357,
          "DRAM Read Bandwidth [Throughput %]": 11.262511916110581,
          "DRAM Write Bandwidth [Throughput %]": 6.589579361296473
        },
        "collection_mean_percent": {
          "SMs Active [Throughput %]": 96.43076434469617,
          "SM Issue [Throughput %]": 75.45898793139953,
          "Tensor Active [Throughput %]": 1.1264450561084056,
          "DRAM Read Bandwidth [Throughput %]": 13.965085750582258,
          "DRAM Write Bandwidth [Throughput %]": 8.029345754816854
        },
        "capture_seconds": 671.350021455,
        "collection_seconds": 472.310217761,
        "counter_period_ns": 10000000.319579951,
        "validated_intervals": 33,
        "caveat": "SM activity includes waiting warps; it is not FLOP efficiency. Whole capture excludes profiler export after collection."
      }
    }
  },
  "failures": []
}
```
