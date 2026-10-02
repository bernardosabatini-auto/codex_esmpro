# Teacher-mode learnability and pose ablation

Authorized through October 2, 2026, 11 AM America/New_York (15:00 UTC), with at most eight project GPUs running plus pending. The submission guard now enforces the deadline. Only registered own jobs are inspected or modified. Completion monitoring remains active.

Selection is frozen before inspecting any student predictions: 32 members of the prior512 training set, eight per length bucket, ranked by teacher-defined contact-state count and dispersion. All32 selected targets have16 distinguishable valid teacher conformations. These are predicted modes, not biological states or equilibrium populations. All source labels and selection hashes are bound. Locked tests remain untouched.

The first capacity experiment uses pure uniform teacher supervision, rather than the previous50/50 reference mixture, against a reference-only arm. The two teacher arms differ only in fixed-reference versus independent-PCA encoding. Every reference latent remains bitwise identical to its inherited cache. Target order, label draws, initialization and stochastic training streams are matched. Planned2000updates, learning rate3e-5, checkpoints500/2000, fresh32-sample evaluation at CFG1 and CFG2. Preserve every result; no post-hoc guidance selection hidden from reports.

## Label audit first

Job49690071 encodes/audits all512selected conformations in both frames. Three-step decoding achieves mean CA-lDDT0.99597 aligned and0.99530 PCA, but coarse validity drops from1.0 at input to0.96094 and0.95117. Both fail the unchanged1-percentage-point reconstruction-validity margin. This deliberately difficult subset reveals an AE/decoder limitation that the full-corpus mean concealed. Training has not been launched through this failed gate.

Follow-up decision before seeing outcomes: repeat the same label audit with10 decoder steps, identical conformations and noise, before any training. Do not remove failed samples or relax thresholds. If it passes, the capacity experiment and its initialization baseline will both use10 steps; that would not justify a speed claim. If it fails, inspect reconstruction errors and decoder limitations before deciding whether a defensible capacity test remains possible.

## Pre-training revision to a reliable capacity panel

Ten decoder steps (49691755) improve validity to0.97461 aligned and0.98047 PCA but both still fail the unchanged gate. The extreme-diversity panel has mean teacher confidence0.705, range0.436–0.889, and13/32 targets lack the required confident core. Maximum teacher dispersion was the wrong priority for an easy capacity diagnostic. Both failed audits remain reported; no training was performed on that panel.

Before any student outcome is available, freeze a second panel using confident teacher conformations: mean pLDDT>=0.8, a confident core covering at least max(32,ceil(L/2)),2..8 contact states and mean contact-feature distance<=6A. Only five short proteins satisfy these rules, so take those five and the nine highest-confidence eligible proteins in each other bucket (32 total). Keep all16 conformations of every selected protein and audit both encodings at3decoder steps. This is explicitly a selected easy-capacity test, not a generalization benchmark. Source data, definitions and rejected-panel results are retained. Frozen protocol: `configs/overfit_reliable_protocol.json`.

## Validation and additional diagnostics

CPU checks confirm teacher self-recall and invariance of contact assignment under a proper rigid pose change. Unit checks confirm invalid geometry cannot count as a contact-state hit and identical teacher structures do not create distinct modes. The environment lacks pytest; the two test functions were executed directly with the existing environment, without installing packages.

Noise-time-binned velocity MSE is logged during training to distinguish poor early-flow transport from failures near a known target. No objective or random draws change for this diagnostic. The stricter1A contact-hit threshold is reported alongside the frozen2A primary threshold. CFG1 is the primary capacity comparison and CFG2 is retained as a sensitivity analysis (`configs/overfit_decisions.json`).

A read-only analysis of the previously failed20-step paired sampler found several non-neighboring CA distances near1–1.5A, including one below1A. Its failures are substantial collisions, not merely floating-point changes at a validity threshold. No threshold relaxation or unvalidated structure repair is adopted.

The reliable panel retains the pose effect being tested: median additional PCA frame angle10.40degrees,22.85% of conformations exceed90degrees, and15/32 proteins contain at least one such change. Mean teacher confidence ranges0.822–0.967. Thus confidence selection did not remove the orientation discontinuity. Selection and pose summary arrays remain excluded from Git.

A read-only analysis of existing original-student25-step CFG2 latent samples on the frozen reliable panel finds mean nearest-teacher latent RMSE0.4254, teacher latent spread0.0625, and student latent spread0.2084. These quantities use a coordinate-dependent latent representation and are not structural accuracy measures. To separate pose from geometry, each capacity evaluation additionally re-encodes generated backbones before and after a single global fit to the cached reference. Those fits are diagnostic only: generated samples, scoring coordinates and inference remain unchanged. All frame comparisons still use identical evaluation code.

Read-only encoder inspection also clarifies the rotation verdict: coordinate components enter unconstrained learned linear layers, consistent with rotation-dependent codes. A deterministic canonicalization wrapper can make the composite encoding mapping invariant without retraining ProteinAE; changing that wrapper still changes the target convention for the pretrained prediction head. The earlier stronger wording has been corrected in `rotation_verdict_20261001.md`.

## Reliable-panel audit passed

Job49693246 completes the full512-conformation audit: mean CA-lDDT0.999111 for fixed-reference encoding and0.999091 for independent PCA; both decoded coarse-valid fractions are0.998047 versus1.0 at input. Both pass the original reconstruction gate. The fixed handoff submits40-update capacity profile49702037. No training input or sample was removed after this audit. Exact ESM-array and cached-reference-array identity checks precede training configuration preparation.

## Matched training submitted

Capacity profile49702037 completes40updates in81.99seconds of training with64.96GiB peak reserved GPU memory. Training SM issue is57.24%; whole-capture issue is20.12% because startup dominates this short profile. Do not describe the short allocation as meeting the50% whole-run goal. The longer runs amortize startup and will be measured separately.

The fixed handoff submitted reference49704029, aligned-teacher49704255 and PCA-teacher49704413, all from commit9be9139 with identical scientific code trees and configuration except arm. Each requests one H200,24GiB host memory,8CPUs and115minutes; the profile suggests roughly68minutes of training plus evaluation. The handoff timer stopped after all submissions; the completion watcher remains active. No manual duplicate submissions are needed.

The [Gaussian-bridge oracle diagnostic](overfit_teacher_bridge_20261001.md) uses only these teacher labels and simulated noise. At time0, per-coordinate conditional velocity variance is0.007592 aligned versus0.086632 PCA (11.4-fold), while the physical-mode prior is identical. By time0.5, oracle state classification is0.895 and0.919 respectively. This exposes nuisance variation and time dependence but does not establish a trained-model advantage. Actual matched training and structure evaluation decide that question.

## Oracle transport positive control

A separate diagnostic uses the exact empirical-teacher Gaussian-mixture velocity field, with identical fresh Gaussian seeds, ordinary Euler integration at5/10/25/100steps, the same final per-residue layer normalization, and3-step decoding. Both frames and all32 proteins are retained. CPU preparation takes6.7seconds. Single-teacher endpoint and orthogonal latent-transform controls pass. This oracle knows every teacher latent and is explicitly not a deployable sequence predictor. Its role is to show whether correct velocity fields can recover valid teacher modes through this sampler/decoder, separating a learned-head failure from an integration or representation limitation. It does not replace or alter the three matched training runs.

Oracle transport job49708850 completed successfully. At25Euler steps, aligned latents recover96.92% of teacher-defined states and independent PCA recovers91.95%, with99.90% coarse-valid decoded samples in both cases. At100steps these are96.92% and92.40%; the aligned result has already plateaued by25steps. This single shared seed set demonstrates high attainable teacher-mode recall through the existing sampler and decoder; it is neither a learned-model result nor evidence for biological population recovery. The expected recall from32 direct independent teacher draws is94.51%; a realized finite seed set can exceed that expectation. See [full control](oracle_transport_49708850.md).

## Verified shared initialization

All three completed baseline evaluations match, including sample state assignments. At CFG1, teacher-mode recall is 0.74747 with coarse validity 0.99219; at CFG2 recall is 0.56741 with validity 0.99121. Strict 1 Å recall is 0.50446 and 0.35729. Both guidance settings remain reported; CFG1 was declared primary before training. See [baseline comparison](overfit_comparison_0.md).

The CFG1 nearest-teacher latent RMSE is 0.44329, whereas re-encoding globally aligned predicted backbones gives 0.13363. At CFG2 these are 0.43580 and 0.11507. Decoder-to-encoder RMSE is about 0.0055. Much of the raw latent discrepancy is therefore associated with global pose; the alignment is diagnostic only and does not alter any generated prediction or structural score.

Posterior-target profile job49712994 tests the cost of an objective-preserving reduction in target noise, using one H200 for 40 updates. The [declared plan and equivalence tests](posterior_target_plan_20261001.md) precede any full training with that estimator.

## Posterior-target profile passed

Job49712994 completed 40 updates in 80.88 seconds with 64.72 GiB peak reserved memory, compared with 81.99 seconds and 64.96 GiB for the ordinary aligned-target profile. Training SM issue was 58.05%; whole-capture SM issue was 21.69%. Startup dominates the short capture. Sparse logged conditional variance averaged 0.002203, or 3.43% of the logged objective; this is not a measurement of gradient-variance reduction. The method is computationally viable, but its expected benefit appears modest and no full posterior-target training has been launched. See [profile](overfit_49712994.md).

A live check caught terminal accounting while a completed job still appeared as COMPLETING in Slurm. Scheduler queries now always consult the live queue for exact registered IDs and give live allocation state precedence. Regression tests cover the race and fail closed on a live-query error; a real query of all 30 nonterminal-registry IDs found exactly the three running training jobs, with none missing. No cap violation occurred.

Before any 500-update scores were available, comparison reports were extended to display paired family-bootstrap intervals and explicitly evaluate the already-declared capacity screen: recall gain at least 0.10 versus reference, positive recall interval lower bounds versus reference and initialization, and no more than 0.01 loss in validity versus initialization. The label manifest hash binds the family mapping. All 32 targets belong to distinct frozen families, so making that mapping explicit leaves existing baseline intervals unchanged. Intervals are unadjusted; an intermediate pass is provisional and a final capacity pass is not model promotion.

## Finite-sample calibration of the oracle control

A CPU simulation of 100,000 repeated experiments, each drawing 32 empirical teacher labels independently for each of the 32 proteins, has mean recall 0.94526 versus analytic expectation 0.94512. Its central 95% repeated-sampling range is [0.89940, 0.98333]. Both aligned and PCA 25-step oracle results lie inside that range. This is a distribution of repeated finite-label draws, not a confidence interval on biological populations or a paired test between frames. The 0.9692 versus 0.9195 oracle point difference must not be presented as proof of an alignment advantage. The control establishes attainable recall; actual matched learning comparisons address the training question. Reproduce with `scripts/diagnose_teacher_sampling.py`, seed2026100171.

## Larger-batch throughput profile

The measured 64.96 GiB peak of the ordinary profile leaves room within the existing 110 GiB capacity gate. A single-H200, 40-update profile will test batches64/32/16/12 at padded lengths128/256/384/512, versus32/16/8/8 previously. Its purpose is throughput and memory measurement only; changed batch sizes do not constitute a matched optimization experiment. Compare processed samples and padded residues per training second, not update time alone. Keep the three active training arms unchanged and use any accepted batching change consistently in future matched experiments.

Larger-batch profile submitted as job49716889, one H200 with a 10-minute walltime. No new full training arm is submitted while the 500-update comparisons remain incomplete.

## 500-update result and next intervention

The [matched comparison](overfit_comparison_500.md) does not pass the preregistered capacity criterion. At CFG1, recall is 0.42321 reference, 0.67932 aligned teacher and 0.61310 PCA teacher, versus 0.74747 initially. Aligned minus PCA is +0.06622 (unadjusted paired family 95% interval [0.01042, 0.13393]); this is a single-seed intermediate result. Aligned teacher CA-lDDT improves from 0.89841 to 0.96479, with unchanged coarse validity0.99219. Empirical-state TV improves from 0.51074 to 0.17773. Better structure and frequency agreement have not yet produced better total state recall.

The [frequency diagnostic](overfit_state_frequency_500.md) isolates the deficit: aligned training hits21/51 singleton teacher states (41.18%), versus expected87.32% hit probability for32 independent teacher draws, but all29 majority states. PCA hits16/51 singleton states (31.37%). Equal-state sampling is therefore a targeted next intervention, while the original runs continue to2000. The two new frame arms retain the original initialization,2000 updates, learning rate, batches and inference. One uniform label draw is consumed per example in every arm; the balanced inverse-CDF mapping changes only the intended teacher prior. The previous broad balanced run used a different, incompatible N-terminal frame, a50% reference mixture and different clusters; its negative result remains retained. This test concerns rare-state learnability on the corrected small panel.

The [balanced protocol](../configs/overfit_balanced_protocol.json) was declared before submission. Original empirical state-TV remains visible alongside TV to the equal-state prior. Full posterior-target training is deferred because its estimated target-noise contribution is small relative to the measured rare-state deficit. No full-data expansion or model promotion is justified yet.

When adding throughput fields, I regenerated the original profile JSON used by the training configurations. It has been restored byte-for-byte with its recorded SHA2563f088ee2146a2c79b56163c6e473f59d28becb49623450c3032aa5d422ae25eb using the original summarizer; the enriched JSON is retained separately as `overfit_49702037_throughput.json`. No score or authorization threshold changed.

Balanced aligned49718446 and balanced PCA49718483 were submitted from the same commitff8376f, one H200 and115minutes each, with completion summaries registered. The three empirical/reference runs and larger-batch profile bring the total to six running-plus-pending project GPUs at submission. No posterior-target full run was submitted.

## Fixed checkpoint analysis monitoring

The completion watcher now also executes the fixed empirical and balanced500/2000 comparisons once all required checkpoint scores are present. It validates exact registered ownership, runs CPU analysis with CUDA hidden, handles at most one comparison/frequency-report pair per tick, and retries failures. It does not submit experiments. The first automatic empirical500 comparison reproduces the manual JSON byte-for-byte (SHA2566cf7ed94517d0297bc4bf58ba6efa66619ee21b44b0a0f7087a902aac5c00f08). Tests cover incomplete checkpoints, duplicate execution, ownership, retries, confounded comparisons and invalid-sample accounting. An identical-prediction dry run with real frozen metadata gives exactly zero balanced-versus-empirical differences and intervals; no synthetic experiment output was saved.

## Fresh teacher recurrence control prepared

The original16 teacher conformations share one stochastic ESMFold2 trunk realization. A new bounded control reproduces those structures, verifies RNG-restored sampler replay, and generates32 fresh diffusion samples with that trunk and32 with a newly sampled trunk. The two conditions use the same new diffusion seeds. All states, contact features and current training labels remain frozen. Every model artifact was rehashed on CPU before scheduling, avoiding GPU time spent hashing26GB of weights. Tests confirm that the reproduction check accepts rigid pose changes and rejects structural changes, and that the new random streams are stable and distinct. Full GPU replay controls are required before fresh samples are scored.

The earlier87.3% singleton-hit reference resamples the16 stored empirical labels; it is not a measured recurrence rate from fresh ESMFold2 generations. The new diagnostic addresses that distinction. Its plan is [teacher recurrence protocol](../configs/teacher_recurrence_protocol.json); one H200,25-minute cap, no training or test-set selection based on these outcomes.

Fresh teacher recurrence was submitted as job49722263 from commit8955195, one H200 with a25-minute walltime and registered `summarize_teacher_recurrence` completion action. The registered running-plus-pending count was seven at submission.

## Completed empirical 2,000-update test

The [final comparison](overfit_comparison_2000.md) passes all matching controls but neither teacher arm passes the capacity screen. Primary CFG1 recall is0.37262 reference,0.62500 aligned and0.66369 PCA, versus0.74747 at initialization. Aligned versus initialization is-0.12247 with paired95% interval[-0.22292,-0.01875]. Aligned minus PCA is-0.03869[-0.10595,0.03333]: its intermediate frame advantage disappears. Both teacher arms reach0.99902 coarse validity and approximately0.982 teacher CA-lDDT. These are accurate teacher-like samples with deficient rare-state coverage, not a successful generative improvement. Singleton hits are15/51 aligned and21/51 PCA, versus27/51 initially; both hit all29 majority states. Keep the original model and await balanced-state tests; no full-data expansion follows this failure.

The exposure replay matches all logged target/label hashes. The [500-update diagnostic](overfit_exposure_500.md) finds fewer late-time examples for long proteins, but the most-exposed short group loses coverage while the longest group slightly improves. Exposure alone is not a sufficient failure diagnosis. No noise-time sweep was launched. The2000-update replay is retained separately.

## Larger-batch measurement and solver screen

Profile49716889 completes40 updates in137.50 seconds using90.62GiB. Throughput is9.02 examples/s and2085.24 padded residues/s, versus7.81 and1873.40 in the original short profile: approximately15.5% and11.3% higher. The length mix differs, so these are descriptive work-normalized measurements, not a clean fixed-work causal estimate. Training SM issue rises from57.24% to61.02%; short-profile whole-capture issue is41.22%. The full aligned training/evaluation capture reaches64.08% SM issue, clearing the requested50% at that counter. It is not a FLOP-efficiency measurement. Preserve matched batches for all current training arms.

An inference-only [solver protocol](../configs/midpoint_protocol.json) compares Euler25/16/20 CFG2, midpoint8/10 CFG2 and Euler25 CFG1 on the existing64 tuning families and three seeds. Midpoint uses two field evaluations per interval; matched Euler controls distinguish integrator changes from evaluation count. The default Euler implementation is bitwise identical to committed code on a CPU pair-model control at CFG1/2. Unit checks cover evaluation counts, analytic linear-field error and self-conditioning updates. This does not establish second-order accuracy for a learned history-dependent field. GPU controls must reproduce the original baseline and validate batching. No optimizer, pair-label training data or locked tests are used. Passing the reference-quality screen permits ensemble and resident-latency follow-up, not a speed or diversity claim.

Solver screen submitted as49728184 from67d14dd, one H200 and15minutes; four project GPUs running-plus-pending at submission. Its registered completion analysis includes all six settings.

Follow-up rule for the inference-only screen, fixed before its GPU output: among quality-qualified nonbaseline settings, test the one with the fewest nominal network forwards; ties prefer Euler over midpoint, then the protocol order. Evaluate that setting on the complete48-protein development ensemble panel with original seeds and the existing geometry, reference-quality and coverage gate. Only a passing ensemble screen merits a matched resident sequence-to-backbone latency run including ESMC, sampler and decoder against both original student and direct teacher. This limits screening cost and does not select by a favorable noisy point estimate. Keep every initial screen result visible. The existing ensemble/latency entry points now accept the solver and guidance explicitly while preserving old defaults. No follow-up is scheduled before the required scores exist.

## Fresh teacher recurrence completed

Job49722263 completed all32 proteins with64 replay/reproduction controls. Original-label maximum CA RMSD is0.000144A and replay maximum0.000169A; peak reserved memory77.61GiB. [Fresh teacher recall](teacher_recurrence_49722263.md) is0.83661 with the original trunk and0.85119 with a new trunk, with100% coarse validity. Singleton hits are32/51 and33/51, lower than the87.3% stored-label resampling expectation; that expectation is not the fresh teacher distribution. With matched new diffusion seeds, changing the trunk changes all32 proteins' predictions (mean paired CA RMSD0.16565A; per-protein means0.01761–0.91489A), confirming the two conditions are distinct.

The [post-hoc student comparison](teacher_student_recurrence_2000.md) finds31 singleton states in both fresh teacher conditions, one only in the fixed-trunk condition, two only in the new-trunk condition, and17 in neither finite sample. On the31 recurring in both, initialization hits22, aligned2000 hits11 and PCA2000 hits14. The decline therefore includes repeatedly generated teacher states; it is not explained solely by nonrecurring singleton labels. This diagnostic changes no state, score denominator, prior or gate. Counts pooled over states are descriptive; family-level intervals are reported separately. Teacher generation still does not establish biological populations.

The completed teacher control leaves two balanced training jobs active and the one-GPU solver screen queued. Balanced checkpoint comparisons remain monitored automatically.

## Latent-label versus decoded-state check

A CPU [nearest-latent identity diagnostic](latent_state_assignments_empirical.md) uses each arm's own training-frame labels and checks exact teacher self-assignment. At2000, permissive latent singleton recall is20/51 aligned and26/51 PCA, compared with decoded valid hits15/51 and21/51. Sample identity agreement is86.9% and85.7%; at initialization it is only42–44%. Raw latent identity has no validity or distance gate and is strongly affected by pose, so it cannot replace contact-state evaluation or establish that the decoder causes missed modes. Both latent and structural diagnostics show deficits; neither justifies a decoder-only fix.

Missing a specified state in32 samples also does not establish zero model probability: the exact one-sided95% binomial upper bound after0/32 hits is0.0894, greater than1/16. Larger ensembles could distinguish very low from zero probability, but they would not repair the demonstrated coverage loss at the matched32-sample budget. Balancing the training prior remains the targeted intervention before spending on a larger sampling budget.

## Inference solver screen failed

All1152 samples and24 batching controls completed in job49728184; the original Euler25 baseline reproduces exactly. [Every cheaper setting fails](midpoint_49728184.md) the unchanged gate. Euler16 loses0.00678 CA-lDDT and1.56points validity. Midpoint8/10 show severe losses: CA-lDDT0.67461/0.69770 and valid fractions0.42188/0.61979. The analytic CPU solver check therefore does not translate into acceptable integration of this learned, self-conditioned field. No midpoint ensemble or latency follow-up is justified. Euler25 CFG1 loses0.01030 CA-lDDT despite its diversity advantage on the training panel; it is not a qualified speed replacement.

Uniform Euler20 comes closest: CA-lDDT delta-0.00212 with interval[-0.00423,-0.000028] passes the accuracy margin, but validity falls from188/192 to186/192, a0.0104167 loss, exceeding the0.01 margin. The threshold is not relaxed or rounded into a pass. The ensemble preparer correctly rejects all five candidates.

A bounded [Euler-grid follow-up](../configs/euler_schedule_protocol.json), fixed before submission, compares uniform25/20 controls, uniform22, and20 intervals with powers0.75/1.25. Powers less/greater than one concentrate intervals late/early, respectively; neither direction is assumed better. The original weights, sample seeds, precision and all quality gates remain unchanged. Existing Euler20/25 predictions must reproduce. If a candidate qualifies, take the cheapest to the existing ensemble gate and then matched resident latency; if none qualifies, stop this grid search. This follow-up investigates the small observed uniform20 deficit rather than retrying the failed midpoint method. CPU tests check nonuniform interval widths and evaluation times; default Euler output and the entire previous-screen report remain identical.

The first solver screen uses32.03GiB peak reserved memory and70.54% SM issue in measured model ranges, but46.66% across the full467-second capture, below the whole-run50% target. Model ranges account for302.81seconds; the run manifest covers409.19seconds after the original checkpoint hash. A CPU export removes optimizer/non-EMA content, reducing checkpoint bytes from7,426,892,649 to1,856,643,912. All469 EMA tensors compare bit-for-bit with the source. The export hash is37c911faff08a10a48ae088877ca62af7582eb0fd92ca12e9b9bbb203addbad2; the original source hash is retained. Future screen GPU nodes hash the smaller exact-weight artifact, while output-reproduction controls remain mandatory. This targets allocation overhead rather than inflating useful work to improve a utilization percentage. Its measured benefit remains to be determined.

Euler-grid follow-up submitted as49734171 from1668ed6, one H200 with a15-minute walltime; three project GPUs running-plus-pending at submission. The exact-weight compact checkpoint remains an excluded local data artifact.

## Balanced500 capacity result

Both balanced arms [pass the original capacity screen](overfit_balanced_comparison_500.md) at the predeclared500-update checkpoint. CFG1 aligned recall0.89881 exceeds initialization by0.15134[0.06696,0.23467] and empirical same-frame training by0.21949[0.14420,0.29525]. PCA recall0.87589 exceeds initialization by0.12842[0.02009,0.23230]. Coarse validity is0.99609 aligned and0.99902 PCA; strict1A recall rises to0.81443 and0.77753. Aligned minus PCA remains unresolved:0.02292[-0.03958,0.08646]. The changed teacher prior is the supported intervention here; frame choice has no demonstrated advantage. Empirical-prior TV worsens relative to empirical training, as expected when intentionally shifting mass toward rare states; these frequencies are not physical populations. Both runs continue to2000.

Next, evaluate all four matched500-update teacher checkpoints on the existing64 tuning families at CFG1/2 alongside the original model. This checks accuracy outside the32 training proteins before deciding how to expand the recipe; small-panel capacity alone is not generalization or promotion. Preserve all arms and both guidance settings. The user clarified that50% utilization is a goal, not a gate;47% is acceptable. Scientific usefulness per GPU-hour takes priority over a utilization percentage.

The [accuracy-transfer protocol](../configs/overfit_native_protocol.json) and code are prepared for all four500-update checkpoints plus original weights, both guidance settings and all192 samples per condition. CPU preparation verifies no family overlap between the32 training proteins and64 tuning families, freezes training-manifest snapshots and hashes all four checkpoint files. One GPU shares a resident decoder and embedding cache across all five heads; no optimization is executed. Tests cover identity comparisons, accuracy loss, missing/duplicate samples, failed batch controls and the exact2/192 validity loss that must fail the0.01 margin. The existing watcher has a registered completion summary for this experiment.

Accuracy-transfer job49736749 was submitted from811a35b, one H200 with a20-minute walltime and registered completion analysis. Four project GPUs are running-plus-pending at submission. No new full training has been launched before these transfer results and final balanced comparisons.

## Broader training-data preparation without another GPU audit

Reapplying the original metadata rule exactly reproduces all32 selected records and yields122 eligible families:5/70/25/22 in the128/256/384/512 buckets. The additional90 comprise61/16/13 medium-to-long proteins; no new short proteins meet the rule. No student score determines inclusion. The inventory is an excluded local data artifact.

The unchanged aligned-label audit covers all122. Its two reconstruction failures give a conservative balanced-prior validity lower bound0.995219 when failures are assigned to the highest-weight valid labels. Per-protein minimum CA-lDDT bounds the weighted cohort mean at0.999375. Bounds also reach at least0.99 validity in every bucket. Thus the existing reconstruction margins hold without repeating a GPU audit. The [certificate](reliable122_reconstruction_bounds.md) checks original32 identity, audited-array provenance, family uniqueness, state mappings and historical metric controls; tests enumerate all failure placements to establish that the bound is exact for the available count information. This applies to the unchanged aligned labels and historical decoder/noise configuration, not PCA labels or arbitrary future decoder seeds.

The cohort imbalance changes how a larger experiment should sample proteins. Uniform bucket cycling would give each of the5 short proteins14 times the expected mean-loss weight of each of the70 medium proteins before gradient clipping. Future matched training should draw buckets in proportion to their target counts, preserving equal expected protein weight in a protein-averaged loss. That sampling change must be shared by empirical and balanced arms and recorded explicitly; it is not a modification to the running32-protein comparisons. Expansion remains contingent on the pending accuracy-transfer results.

## Euler-grid result and ensemble follow-up

Job49734171 completes960 samples and20 batching controls with the compact exact-weight checkpoint. Original Euler20/25 predictions reproduce the prior screen. [Uniform Euler22 qualifies](midpoint_49734171.md): CA-lDDT delta-0.000416[-0.002056,0.001270] and validity delta-0.005208. The20-step late-dense grid passes accuracy but again loses2/192 valid samples; the early-dense grid fails both margins. No threshold is relaxed. The fixed cost-first rule selects uniform22, with44 network forwards versus50 at baseline. This is a nominal12% reduction in head forwards, not an end-to-end speed claim.

The existing48-family ensemble test is the next gate for Euler22, using original weights, CFG2, original evaluation seeds, all three noise-source arms and the unchanged geometry/reference-quality/coverage criteria. If it fails, no latency promotion follows; if it passes, run matched resident sequence-to-backbone timing including ESMC and decoder. This sampling experiment is separate from the balanced fine-tuning checkpoints. Their combination would need its own validation.


Euler22 ensemble job49740635 was submitted from0907860 with one H200 and a20-minute cap. Its completion watcher includes CPU reference-state scoring. The job is queued; the two balanced training runs remain active.

## Separate tuning transfer at500 updates

Job49736749 completes1920 scores and40 controls in10:34. The [full transfer report](overfit_native_49736749.md) retains all ten head/guidance settings. Aligned balanced CFG1 improves CA-lDDT over original CFG2 by0.010428, family95% interval[0.005422,0.015180], while validity decreases by1/192=0.005208, within the unchanged0.01 margin. It passes both prior training capacity and this separate tuning screen. Balanced minus empirical within aligned CFG1 improves CA-lDDT by0.006810[0.001345,0.014101]. PCA empirical CFG1 also passes transfer but failed training-capacity improvement; PCA balanced CFG1 fails the validity margin. These unadjusted development intervals do not establish independent-test performance.

Advance aligned balanced500 CFG1 to the48-family ensemble assessment, preserving Euler25, FP32, decoder3, cached conditioning and paired seeds. Do not combine it with Euler22 before validating that combination. The preparer reanalyzes transfer scores, checks capacity eligibility, hashes the frozen checkpoint/training evidence and verifies no training-family overlap with this development panel. The new batch script uses one H10080GB with a30-minute cap: the prior same-shape ensemble measured43.39GiB peak reserved, leaving substantial headroom. Batching quality controls remain mandatory. Comparisons of speed require matched hardware.

The user authorized smaller jobs on RTX or H100. The eight-GPU cap applies across GPU types. Local Slurm exposes H10080GB and RTX PRO6000 Blackwell partitions to the existing account. H100 uses the already exercised Hopper architecture; RTX needs a bounded compatibility and numerical-control check before substantial work. The latest transfer capture measured59.34% whole-capture SM issue and71.17% within model ranges; these counters are not FLOP efficiency, and50% remains a target rather than a gate.

Balanced aligned500 ensemble job49742947 was submitted from5ff951d to H100,30-minute cap, with completion summary and automatic CPU state scoring. Four project GPUs running-plus-pending at submission.

A bounded RTX compatibility job will replay only original Euler25 CFG2 on the existing64 tuning proteins. The installed PyTorch2.11/CUDA13.0 build includes sm_120. This tests the real32GiB inference workload and checks all192 per-sample CA-lDDT/validity values against H200 at the existing1e-6 tolerance. No architecture, precision or quality threshold changes. It validates this inference path only, with a10-minute cap.


RTX strict-identity job49743331 runs successfully on RTX PRO6000 Blackwell96GB but fails its1e-6 score gate at sample41. The first mismatch is CA-lDDT+0.000344 with identical coarse validity. All42 saved matched structures have pair CA-lDDT1.0 and maximum CA-RMSD0.031352A; maximum unaligned coordinate difference is0.133022A. This was a61.5-second model run, not a full-panel compatibility pass. Preserve the failure. A separate full192-sample follow-up uses the existing0.2A/0.99 structural agreement limits and existing reference-quality margins(-0.005 CA-lDDT family lower bound,-0.01 validity delta) against frozen H200 outputs. It keeps every prediction and reports cross-hardware results separately; exact score identity is not claimed. The new protocol is fixed before rerunning, after observing this limited failure. Tests require both geometry and reference-quality agreement and complete paired coverage.

CPU array comparison confirms that all32 original capacity proteins have bit-identical reference backbone, cached reference latent, teacher backbone and aligned teacher latent in the expansion source shards. Expansion can reuse these labels without another encoding/copy step; inclusion remains metadata-based.

RTX full-panel structural/quality comparison submitted as49744818 from09c8d19, one GPU and10-minute cap; five project GPUs running-plus-pending at submission.

Exploratory length breakdown of balanced aligned500 CFG1 transfer versus original CFG2 gives CA-lDDT differences+0.00956/+0.01141/+0.01294/+0.00782 for128/256/384/512 buckets,16 families each. The single net additional invalid sample occurs in the shortest bucket; all other buckets have unchanged validity. These post hoc subgroups do not change selection or thresholds; the short-bucket uncertainty interval crosses zero, and no subgroup improvement claim is used to promote the model.
