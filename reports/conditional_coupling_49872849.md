# Matched conditional noise/teacher coupling

All32families are training data. Teacher states are predictions,not biological populations. No independent tests or promotion.

All500target/label/noise/time/dropout/RNG traces matched; all4096archived predictions and initial output identity audited.

| Arm | Recall@32 | Coarse valid | Teacher CA-lDDT | Reference CA-lDDT | Balanced TV |
|---|---:|---:|---:|---:|---:|
| initial | 0.74821 | 0.98828 | 0.89806 | 0.88196 | 0.53133 |
| independent | 0.88393 | 0.99609 | 0.95760 | 0.92575 | 0.37547 |
| optimal | 0.87738 | 0.99219 | 0.95681 | 0.92527 | 0.38826 |

Optimal minusinitial: recall +0.12917,95%family interval [0.04583333333333334, 0.21666666666666667]; validity +0.00391.

Optimal minusindependent: recall -0.00655,95%family interval [-0.05029761904761905, 0.03720238095238096]; validity -0.00391.

Qualified for replication/native screen: False. Checks: {'recall_vs_control': False, 'recall_vs_initial': True, 'validity': True, 'teacher_fidelity': True}.
