# Training-source confidence audit

Training-only, all sources accounted for. AFDB pLDDT is distinct from the original ESMFold teacher-confidence filter; neither establishes designability.

All7941 source sequences and CA coordinates matched the training corpus.

|Corpus|Length bucket|N|Median mean pLDDT|Mean pLDDT≥80|
|---|---|---:|---:|---:|
|original512|all|512|84.51|373|
|original512|128|24|88.70|24|
|original512|256|168|87.41|168|
|original512|384|160|81.63|90|
|original512|512|160|81.65|91|
|added7429|all|7429|84.29|5522|
|added7429|128|2021|87.89|2018|
|added7429|256|1858|86.64|1850|
|added7429|384|1796|79.39|840|
|added7429|512|1754|79.09|814|

The old set was selected using ESMFold teacher confidence; AFDB pLDDT is a different measure. Similar pooled means conceal small length-stratified shifts and do not establish equivalent designability.
