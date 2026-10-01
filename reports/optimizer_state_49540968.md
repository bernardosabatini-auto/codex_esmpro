# Optimizer-history continuation diagnostic

Both arms start from saved raw model weights and saved EMA. Only AdamW moments and bias-correction step counters differ: fresh versus restored. Same beta2=0.95, pilot data, per-protein loss, learning-rate schedule, batches and training seed. The original RNG/data stream and learning-rate schedule are not resumed.

Status: complete. Eligible for two additional matched training seeds: False. No independent-test scoring.

TM: fresh 0.56587, restored 0.56586, paired change -0.00002, 95% cluster interval [-0.00011264336686549889, 9.35141555501672e-05].

A single development pair does not establish an accuracy improvement. Retain the +0.01 accuracy-promotion threshold, training-seed replication and independent confirmation.

```json
{
  "status": "complete",
  "runs": {
    "optimizer_state_49540968_0": {
      "task": {
        "seed": 7919,
        "arm": "flow",
        "name": "fresh_optimizer_history",
        "overrides": {
          "optimizer_state_experiment": "fresh"
        }
      },
      "initialization": {
        "model_weights": "saved_raw",
        "ema_weights": "saved_ema",
        "optimizer_state": "fresh",
        "optimizer_initial_step": 0,
        "historical_step": 63235,
        "exact_resume": false,
        "observed_optimizer_steps": []
      },
      "accuracy": {
        "predictions": 1878,
        "targets": 626,
        "mean_ca_lddt": 0.6717309541939689,
        "mean_ca_rmsd": 12.654829861861067,
        "diagnostic_mean_tm_after_kabsch": 0.4411358267600424,
        "mean_tm_fixed_reference": 0.5658731469648562
      },
      "training_seconds": 1539.3450090100523,
      "peak_reserved_gib": 83.962890625,
      "hardware": {
        "whole_capture_mean_percent": {
          "SMs Active [Throughput %]": 92.9284527628085,
          "SM Issue [Throughput %]": 48.480301154640884,
          "Tensor Active [Throughput %]": 4.826951131400802,
          "DRAM Read Bandwidth [Throughput %]": 20.049512878686773,
          "DRAM Write Bandwidth [Throughput %]": 12.236547214181511
        },
        "collection_mean_percent": {
          "SMs Active [Throughput %]": 96.76713245372987,
          "SM Issue [Throughput %]": 41.546257137845686,
          "Tensor Active [Throughput %]": 6.408288021411913,
          "DRAM Read Bandwidth [Throughput %]": 23.354589334320774,
          "DRAM Write Bandwidth [Throughput %]": 14.400271546711881
        },
        "capture_seconds": 2172.972534536,
        "collection_seconds": 1539.34494935,
        "counter_period_ns": 10000057.684154334,
        "validated_intervals": 1,
        "caveat": "SM activity includes waiting warps; it is not FLOP efficiency. Whole capture excludes profiler export after collection."
      }
    },
    "optimizer_state_49540968_1": {
      "task": {
        "seed": 7919,
        "arm": "flow",
        "name": "restored_optimizer_history",
        "overrides": {
          "optimizer_state_experiment": "restored"
        }
      },
      "initialization": {
        "model_weights": "saved_raw",
        "ema_weights": "saved_ema",
        "optimizer_state": "restored",
        "optimizer_initial_step": 63235,
        "historical_step": 63235,
        "exact_resume": false,
        "observed_optimizer_steps": [
          63235
        ]
      },
      "accuracy": {
        "predictions": 1878,
        "targets": 626,
        "mean_ca_lddt": 0.6718005600469046,
        "mean_ca_rmsd": 12.655335729423168,
        "diagnostic_mean_tm_after_kabsch": 0.4411029217340723,
        "mean_tm_fixed_reference": 0.5658576411075613
      },
      "training_seconds": 1540.6141147320159,
      "peak_reserved_gib": 84.041015625,
      "hardware": {
        "whole_capture_mean_percent": {
          "SMs Active [Throughput %]": 92.61569470078878,
          "SM Issue [Throughput %]": 48.26507534227707,
          "Tensor Active [Throughput %]": 4.813600176303683,
          "DRAM Read Bandwidth [Throughput %]": 20.0078234759373,
          "DRAM Write Bandwidth [Throughput %]": 12.211651653306154
        },
        "collection_mean_percent": {
          "SMs Active [Throughput %]": 96.68794178929126,
          "SM Issue [Throughput %]": 41.50197648983195,
          "Tensor Active [Throughput %]": 6.401464355028203,
          "DRAM Read Bandwidth [Throughput %]": 23.339047520138127,
          "DRAM Write Bandwidth [Throughput %]": 14.38938472423261
        },
        "capture_seconds": 2178.060795345,
        "collection_seconds": 1540.614091667,
        "counter_period_ns": 10000049.564266201,
        "validated_intervals": 1,
        "caveat": "SM activity includes waiting warps; it is not FLOP efficiency. Whole capture excludes profiler export after collection."
      }
    }
  },
  "failures": [],
  "screen_passed": false,
  "accuracy_promotion": false,
  "paired": {
    "tm_fixed_reference": {
      "n": 626,
      "clusters": 606,
      "bootstrap_unit": "cluster",
      "ours": 0.5658731469648562,
      "theirs": 0.5658576411075613,
      "theirs_minus_ours": -1.550585729499774e-05,
      "ci95": [
        -0.00011264336686549889,
        9.35141555501672e-05
      ],
      "ours_wins": 324,
      "ties": 9,
      "coverage": 1.0
    },
    "ca_lddt": {
      "n": 626,
      "clusters": 606,
      "bootstrap_unit": "cluster",
      "ours": 0.6717309541939688,
      "theirs": 0.6718005600469045,
      "theirs_minus_ours": 6.96058529356759e-05,
      "ci95": [
        -3.981770883194785e-05,
        0.00020739126546699734
      ],
      "ours_wins": 262,
      "ties": 69,
      "coverage": 1.0
    }
  },
  "vs_untouched": {
    "fresh": {
      "tm_fixed_reference": {
        "n": 626,
        "clusters": 606,
        "bootstrap_unit": "cluster",
        "ours": 0.5682384930777423,
        "theirs": 0.5658731469648562,
        "theirs_minus_ours": -0.0023653461128860494,
        "ci95": [
          -0.004071063952029199,
          -0.0006234612984781674
        ],
        "ours_wins": 364,
        "ties": 0,
        "coverage": 1.0
      },
      "ca_lddt": {
        "n": 626,
        "clusters": 606,
        "bootstrap_unit": "cluster",
        "ours": 0.6745045193931416,
        "theirs": 0.6717309541939688,
        "theirs_minus_ours": -0.002773565199172728,
        "ci95": [
          -0.004162021653907534,
          -0.0013348619974995221
        ],
        "ours_wins": 370,
        "ties": 4,
        "coverage": 1.0
      }
    },
    "restored": {
      "tm_fixed_reference": {
        "n": 626,
        "clusters": 606,
        "bootstrap_unit": "cluster",
        "ours": 0.5682384930777423,
        "theirs": 0.5658576411075613,
        "theirs_minus_ours": -0.0023808519701810464,
        "ci95": [
          -0.00406773203813057,
          -0.0006656626789917467
        ],
        "ours_wins": 365,
        "ties": 0,
        "coverage": 1.0
      },
      "ca_lddt": {
        "n": 626,
        "clusters": 606,
        "bootstrap_unit": "cluster",
        "ours": 0.6745045193931416,
        "theirs": 0.6718005600469045,
        "theirs_minus_ours": -0.0027039593462370518,
        "ci95": [
          -0.0040823107968659435,
          -0.0012707339285756725
        ],
        "ours_wins": 369,
        "ties": 1,
        "coverage": 1.0
      }
    }
  },
  "geometry": {
    "predicted_ca_gaps_on_reference_short": {
      "n": 626,
      "clusters": 606,
      "bootstrap_unit": "cluster",
      "ours": 0.0027165357815853992,
      "theirs": 0.0027472729190534118,
      "theirs_minus_ours": 3.073713746801244e-05,
      "ci95": [
        -6.678686495528638e-06,
        7.484612990172276e-05
      ],
      "ours_wins": 14,
      "ties": 592,
      "coverage": 1.0
    },
    "peptide_length_outliers_on_reference_short": {
      "n": 626,
      "clusters": 606,
      "bootstrap_unit": "cluster",
      "ours": 0.0053107059801650374,
      "theirs": 0.005413988444727324,
      "theirs_minus_ours": 0.00010328246456228613,
      "ci95": [
        2.6645851044029e-05,
        0.0001841825003522481
      ],
      "ours_wins": 37,
      "ties": 531,
      "coverage": 1.0
    }
  }
}
```
