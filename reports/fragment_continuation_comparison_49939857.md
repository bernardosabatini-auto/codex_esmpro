# Additional isolated-fragment adaptation

Same32training proteins and evaluation panel. Starts from parentEMA+adapter, with fresh optimizer and data/noise draws under a restarted schedule. This is additional adaptation, not an exact optimizer-state resume or a pure isolated step-count intervention. Parent failures remain reported. Strict proper-rotation and same-refold outcomes are audited separately.

```json
{
  "status": "complete",
  "parent_updates": 2000,
  "candidate_total_updates": 4000,
  "initial_parent_samples_verified": 384,
  "manifest_sha256": "d3ea388805b4e0d17ae5ea2c687fd71012026399581221a485abab66be072423",
  "parent_manifest_sha256": "9c0493fe37e0145cae27a25f9bc3b180d42cd7ac08eb0bc76d0dd91e8da35036",
  "comparisons": [
    {
      "total_updates": 2500,
      "cohort": "train",
      "metric": "joint",
      "parent": 0.078125,
      "candidate": 0.1015625,
      "candidate_minus_parent": {
        "mean": 0.0234375,
        "ci95": [
          -0.0234375,
          0.078125
        ],
        "families": 32
      }
    },
    {
      "total_updates": 2500,
      "cohort": "train",
      "metric": "coarse_valid",
      "parent": 0.9921875,
      "candidate": 0.984375,
      "candidate_minus_parent": {
        "mean": -0.0078125,
        "ci95": [
          -0.03125,
          0.015625
        ],
        "families": 32
      }
    },
    {
      "total_updates": 2500,
      "cohort": "train",
      "metric": "motif_drms",
      "parent": 6.513468626886606,
      "candidate": 6.111161314416677,
      "candidate_minus_parent": {
        "mean": -0.40230731246992946,
        "ci95": [
          -0.7339137384493369,
          -0.08850251331459737
        ],
        "families": 32
      }
    },
    {
      "total_updates": 2500,
      "cohort": "train",
      "metric": "ca_lddt",
      "parent": 0.37926077491471044,
      "candidate": 0.39837219619411485,
      "candidate_minus_parent": {
        "mean": 0.019111421279404385,
        "ci95": [
          0.004453224847117653,
          0.03669542724921212
        ],
        "families": 32
      }
    },
    {
      "total_updates": 2500,
      "cohort": "development",
      "metric": "joint",
      "parent": 0.015625,
      "candidate": 0.0,
      "candidate_minus_parent": {
        "mean": -0.015625,
        "ci95": [
          -0.046875,
          0.0
        ],
        "families": 16
      }
    },
    {
      "total_updates": 2500,
      "cohort": "development",
      "metric": "coarse_valid",
      "parent": 0.96875,
      "candidate": 0.984375,
      "candidate_minus_parent": {
        "mean": 0.015625,
        "ci95": [
          -0.03125,
          0.0625
        ],
        "families": 16
      }
    },
    {
      "total_updates": 2500,
      "cohort": "development",
      "metric": "motif_drms",
      "parent": 2.8548352206125855,
      "candidate": 3.2622947208583355,
      "candidate_minus_parent": {
        "mean": 0.40745950024574995,
        "ci95": [
          0.08724302412010729,
          0.808416241616942
        ],
        "families": 16
      }
    },
    {
      "total_updates": 2500,
      "cohort": "development",
      "metric": "ca_lddt",
      "parent": 0.299698670813013,
      "candidate": 0.2993857629656352,
      "candidate_minus_parent": {
        "mean": -0.00031290784737783225,
        "ci95": [
          -0.006307158468458367,
          0.005489219817663508
        ],
        "families": 16
      }
    },
    {
      "total_updates": 4000,
      "cohort": "train",
      "metric": "joint",
      "parent": 0.078125,
      "candidate": 0.1953125,
      "candidate_minus_parent": {
        "mean": 0.1171875,
        "ci95": [
          0.0625,
          0.1796875
        ],
        "families": 32
      }
    },
    {
      "total_updates": 4000,
      "cohort": "train",
      "metric": "coarse_valid",
      "parent": 0.9921875,
      "candidate": 0.984375,
      "candidate_minus_parent": {
        "mean": -0.0078125,
        "ci95": [
          -0.03125,
          0.015625
        ],
        "families": 32
      }
    },
    {
      "total_updates": 4000,
      "cohort": "train",
      "metric": "motif_drms",
      "parent": 6.513468626886606,
      "candidate": 5.782612983719446,
      "candidate_minus_parent": {
        "mean": -0.7308556431671605,
        "ci95": [
          -1.2337602459971095,
          -0.19970823618350558
        ],
        "families": 32
      }
    },
    {
      "total_updates": 4000,
      "cohort": "train",
      "metric": "ca_lddt",
      "parent": 0.37926077491471044,
      "candidate": 0.4661980832629693,
      "candidate_minus_parent": {
        "mean": 0.08693730834825886,
        "ci95": [
          0.051806390286267275,
          0.12620481638136558
        ],
        "families": 32
      }
    },
    {
      "total_updates": 4000,
      "cohort": "development",
      "metric": "joint",
      "parent": 0.015625,
      "candidate": 0.0,
      "candidate_minus_parent": {
        "mean": -0.015625,
        "ci95": [
          -0.046875,
          0.0
        ],
        "families": 16
      }
    },
    {
      "total_updates": 4000,
      "cohort": "development",
      "metric": "coarse_valid",
      "parent": 0.96875,
      "candidate": 1.0,
      "candidate_minus_parent": {
        "mean": 0.03125,
        "ci95": [
          0.0,
          0.078125
        ],
        "families": 16
      }
    },
    {
      "total_updates": 4000,
      "cohort": "development",
      "metric": "motif_drms",
      "parent": 2.8548352206125855,
      "candidate": 3.3866354674100876,
      "candidate_minus_parent": {
        "mean": 0.531800246797502,
        "ci95": [
          0.1849875726969913,
          0.8882994921412318
        ],
        "families": 16
      }
    },
    {
      "total_updates": 4000,
      "cohort": "development",
      "metric": "ca_lddt",
      "parent": 0.299698670813013,
      "candidate": 0.2970377822582705,
      "candidate_minus_parent": {
        "mean": -0.0026608885547425264,
        "ci95": [
          -0.013236903301700617,
          0.008007962437855736
        ],
        "families": 16
      }
    }
  ]
}
```
