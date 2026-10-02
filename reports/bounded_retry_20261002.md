# Bounded geometry retry feasibility

CPU reuse of all16 frozen two-state development families. Four attempts per32 output slots, first coarse-valid draw only; exhausted slots return their original draw. Selection uses no reference scores. All128 historical draws and all failures remain in the raw record.

| Pipeline | Initially invalid | Recovered | Still invalid | Attempted draws/output | Feasible |
|---|---:|---:|---:|---:|---|
| original | 9/512 | 9 | 0 | 1.02148 | True |
| compact500 | 5/512 | 5 | 0 | 1.00977 | True |

## original selected32 versus raw32

- valid_fraction: 0.98242 → 1.00000; change +0.01758, paired-family95% interval [0.0, 0.046875].
- oracle_ca_lddt: 0.89329 → 0.89334; change +0.00005, paired-family95% interval [-6.6157282593709565e-06, 0.00013428713588412716].
- coverage: 0.43750 → 0.43750; change +0.00000, paired-family95% interval [0.0, 0.0].
- both_states: 0.06250 → 0.06250; change +0.00000, paired-family95% interval [0.0, 0.0].

## compact500 selected32 versus raw32

- valid_fraction: 0.99023 → 1.00000; change +0.00977, paired-family95% interval [0.0, 0.02734375].
- oracle_ca_lddt: 0.90231 → 0.90306; change +0.00074, paired-family95% interval [-2.1872407714652875e-05, 0.002255892280512907].
- coverage: 0.43750 → 0.43750; change +0.00000, paired-family95% interval [0.0, 0.0].
- both_states: 0.06250 → 0.06250; change +0.00000, paired-family95% interval [0.0, 0.0].

## Matched compact500 minus original

- raw coverage: +0.00000, paired-family95% interval [-0.09375, 0.09375].
- raw both_states: +0.00000, paired-family95% interval [0.0, 0.0].
- raw valid_fraction: +0.00781, paired-family95% interval [-0.017578125, 0.0390625].
- raw oracle_ca_lddt: +0.00902, paired-family95% interval [0.003613434446520449, 0.014826417441193642].
- retry coverage: +0.00000, paired-family95% interval [-0.09375, 0.09375].
- retry both_states: +0.00000, paired-family95% interval [0.0, 0.0].
- retry valid_fraction: +0.00000, paired-family95% interval [0.0, 0.0].
- retry oracle_ca_lddt: +0.00972, paired-family95% interval [0.004545613269558203, 0.015154715063361357].

Declared feasibility criterion: True.

Attempted draws are a simulation cost proxy, not measured latency. Both source jobs already generated2048 draws. No runtime, memory or independent-generalization claim. Raw model gates are unchanged; this separately defined retry pipeline needs its own matched native and external evaluation before promotion. State coverage cannot decrease here because initially valid draws are retained; unchanged coverage is not evidence of new modes.
