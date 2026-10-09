# Whole-chain bond projection: CPU diagnostic

```json
{
  "gate": {
    "native": true,
    "native_cond": false,
    "generated": false
  },
  "summary": {
    "generated_cond": {
      "samples": 16,
      "failures": 0,
      "mean_source_tm": 0.574494375,
      "minimum_source_tm": 0.47944,
      "stages": {
        "source": {
          "coarse_valid": 13,
          "raw_gate_passed": 13,
          "connected": 0,
          "overlap_free": 13,
          "joint": 0
        },
        "projected": {
          "coarse_valid": 3,
          "raw_gate_passed": 3,
          "connected": 16,
          "overlap_free": 2,
          "joint": 2
        }
      }
    },
    "generated_untrained": {
      "samples": 16,
      "failures": 0,
      "mean_source_tm": 0.481173125,
      "minimum_source_tm": 0.36717,
      "stages": {
        "source": {
          "coarse_valid": 12,
          "raw_gate_passed": 12,
          "connected": 0,
          "overlap_free": 5,
          "joint": 0
        },
        "projected": {
          "coarse_valid": 2,
          "raw_gate_passed": 2,
          "connected": 16,
          "overlap_free": 0,
          "joint": 0
        }
      }
    },
    "native_cond": {
      "samples": 16,
      "failures": 0,
      "mean_source_tm": 0.6277962500000001,
      "minimum_source_tm": 0.46374,
      "stages": {
        "source": {
          "coarse_valid": 16,
          "raw_gate_passed": 16,
          "connected": 0,
          "overlap_free": 16,
          "joint": 0
        },
        "projected": {
          "coarse_valid": 4,
          "raw_gate_passed": 4,
          "connected": 16,
          "overlap_free": 4,
          "joint": 4
        }
      }
    },
    "native_reference": {
      "samples": 4,
      "failures": 0,
      "mean_source_tm": 0.999995,
      "minimum_source_tm": 0.99998,
      "stages": {
        "source": {
          "coarse_valid": 4,
          "raw_gate_passed": 4,
          "connected": 4,
          "overlap_free": 4,
          "joint": 4
        },
        "projected": {
          "coarse_valid": 4,
          "raw_gate_passed": 4,
          "connected": 4,
          "overlap_free": 4,
          "joint": 4
        }
      }
    }
  },
  "bounds": {
    "lengths": [
      [
        1.4427532893985051,
        1.49673634413943
      ],
      [
        1.5093534108994473,
        1.5658643189287593
      ],
      [
        1.3195317942140217,
        1.357477521927836
      ]
    ],
    "angles": [
      [
        2.076686300797161,
        2.3578296349624117
      ],
      [
        1.8047005033898642,
        2.129226322716969
      ],
      [
        1.958591284566695,
        2.174824941689956
      ]
    ]
  }
}
```
