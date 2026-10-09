# Isolated-fragment context-code flow

```json
{
  "status": "complete",
  "qualified": true,
  "profile_only": true,
  "updates": 40,
  "data_manifest_sha256": "6b68e7b861a98a4c6865b7df2f681a2f1a173205f2954597f77ac2f395504604",
  "manifest_sha256": "2defd25098ab6e57e6fa3b93ccd5794910ee6cbffefd92745e03ccfa34fdb2b1",
  "counts": {
    "train": 464,
    "validation": 16,
    "evaluation": 32
  },
  "recommended_full_minutes": 7,
  "elapsed_seconds": 18.15847169002518,
  "interpretation": "Technical qualification only; loss and sampled latent diversity do not establish structural designability.",
  "arms": {
    "isolated": {
      "training_seconds": 2.2346761832013726,
      "peak_reserved_GiB": 0.203125,
      "parameters": 805256,
      "sensitivity": 0.0002879798412322998,
      "checkpoint_sha256": "fefa19a594a00e91d67032811fa32c50fc16aa54abced6e677e4ffc69f4886e1",
      "codes_sha256": "bafd890011dbadb13bacc6fe53e316e2c38ad47e2cd824fd76106a8e63cd431b",
      "initial_loss": 2.0076755434274673,
      "final_validation_loss": 1.9762314533193905,
      "final_training_loss": 1.7934901118278503,
      "mean_per_target_code_std": 0.6161864399909973
    },
    "ablated": {
      "training_seconds": 0.2520404583774507,
      "peak_reserved_GiB": 0.205078125,
      "parameters": 805256,
      "sensitivity": 0.0,
      "checkpoint_sha256": "c21894ee8ab9a9434d42d2652986ac74c9b0d082a394bb8fc9c1ec6ab1336b29",
      "codes_sha256": "7215c5efb032f9bc8f521094fd65f36300c832cbcb3ec893067b0c040489493d",
      "initial_loss": 2.0076755434274673,
      "final_validation_loss": 1.9762619783480961,
      "final_training_loss": 1.7933602273464202,
      "mean_per_target_code_std": 0.616186261177063
    }
  }
}
```
