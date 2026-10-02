# Matched external bounded-retry results

All48 frozen development families, including all16 eligible two-state families. Raw and selected32 scored separately using unchanged definitions; all failures retained. Selected candidates compare against selected original, with all four heads included.

| Pipeline | Selected CA-lDDT | Valid fraction | State coverage | Both-state fraction | MD W1 | Sampling quality | Training diversity |
|---|---:|---:|---:|---:|---:|---|---|
| original | 0.86796 | 1.00000 | 0.43750 | 0.06250 | 0.48850 | True | False |
| compact500 | 0.87286 | 1.00000 | 0.43750 | 0.06250 | 0.48941 | True | False |
| seed2026100171_balanced | 0.87490 | 1.00000 | 0.34375 | 0.00000 | 0.49485 | False | False |
| seed2026100181_balanced | 0.87445 | 1.00000 | 0.34375 | 0.00000 | 0.49017 | False | False |

## original

- raw minus matched original, coverage_at_32: +0.00000, paired-family95% interval [0.0, 0.0].
- raw minus matched original, both_states: +0.00000, paired-family95% interval [0.0, 0.0].
- raw minus matched original, ca_lddt: +0.00000, paired-family95% interval [0.0, 0.0].
- raw minus matched original, coarse_valid: +0.00000, paired-family95% interval [0.0, 0.0].
- raw minus matched original, md_w1: +0.00000, paired-family95% interval [0.0, 0.0].
- latent minus matched original, coverage_at_32: +0.00000, paired-family95% interval [0.0, 0.0].
- latent minus matched original, both_states: +0.00000, paired-family95% interval [0.0, 0.0].
- latent minus matched original, ca_lddt: +0.00000, paired-family95% interval [0.0, 0.0].
- latent minus matched original, coarse_valid: +0.00000, paired-family95% interval [0.0, 0.0].
- latent minus matched original, md_w1: +0.00000, paired-family95% interval [0.0, 0.0].

Selected-minus-raw coverage:+0.00000; validity:+0.00586; CA-lDDT:+0.00003; MD W1:+0.00000.
Recovered9/9 initially invalid outputs; exhausted0; attempts/output1.00716. Generation264.77s + retries5.34s; peak41.93GiB.

## compact500

- raw minus matched original, coverage_at_32: +0.00000, paired-family95% interval [-0.09375, 0.09375].
- raw minus matched original, both_states: +0.00000, paired-family95% interval [0.0, 0.0].
- raw minus matched original, ca_lddt: +0.00455, paired-family95% interval [-0.00032180615606606724, 0.009213545792516186].
- raw minus matched original, coarse_valid: +0.00195, paired-family95% interval [-0.006510416666666667, 0.012369791666666666].
- raw minus matched original, md_w1: -0.00418, paired-family95% interval [-0.017040087707280306, 0.0062094508261517035].
- latent minus matched original, coverage_at_32: +0.00000, paired-family95% interval [-0.09375, 0.09375].
- latent minus matched original, both_states: +0.00000, paired-family95% interval [0.0, 0.0].
- latent minus matched original, ca_lddt: +0.00489, paired-family95% interval [5.027585543574882e-05, 0.009488289837311448].
- latent minus matched original, coarse_valid: +0.00000, paired-family95% interval [0.0, 0.0].
- latent minus matched original, md_w1: +0.00091, paired-family95% interval [-0.006283060708569092, 0.007814092992915111].

Selected-minus-raw coverage:+0.00000; validity:+0.00391; CA-lDDT:+0.00037; MD W1:+0.00509.
Recovered6/6 initially invalid outputs; exhausted0; attempts/output1.00391. Generation131.47s + retries1.87s; peak41.89GiB.

## seed2026100171_balanced

- raw minus matched original, coverage_at_32: -0.09375, paired-family95% interval [-0.1875, 0.0].
- raw minus matched original, both_states: -0.06250, paired-family95% interval [-0.1875, 0.0].
- raw minus matched original, ca_lddt: +0.00618, paired-family95% interval [0.001289316806831579, 0.010733512402359225].
- raw minus matched original, coarse_valid: +0.00391, paired-family95% interval [-0.0026041666666666665, 0.014973958333333334].
- raw minus matched original, md_w1: +0.00418, paired-family95% interval [-0.007438895712772728, 0.019363900632613604].
- latent minus matched original, coverage_at_32: -0.09375, paired-family95% interval [-0.1875, 0.0].
- latent minus matched original, both_states: -0.06250, paired-family95% interval [-0.1875, 0.0].
- latent minus matched original, ca_lddt: +0.00694, paired-family95% interval [0.002006366984695732, 0.011433592598284605].
- latent minus matched original, coarse_valid: +0.00000, paired-family95% interval [0.0, 0.0].
- latent minus matched original, md_w1: +0.00635, paired-family95% interval [-0.004590166890341921, 0.021161363747455145].

Selected-minus-raw coverage:+0.00000; validity:+0.00195; CA-lDDT:+0.00079; MD W1:+0.00217.
Recovered3/3 initially invalid outputs; exhausted0; attempts/output1.00260. Generation140.14s + retries0.76s; peak41.91GiB.

## seed2026100181_balanced

- raw minus matched original, coverage_at_32: -0.09375, paired-family95% interval [-0.1875, 0.0].
- raw minus matched original, both_states: -0.06250, paired-family95% interval [-0.1875, 0.0].
- raw minus matched original, ca_lddt: +0.00652, paired-family95% interval [0.00117777096081285, 0.011453124295718958].
- raw minus matched original, coarse_valid: +0.00586, paired-family95% interval [0.0, 0.016276041666666668].
- raw minus matched original, md_w1: +0.00168, paired-family95% interval [-0.005478030405786049, 0.008343750427710381].
- latent minus matched original, coverage_at_32: -0.09375, paired-family95% interval [-0.1875, 0.0].
- latent minus matched original, both_states: -0.06250, paired-family95% interval [-0.1875, 0.0].
- latent minus matched original, ca_lddt: +0.00649, paired-family95% interval [0.0011534315596123212, 0.01143016124826277].
- latent minus matched original, coarse_valid: +0.00000, paired-family95% interval [0.0, 0.0].
- latent minus matched original, md_w1: +0.00168, paired-family95% interval [-0.005478030405786049, 0.008343750427710381].

Selected-minus-raw coverage:+0.00000; validity:+0.00000; CA-lDDT:+0.00000; MD W1:+0.00000.
Recovered0/0 initially invalid outputs; exhausted0; attempts/output1.00000. Generation141.06s + retries0.00s; peak41.91GiB.

Replicated broader sampling quality:False; replicated broader training diversity:False.

MD W1 is better when lower and remains reported even when the formal quality gate passes. Generation timings exclude ESM, loading, controls, geometry selection and disk I/O; end-to-end timing is still required. Oracle CA-lDDT is nearest-reference quality per sample, never reference-based deployment selection. These are development results, not independent-test or equilibrium-population claims. Raw-model native failures remain unchanged.
