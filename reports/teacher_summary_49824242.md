# Frozen teacher ESM summary extraction

Status: complete; numerical/resource/overhead qualification: True.

One pretrained81-layer mixture, learned normalization and256-dimensional projection; no teacher folding trunk or diffusion. Existing final ESMC embedding retained. Nine controls include all8 fixed development sequences and a mixed-length batch. This does not establish predictive usefulness or justify long training.

Vanilla/streamed extraction means of3-repeat sequence medians: 0.11725/0.11979s; streamed/vanilla ratio1.02162, family95% interval[1.0200092888835581, 1.024012557740461].

Peak including full-state controls26.848GiB; loading64.89s; worker76.15s. Timings include tokenization and GPU work, exclude loading/reference controls/disk; GPU feature outputs remain resident.

mixed_length_batch2: summaryRMSE2.17581e-06,max1.71661e-05; finalembeddingmax0; padding/hooks True/True.

ood60__P50405__67632888e82e: summaryRMSE2.04085e-06,max1.33514e-05; finalembeddingmax0; padding/hooks True/True.

crypticpocket__P61586__aeabcc544d6c: summaryRMSE1.45376e-06,max9.53674e-06; finalembeddingmax0; padding/hooks True/True.

crypticpocket__P08037__b8cdcf0b572c: summaryRMSE1.75443e-06,max1.14441e-05; finalembeddingmax0; padding/hooks True/True.

crypticpocket__Q16658__6d919890c9e7: summaryRMSE1.5168e-06,max1.52588e-05; finalembeddingmax0; padding/hooks True/True.

md_emulation__cath1_3udcA02__0175a90823bb: summaryRMSE2.10389e-06,max1.33514e-05; finalembeddingmax0; padding/hooks True/True.

md_emulation__cath1_3luyA02__33e7c503c257: summaryRMSE2.24271e-06,max1.90735e-05; finalembeddingmax0; padding/hooks True/True.

nmr__1BFY_1__b91a89d44751: summaryRMSE2.12676e-06,max1.14441e-05; finalembeddingmax0; padding/hooks True/True.

nmr__1BM5_1__17d05a87e530: summaryRMSE1.50347e-06,max1.04904e-05; finalembeddingmax0; padding/hooks True/True.
