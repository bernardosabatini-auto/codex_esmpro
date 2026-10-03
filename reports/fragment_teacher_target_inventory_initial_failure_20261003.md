# Teacher-target source inventory correction

The first CPU audit stopped before target selection: the expanded-data source list omitted the four immutable teacher shards used by the original32training proteins. The corrected audit includes those shards only when their expected label hashes agree across the already bound training rows and their source manifests are complete; every label file is rehashed and every reference backbone/latent and sequence identity is checked. No eligibility threshold, condition, sequence or target changed. No GPU job was launched.
