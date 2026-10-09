# Whole-chain anchored kinematics: CPU diagnostic

Representation tests only; no designability or learned-model claim.

```json
[
  {
    "arm": "native",
    "samples": 4,
    "mean_source_tm": 1.0,
    "stages": {
      "source": {
        "coarse": 4,
        "raw": 4,
        "connected": 4,
        "overlap_free": 4,
        "joint": 4
      },
      "constructed": {
        "coarse": 4,
        "raw": 4,
        "connected": 4,
        "overlap_free": 4,
        "joint": 4
      }
    }
  },
  {
    "arm": "parent6000",
    "samples": 16,
    "mean_source_tm": 0.5530168750000001,
    "stages": {
      "source": {
        "coarse": 16,
        "raw": 3,
        "connected": 16,
        "overlap_free": 14,
        "joint": 2
      },
      "constructed": {
        "coarse": 6,
        "raw": 6,
        "connected": 16,
        "overlap_free": 5,
        "joint": 5
      }
    }
  },
  {
    "arm": "retrieved",
    "samples": 16,
    "mean_source_tm": 0.57850875,
    "stages": {
      "source": {
        "coarse": 9,
        "raw": 6,
        "connected": 9,
        "overlap_free": 10,
        "joint": 4
      },
      "constructed": {
        "coarse": 6,
        "raw": 6,
        "connected": 9,
        "overlap_free": 9,
        "joint": 3
      }
    }
  }
]
```
