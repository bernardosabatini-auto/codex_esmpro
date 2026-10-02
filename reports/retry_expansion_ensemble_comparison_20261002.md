# Matched external bounded-retry results

All48 frozen development families, including all16 eligible two-state families. Raw and selected32 scored separately using unchanged definitions; all failures retained. Selected candidates compare against selected original, with all declared heads included.

| Pipeline | Selected CA-lDDT | Valid fraction | State coverage | Both-state fraction | MD W1 | Sampling quality | Training diversity |
|---|---:|---:|---:|---:|---:|---|---|
| original | 0.86796 | 1.00000 | 0.43750 | 0.06250 | 0.48850 | True | False |
| seed2026100171_expansion | 0.87213 | 1.00000 | 0.46875 | 0.06250 | 0.48500 | True | False |
| seed2026100181_expansion | 0.87187 | 1.00000 | 0.40625 | 0.06250 | 0.48594 | False | False |

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

## seed2026100171_expansion

- raw minus matched original, coverage_at_32: +0.03125, paired-family95% interval [-0.0625, 0.125].
- raw minus matched original, both_states: +0.00000, paired-family95% interval [0.0, 0.0].
- raw minus matched original, ca_lddt: +0.00419, paired-family95% interval [-0.00025184960579454604, 0.008294749582661402].
- raw minus matched original, coarse_valid: +0.00586, paired-family95% interval [0.0, 0.016276041666666668].
- raw minus matched original, md_w1: -0.00350, paired-family95% interval [-0.011300270767052449, 0.0036893342221589573].
- latent minus matched original, coverage_at_32: +0.03125, paired-family95% interval [-0.0625, 0.125].
- latent minus matched original, both_states: +0.00000, paired-family95% interval [0.0, 0.0].
- latent minus matched original, ca_lddt: +0.00417, paired-family95% interval [-0.00026765328072456997, 0.008261047570135543].
- latent minus matched original, coarse_valid: +0.00000, paired-family95% interval [0.0, 0.0].
- latent minus matched original, md_w1: -0.00350, paired-family95% interval [-0.011300270767052449, 0.0036893342221589573].

Selected-minus-raw coverage:+0.00000; validity:+0.00000; CA-lDDT:+0.00000; MD W1:+0.00000.
Recovered0/0 initially invalid outputs; exhausted0; attempts/output1.00000. Generation140.76s + retries0.00s; peak41.91GiB.

## seed2026100181_expansion

- raw minus matched original, coverage_at_32: -0.03125, paired-family95% interval [-0.09375, 0.0].
- raw minus matched original, both_states: +0.00000, paired-family95% interval [0.0, 0.0].
- raw minus matched original, ca_lddt: +0.00291, paired-family95% interval [-0.0017622485392383, 0.007282337667379415].
- raw minus matched original, coarse_valid: +0.00260, paired-family95% interval [-0.005208333333333333, 0.014322916666666666].
- raw minus matched original, md_w1: -0.00604, paired-family95% interval [-0.014716442775789648, 0.0014958101040104571].
- latent minus matched original, coverage_at_32: -0.03125, paired-family95% interval [-0.09375, 0.0].
- latent minus matched original, both_states: +0.00000, paired-family95% interval [0.0, 0.0].
- latent minus matched original, ca_lddt: +0.00391, paired-family95% interval [-0.0006098387785808785, 0.008160916798394438].
- latent minus matched original, coarse_valid: +0.00000, paired-family95% interval [0.0, 0.0].
- latent minus matched original, md_w1: -0.00256, paired-family95% interval [-0.008830311282913034, 0.0030997401351848786].

Selected-minus-raw coverage:+0.00000; validity:+0.00326; CA-lDDT:+0.00102; MD W1:+0.00348.
Recovered5/5 initially invalid outputs; exhausted0; attempts/output1.00326. Generation140.13s + retries1.24s; peak41.91GiB.

Replicated broader sampling quality:False; replicated broader training diversity:False.

MD W1 is better when lower and remains reported even when the formal quality gate passes. Generation timings exclude ESM, loading, controls, geometry selection and disk I/O; end-to-end timing is still required. Oracle CA-lDDT is nearest-reference quality per sample, never reference-based deployment selection. These are development results, not independent-test or equilibrium-population claims. Raw-model native failures remain unchanged.
