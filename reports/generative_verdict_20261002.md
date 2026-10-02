# Generative capability: what survives a stricter assay

Reliable isolated-fragment scaffolding remains unsolved. A supplemental screen found one strict same-refold success among 64 guided samples on one short protein, but the fresh-noise replication gave 0/16 at both guidance settings despite a passing native control. Every fixed eight-backbone assay still has zero strict successes. Global designability and raw motif fit can improve separately without satisfying the joint criterion. Direct atom inputs did not improve retention or designability. Fixed3×latent motif weighting improved raw retention to2/64, but both matches lost their motifs after refolding:0/64strict successes. These are development experiments; locked tests remain unscored.

## Contact guidance through initial noise

The original50-step flow and frozen decoder pass forward identity, directional finite differences and checkpointed/direct gradient controls. Eight fixed cases compare up to12normalized-gradient updates against the best contact match among33random candidates, using only the supplied contact objective for selection. Every generated failure is retained.

| Method | Contact within1A | Full-backbone valid | Best8designable | Generated joint success | Joint success also retained after refolding | Generation/search seconds |
|---|---:|---:|---:|---:|---:|---:|
| Initial single sample | 0/8 | 8/8 | 6/8 | 0/8 | 0/8 | 3.49 |
| Noise guidance | 5/8 | 8/8 | 6/8 | 4/8 | 2/8 | 168.06 |
| Random candidate selection | 3/8 | 8/8 | 6/8 | 3/8 | 3/8 | 41.27 |

Guidance is numerically valid but does not earn its cost for this contact task. The matching6/8designability counts are too small to prove no regression. Generation timing excludes model loading, numerical controls and designability assays; no end-to-end speed claim. Peak reserved GPU memory was8.34GiB. See [generation](noise_guidance_49863415.md), [224refold assay](noise_designability_49863726.md) and [constraint retention](refold_constraint_retention_20261002.md).

## Isolated fragments expose a real limitation

The earlier motif codes came from complete structures. We instead cropped each motif first, canonicalized using only that fragment and encoded it as a standalone chain. Same original50step/RePaint3recipe,16families/four paired seeds, unchanged noise streams; all controls passed.

| Motif code source | Motif dRMS | Motif within1A | Full-backbone valid |
|---|---:|---:|---:|
| Complete native structure | .390A | 64/64 | 43/64 |
| Isolated fragment | .417A | 64/64 | 26/64 |

Validity drops26.6percentage points; paired-family95%interval[-42.2,-12.5]. This comparison changes context, frame and encoder positions together; it cannot attribute the loss to one of them. Standalone fragment roundtrips average.124A distance RMS, so failure is not simply inability to reconstruct the supplied fragment. All57nonlocal CA clash pairs in isolated outputs involve motif–scaffold contacts;39of68CA gaps are at motif boundaries. See [generation](isolated_motif_49864561.md) and [failure localization](fragment_failure_diagnostic_20261002.md).

On the fixed four-family/two-seed ProteinMPNN panel, free sequence design gives3/8joint successes for full-context codes and2/8for isolated codes. Requiring the SAME designed sequence to refold with acceptable global agreement, valid geometry and motif dRMS<=1A reduces both to0/8. A global scTM>.5does not establish local motif preservation. See [160refold assay](fragment_designability_49865077.md).

## Fixing the motif sequence is necessary to test, but is insufficient here

We repeated the identical20backbone assay, fixing only the supplied motif amino acids in ProteinMPNN; all scaffold positions remained freely designed. All160refolds, fixed residues, positive controls and repeatability controls were audited.

| Motif code source | Strict joint, free sequence design | Strict joint, motif residues fixed |
|---|---:|---:|
| Full context | 0/8 | 2/8 |
| Isolated fragment | 0/8 | 0/8 |

This is a small feasibility result, not a population success rate or experimental validation. It strengthens the need to assess constraint retention after sequence design, and leaves the practical isolated-fragment task unsolved. See [matched fixed-sequence assay](fixed_motif_designability_49866072.md).

## Noise-space motif optimization also failed

None of264existing random candidates matched these isolated motifs within1A. A frozen eight-case experiment therefore starts from each case's best random candidate and optimizes initial noise through the original flow using a motif distance-matrix objective. It uses the same12update/line-search recipe, unchanged numerical controls and no motif-code insertion. Any follow-up must retain the fixed motif sequence and the strict same-sequence refolding gate. No outcome-driven parameter grid is authorized by this protocol.

The completed eight-case test passed every numerical check but reached0/8motifs within1A. Mean motif dRMS changed4.463→4.380A, with both starts and endpoints8/8coarse-valid. Accounting for initial random search, cost increased41.27→342.30seconds. The frozen recipe is closed without a designability follow-up or parameter grid. See [motif noise guidance](motif_noise_guidance_49867032.md).

## Refinement-history ablation also closed

The inherited refinement recipe retains one self-conditioning estimate across inner refinements. Refreshing it after every inner evaluation, with the same weights, noise, times, isolated-fragment codes and148velocity evaluations, did not help. Raw joint success changed26/64→24/64: difference−0.03125,95%family interval[−0.140625,0.09375]. All64motifs still met1A fidelity. This recipe failed its predeclared gate and received no designability follow-up. See [completed history ablation](motif_history_49868443.md).

## Pair-free unconditional generation is not materially faster in this profile

The corrected r4b pair-free checkpoint and original pair model both produce64/64coarse-valid backbones on the same16families/four noises. All128outputs and8CFG0/null controls pass; the64original outputs reproduce the historical archive. Generation-only times are11.06s versus10.78s, peak3.83/3.84GiB. The unconditional sampler already skips sequence-conditioned pair computation. Therefore the reported3.5xtraining-step benefit cannot be carried over to this path. These one-pass timings do not establish a small speed difference, and no pair-free designability assay has been run. See [corrected pair-free profile](pairfree_generation_49880198.md).


## Explicit isolated-fragment training: first completed comparison

The new open-ended generation campaign trained a zero-initialized fragment adapter on32existing training proteins with nine standalone fragments each. Inputs were only cropped fragment latents, supplied motif amino acids and placement; no scaffold sequence, ESM embedding or output-latent clamping. Adapter-only and full-network arms used identical initialization, data and random draws for2000updates. All2304saved predictions were audited.

Neither arm passed its prespecified capacity gate. Adapter-only had0/128training joint successes. Full-network had6/128with conditioning versus1/128with the fragment dropped: a3.9percentage-point difference with paired-family95%interval[0,8.6]. Both produced0/64development joint successes. Lower average motif error is not adequate constraint retention.

The subsequent fixed-motif ProteinMPNN/refolding assays each retained36backbones and288refolds. The same single refold had to match the scaffold globally, pass geometry and preserve the motif under both distance RMS and proper-rotation CA RMSD thresholds of1A.

| Conditioner | Valid globally agreeing refold, motif sequence fixed | Strict motif/global/geometry success |
|---|---:|---:|
| Token adapter only |2/8|0/8|
| Token adapter plus full network |4/8|0/8|

These are four-family development feasibility results. The difference in global designability is uncertain, and neither method solved motif scaffolding. Shared control sequences were identical; refolds differed slightly numerically (maximum CA RMSD0.00967A,lDDT1), within the established teacher repeatability tolerance, with the same control decisions. Experimental scaffolds gave4/4valid global refolds and3/4strict successes; fixing their motif amino acids in a separate32refold calibration still gave3/4strict successes, with a different failing family. Thresholds and failed cases were retained.

A direct intramotif-distance conditioner is being tested next. Its first run stopped at500updates on a numerical pose control. A frozen-checkpoint diagnostic reproduced the failure and separated FP32coordinate rounding from exact rotation: FP64distance calculation plus exact rigid transforms produced identical latents on all four controls, while rounding changed backbone CA RMSD by at most0.001166A without changing validity. The failed run remains failed. The corrected fresh2000update restart completed with all24exact-pose controls passing and all1152outputs audited. Development motif dRMS fell to3.195A from6.596Afor the token-only adapter; all64development samples remained coarse-valid. Nevertheless, joint motif success remained0/64development and0/128training. All2000training draw traces matched the token-only baseline. Direct distances improve conditioning substantially but do not yet enforce the requested fragment.

See [training comparison](fragment_training_comparison_2000.md), [paired refolding](trained_fragment_designability_comparison.md), [fixed native positives](fragment_fixed_positive_49906292.md), and [numerical diagnostic](fragment_geometry_pose_49908661.md).

## Decoded motif supervision and stronger guidance did not solve retention

The decoded-motif auxiliary run **49921479** completed 2,000 updates with matched training draws and passing numerical controls. It bounded the auxiliary adapter gradient to half the flow gradient norm. Mean development motif dRMS fell from **3.195 to 3.004 Å**, but joint counts remained **0/128 training and 0/64 development**. Its prespecified improvement gate failed. Its completed unchanged 288-refold assay gave 0/8 strict successes and 2/8 valid globally agreeing refolds, identical per-backbone decisions to the frozen distance baseline. The recipe is closed.

The distance-only model completed its own 288-refold assay: **0/8 strict successes and 2/8 valid globally agreeing refolds**, with the supplied motif residues fixed during sequence design. That is the same global designability count as the token-only adapter, with substantial uncertainty across four families.

A single CFG2 screen also failed: mean motif dRMS improved to **2.329 Å** from 3.195 Å at CFG1, but both produced **0/64 strict raw matches**. CFG2 took 1.90 times as long. All 128 outputs remained coarse-valid. No strength sweep follows. Allowing reflections during a diagnostic alignment did not recover any sub-1 Å fit, so handedness alone does not explain the failures.

The full-network distance-conditioner run **49929751** completed 2,000 updates. Strict raw retention reached 8/128 training samples across four families, versus 0/128 with conditioning dropped, but remained 0/64 on development proteins. Its matched designability assay gave **5/8 valid globally agreeing refolds and 0/8 strict successes**. The increase over token-plus-trunk training (4/8) is uncertain on four families.

A matched fresh-optimizer continuation to 4,000 cumulative updates (**49939857**) increased strict raw training retention to 20/128 versus 9/128 for its null branch. The null improvement warns of memorization. Development retention stayed 0/64 and mean motif dRMS worsened from 2.855 to 3.387 Å. The unchanged 288-refold assay (**49949949**) gave **3/8 valid globally agreeing refolds and 0/8 strict successes**. Compared with the parent, the global-success difference was −25 percentage points, descriptive four-family interval [−75,25]. More updates on these32proteins have not demonstrated useful transfer. See [matched refolding comparison](fragment_continued_designability_comparison_49949949.md).

## Designability optimization will use actual refold measurements

The completed feedback experiment **49941786** collected candidates from eight existing training families. A qualifying target must be one valid refold that simultaneously fits the fragment and globally agrees with the generated scaffold. Thresholds and minimum label yield are fixed in [the feedback protocol](../configs/fragment_feedback_protocol.json). Development and locked-test proteins were excluded from those labels. All eight native positive controls had valid globally agreeing refolds. Only **2/16 generated backbones across two families** yielded a qualifying target (one retained its motif, one was repaired during refolding), below the prespecified minimum8backbones/fourfamilies. Feedback training is closed for insufficient label yield; the two selected labels will not be used to justify training. A raw motif failure repaired by sequence refolding remains a failed retention sample; it can only become a separately identified training target.

An exploratory ProteinMPNN score diagnostic found no useful within-backbone sequence-ranking signal: mean Spearman correlation 0.010 across 24 generated backbones. Selecting the lowest global score produced **3/24** valid global refolds, versus **5/24** for the first sequence. This does not support likelihood-only training or a cheap designability selector. Results are exploratory and share four development families across three model arms.

## Data breadth improves transfer error, not yet strict retention

The matched 128-protein continuation **49951202** completed 2,000 updates with all primary noise/time/drop/history draws matched to the 32-protein control **49939857** and all 384 initial outputs identical. Evaluation remains the original 32 training and 16 development proteins.

Development motif dRMS fell from **3.387 to 1.962 Å** (paired-family difference −1.425 Å, descriptive interval [−1.735,−1.112]). Proper motif RMSD fell from 5.369 to 3.383 Å. All64development outputs were coarse-valid; nine passed the distance-only criterion, but **none passed strict proper-rotation retention**. The best proper fit was1.145Å, and allowing reflections recovered no additional sub-1Å matches. The final same-budget assay **49961674** yielded **4/8 valid globally agreeing refolds, 0/8 strict successes**, versus3/8global for the narrow control. That difference is uncertain across four families.

The new **512-protein** corpus adds384already-audited native references and preserves all128existing proteins and their inputs. The available short-chain pool is exhausted; additions are128each in256/384/512length buckets, while training bucket sampling stays fixed. The first data build **49978003** failed because an FP32 rigid-transform check perturbed coordinates. CPU diagnosis on all512references found exact FP64 transforms give bitwise-identical canonical coordinates, with old-versus-double coordinates differing by at most0.00004292Å. The correction changed only construction of the control; thresholds and supplied inputs stayed fixed. Corrected build **49981806** passed with4,608fragments, all512posecontrols, and94.33%ofnewfragment reconstructions within0.5Ådistance error. The failed build remains archived.

Profile **49984278** matched all40primary training draws at29.168GiB and22.82seconds. Training **49985054** completed the same2,000updates as128control49951202, from the same parent and fresh optimizer seed. Its fixed288-refold assay49993768 gave4/8validglobal and0strict, unchanged counts from128data; shared controls passed. Supplemental refolding49996435 of its lone strict raw match also failed, with the native fixed-motif control passing. Therefore all64screened512outputs fail strict same-refold retention. This does not expand or score the locked tests.

## Complete-generation motif loss does not earn its cost

The actual-rollout objective differentiates all50Euler steps and the frozen3-step decoder, then scores proper-rotation motif RMSD on generated samples. It preserves primary random draws, uses independent auxiliary noise, and caps the auxiliary gradient norm at half the primary gradient norm. CPU checkpoint/direct-gradient, finite-difference, mode and RNG checks passed; GPU forward controls matched exactly. Training costs roughly **nine times** plain flow matching.

The prospective500-update pilots use the first500updates of the same2,000-step schedule; comparisons below are against equally exposed plain controls, not their later checkpoints.

| Training corpus | Plain versus rollout development proper motif RMSD | Plain versus rollout strict raw development matches | Plain versus rollout valid globally agreeing refolds | Strict refold successes |
|---|---:|---:|---:|---:|
|32proteins|5.157 →4.881Å|0/64 →0/64|8/8 →4/8|0/8inboth|
|128proteins|3.921 →3.363Å|0/64 →0/64|3/8 →3/8|0/8inboth|

The32-protein designability difference is −50percentagepoints, descriptive four-family interval[−87.5,−12.5]; the128-protein difference is0[−37.5,37.5]. Allpositive and shared-refold controls passed. The small improvements in average motif fit do not establish successful conditioning and do not justify extending this expensive objective. Both rollout recipes are closed. See [32-protein comparison](fragment_rollout_designability_comparison_49976535.md) and [128-protein comparison](fragment_rollout_expanded_designability_comparison_49983356.md).

## Conditional target frame: an explicitly revised label-quality check

Original targets already use whole-protein PCA frames, while supplied fragments use their own standalone frames. Fragment-anchored targets place each complete native backbone into its supplied fragment's frame before encoding. Only labels change; full-target coordinates/codes never enter the conditioner. A24-condition training-only probe **49969994** reduced standalone-to-full motif latent mismatch by39.9%.

The full32-protein/288-condition label build **49972080** failed its original absolute gate:267/288valid reconstructions within0.5Åglobal proper CA RMSD, below95%. All288were coarse-valid, and alloriginal input arrays were preserved. The missing matched-baseline diagnostic **49976656** subsequently showed original cached labels also pass only267/288, with similar global and motif errors. This failure does not establish a degradation caused by anchoring; it remains recorded as a failed gate.

A **separate revised protocol**, specified before new measurements, compared both labels using three fresh decoder-noise seeds on the same32trainingproteins. It required upper95%family intervals for anchored-minus-original global and motif RMSD≤0.05Å, both arms≥99%coarsevalid and≥98%validmotiffits within1Å, and at most1percentagepoint loss in global-half-Å pass fraction. Confirmation **49979138** passed across864pairs: interval upper limits0.0014Åglobal and0.0060Åmotif; validity99.54%/99.65%and validmotiffits98.38%/98.84%(original/anchored). These are repeated noises on32families, not96independent proteins or an untouched validation set.

This distinct baseline-relative qualification permits an exploratory matched training test while retaining the original failed absolute gate. Profile **49983643** passed at29.168GiB and23.23seconds for40updates. All40primary draws matched plain control49937189; independently rebuilt hashes verified every conditioned, null and mixed label tensor. Dropped-fragment examples retain original null labels. The500-update test **49984633** completed: development propermotifRMSD5.157→2.183ÅanddRMS3.262→1.689Å, with1/64strict raw matches. Training validity fell126/128→114/128. Its unchanged288-refold assay **49987655** yielded4/8validglobal versus8/8forplain32atlocal500, with0strictinboth (descriptive difference−50pp,[−87.5,−12.5]). The lone strict raw sample also failed supplemental global refolding. The average-fit improvement does not establish successful scaffolding or justify adopting this frame change.

## Failed designability proxies and one fixed inference test

A reconstruction-consistency diagnostic **49967278** measured two autoencoder round trips for76existing backbones. All152cycles were audited and all12nativecontrols reconstructed below1Å. Among coarse-valid generated backbones, negative reconstruction error had pooled AUROC0.382on16trainingexamples and0.635on48developmentexamples; within-family AUROC was0.400/0.508. The prespecified signal screen failed. This proxy is closed without a sign reversal, score sweep, or optimization. ProteinMPNN likelihood likewise lacked useful within-backbone ranking signal, as recorded above.

The completed singleCFG2screen used the full-network128-protein model49951202. The earlier failed CFG2test used the frozen32-protein conditioner49911511; it remains closed. The new test uses the same16developmentfamilies, four noises and fixed1-versus2strength comparison, with historical CFG1 and null parity and exact-pose controls. It can proceed to the unchanged refolding assay only if at least one of the fixed eight assay samples passes strict raw retention, the strict-success difference is positive, and validity meets the existing bound. No strength sweep or deployable-success claim is planned.

## One rare strict success, with the full denominator retained

The singleCFG2screen **49986569** on the128-protein model produced2/64strict raw matches versus0/64atCFG1; validity63/64versus64/64. Both matches are on1BFY, outside the fixed eight-backbone panel, so the original fixed-panel follow-up gate **remains failed**. No strength sweep follows.

A separate, explicitly exploratory diagnostic **49989126** screened all64outputs for each of fourarms (plain32,frame32,plain128,guided128), refolded **every** strict raw match, and counted every rawfailure as a strictfailure. It evaluated threegeneratedbackbones plus their onecorrespondingnativecontrol with the same8sequence/refoldbudget and fixedmotifresidues. Nativecontrolpassed. Oneguided128sample passed allcriteria in the SAME refold; frame32andtheotherguidedcandidatefailed. The result is **1/64guided strict success ononefamily**, not1/2overall efficacy or an estimate ofglobaldesignability for skipped rawfailures. This concerns a16-residue fragment froma54-residueprotein; no broader generalization or experimental-function claim is justified. These development refolds never become training labels.

The512-protein trainingrun **49985054** completed2,000updates: developmentdRMS1.962→1.723ÅandproperRMSD3.383→2.818Åversus128data, with63/64validand1/64strict raw matches. Its fixed288-refold assay and complete-panel strict follow-up both finished without strict success. A separate controlled input-representation experiment will retain aminoacids/distances and originaltargetlabels butzero the eightstandaloneAEcodechannels, comparing from originalweights against49929751. This tests whether latentframe/context mismatch in conditioning is helping orhurting, without rotating outputtargets.

The fresh32-protein input ablation49996241 is running for2,000updates. A prospective one-case replication uses16fresh noises perCFG1/2arm on1BFY, with every strict raw match refolded and diversity measured among first-qualifying valid refolds. This selected-case test cannot establish generalization across proteins.

The input ablation49996241 completed2,000updates with allprimarydraws matched and384initialoutputs identical. It retained8/128strict training matches and0/64development matches. Development proper motif RMSD worsened4.868→5.728Å; all64were valid. Its mandatory matched refolding assay is being prepared.

Fresh-noise replication50008796 used the same predeclared16noise indices perarm on1BFY: CFG1gave3/16strict rawmatches,CFG2gave1/16; all32were valid. Historical, fresh-repeat and exact-pose controls were exact. The first attempt50004066failed batch16-versus4latent tolerance at0.000103235>0.0001; a separate recorded correction preserved the same noises and restored historical batch4, without relaxing thresholds. Allfourrawmatches plus nativefixed-motifcontrol will be refolded. These are selected-case stochastic results, not new-protein validation. All38fragment CPUtests passed; the three new screening tests cover denominator retention and dropped/changed samples.


## Replication and the next conditioning test

Fresh-noise refolding **50011710** completed all 40 refolds: four passing generated backbones and one native scaffold, eight designs each with the same motif residues fixed. The native strict control passed. Both ordinary and stronger guidance gave **0/16 strict successes** after retaining all raw failures in the denominator. The four generated backbones had best global scTM of 0.403, 0.341, 0.442 and 0.474, all below the required 0.5. The earlier rare success did not repeat in these samples; this selected-case experiment supports neither reliable scaffolding nor diversity among successful refolds. No further seed or guidance sweep follows.

The latent-input removal assay **50009556** gave **6/8 valid globally agreeing refolds and 0/8 strict successes**, versus 5/8 global and 0/8 strict for the matched baseline. Positive and shared controls passed. This small global difference is inconclusive; average fragment fit worsened and strict retention did not improve. The removal recipe is closed.

The next isolated-conditioning test retains the useful latent, sequence and distance inputs and adds the supplied fragment's N/CA/C/O coordinates directly. Only the stored isolated fragment enters the new token branch; scaffold inputs and full-target labels remain unchanged. Zero initialization preserves the original generator and shared adapter weights. Two CPU tests verified shared initialization, random-state preservation, unchanged existing inputs, absence of scaffold data, dropout and gradients. Profile **50013507** runs 40 updates on one RTX before any 2,000-update training. Its controls must match the original full-geometry profile. The prospective protocol is [direct backbone tokens](../configs/fragment_backbone_tokens_protocol.json).

The completion watcher now performs real registered-job polls every 30 seconds while CPU audits run. It does not fabricate freshness or inspect other agents' jobs. Nineteen watcher tests passed, including scheduler failure and exact job ownership. This removes submission delays caused by long CPU audits while preserving the existing GPU cap and monitoring requirement.

The direct-atom profile50013507 passed at29.170GiB and23.19training seconds with all40draws and32initial outputs matched; its2,000-update run is50014625. A second prospective test gives supplied-motif residues3×relative weight in the latent flow loss, normalized per protein, while dropped-condition examples keep uniform loss. It uses the matched128-protein continuation recipe and no decoder backpropagation. Analytical gradient/dropout, random-stream and weight1 parity tests passed. Profile50017255 passed at29.168GiB and22.86training seconds, with all40draws and32initial outputs identical to49947730. The measured39-minute allocation supports a2,000-update test against49951202, followed by the unchanged288-refold assay. No weight sweep is planned. See [the fixed weighting protocol](../configs/fragment_latent_weight_protocol.json).

Direct-atom conditioning **50014625** completed all2,000updates, matching allprimarydraws and384initial outputs to49929751. Strict raw training retention was6/128 versus8/128baseline; development remained0/64, with proper motif RMSD4.942 versus4.868Å and dRMS2.868 versus2.855Å. All64development outputs were coarse-valid. These results show no retention improvement from adding uncompressed supplied atoms. The mandatory fixed refolding assay is being prepared.

The fixed3×latent motif weighting run **50019364** completed2,000matched updates. Strict raw training matches increased4/128→12/128 across4→7families. Development improved0/64→2/64 across two families (1BFY slot2 and1CB9 slot0); mean proper motif RMSD3.383→2.703Å and dRMS1.962→1.641Å. Validity was63/64 versus64/64. This is a raw-retention signal, not yet designability. The unchanged288-refold assay is prepared. Any supplemental refolding will preserve eight designs per generated backbone, reusing the fixed assay for its1CB9case.

CPU assay preparation and reporting now avoid redundant post-hoc reads of teacher weights. Every GPU designability job still hashes all teacher artifacts and dependencies before creating its running manifest or loading models. CPU audits continue to verify source/output hashes, exact backbone/sequence coverage and recomputed geometry, motif and global scores. Recomputing the existing49961674baseline produced an exactly identical288-refold report. This changes audit placement, not model weights, data, metrics or success thresholds.

Direct-atom refolding **50025324** completed288refolds:5/8globally agreeing valid conditioned backbones and0/8strict successes, unchanged from49938555. Positive and shared controls passed; this direct-coordinate variant is closed.

The weighted-model fixed assay is50029204. Its supplemental complete-panel protocol reuses the fixed assay's exact eight1CB9slot0refolds and the existing matching fixed-motif native control. Only1BFYslot2anditsnativecontrol require16newrefolds. Combined scoring waits for audited source assays, recomputes reused scores, retains all64raw samples perarm and distinguishes reused from new refolds. This avoids silently doubling the design budget for the overlapping case. Four coverage tests and two original screening tests passed; the reused native control was independently rechecked.

The weighted fixed assay **50029204** gave5/8valid globally agreeing backbones versus4/8baseline, with0/8strict successes in both arms and passing positive/shared controls. The full64supplement **50030977** also gave0strict successes. Both raw matches refolded globally (bestTM0.630on1BFY and0.683on1CB9), but the best proper motif RMSDs were2.176Åand1.487Å. Both fixed-motif native controls passed. The1CB9distance-only metric would have incorrectly claimed success. The fixed loss-weighting test is complete; no weight sweep follows.

A separate prospective [three-round repair pilot](../configs/fragment_refinement_protocol.json) compares refold feedback through the trained conditioner against matched fresh sampling. It uses the two already selected failures, the same24designs percase perarm including eight reused initial designs, and same-valid-refold scoring. It is selected-case feasibility, not generalization or new training supervision.
