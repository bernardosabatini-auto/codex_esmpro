# Weights versus integration steps in unconditional generation

All16 development families/four seeds and all failures retained. Original50/reflow10 plus complementary original10/reflow50. Identical source encodings, noises, decoder and numerical controls. No designability qualification.

| Head | Mode | CA-only valid | Full coarse valid | CA-valid peptide failures /64 |
|---|---|---:|---:|---:|
| original50 | unconditional | 1.0000 | 1.0000 | 0 |
| original50 | motif_u1 | 0.1094 | 0.1094 | 0 |
| original50 | motif_u3 | 0.6875 | 0.6719 | 1 |
| reflow10 | unconditional | 0.7500 | 0.7188 | 2 |
| reflow10 | motif_u1 | 0.1250 | 0.0938 | 2 |
| reflow10 | motif_u3 | 0.3125 | 0.2344 | 5 |
| original10 | unconditional | 0.6250 | 0.2969 | 21 |
| original10 | motif_u1 | 0.1562 | 0.0625 | 6 |
| original10 | motif_u3 | 0.3750 | 0.2031 | 11 |
| reflow50 | unconditional | 0.9844 | 0.9844 | 0 |
| reflow50 | motif_u1 | 0.0781 | 0.0781 | 0 |
| reflow50 | motif_u3 | 0.5469 | 0.5156 | 2 |

Paired-family differences and95% intervals:
- unconditional, original10 minus original50, coarse_valid: -0.7031 [-0.8125, -0.59375].
- unconditional, reflow10 minus reflow50, coarse_valid: -0.2656 [-0.4375, -0.109375].
- unconditional, reflow50 minus original50, coarse_valid: -0.0156 [-0.046875, 0.0].
- unconditional, reflow10 minus original10, coarse_valid: +0.4219 [0.21875, 0.609375].
- motif_u1, original10 minus original50, coarse_valid: -0.0469 [-0.15625, 0.078125].
- motif_u1, original10 minus original50, motif_drms: +0.4677 [0.37025889250217003, 0.566155072231777].
- motif_u1, original10 minus original50, motif_under1A: -0.5625 [-0.703125, -0.40625].
- motif_u1, reflow10 minus reflow50, coarse_valid: +0.0156 [-0.078125, 0.109375].
- motif_u1, reflow10 minus reflow50, motif_drms: +0.6171 [0.502467607066501, 0.7219968345831148].
- motif_u1, reflow10 minus reflow50, motif_under1A: -0.7031 [-0.859375, -0.515625].
- motif_u1, reflow50 minus original50, coarse_valid: -0.0312 [-0.09375, 0.03125].
- motif_u1, reflow50 minus original50, motif_drms: +0.0190 [-0.008352428319631145, 0.045574949262663644].
- motif_u1, reflow50 minus original50, motif_under1A: -0.0156 [-0.046875, 0.0].
- motif_u1, reflow10 minus original10, coarse_valid: +0.0312 [-0.03125, 0.109375].
- motif_u1, reflow10 minus original10, motif_drms: +0.1684 [0.14245746630476788, 0.1947967224521562].
- motif_u1, reflow10 minus original10, motif_under1A: -0.1562 [-0.25, -0.078125].
- motif_u3, original10 minus original50, coarse_valid: -0.4688 [-0.65625, -0.265625].
- motif_u3, original10 minus original50, motif_drms: +0.6127 [0.5134522879205179, 0.7039617631875441].
- motif_u3, original10 minus original50, motif_under1A: -0.4375 [-0.5625, -0.3125].
- motif_u3, reflow10 minus reflow50, coarse_valid: -0.2812 [-0.40625, -0.15625].
- motif_u3, reflow10 minus reflow50, motif_drms: +0.6528 [0.5206916456285399, 0.7733358267927543].
- motif_u3, reflow10 minus reflow50, motif_under1A: -0.4688 [-0.609375, -0.328125].
- motif_u3, reflow50 minus original50, coarse_valid: -0.1562 [-0.28125, -0.03125].
- motif_u3, reflow50 minus original50, motif_drms: +0.0611 [0.013538623915519566, 0.12830094043165438].
- motif_u3, reflow50 minus original50, motif_under1A: -0.0312 [-0.09375, 0.0].
- motif_u3, reflow10 minus original10, coarse_valid: +0.0312 [-0.09375, 0.171875].
- motif_u3, reflow10 minus original10, motif_drms: +0.1011 [0.03906810636399314, 0.16066506723873278].
- motif_u3, reflow10 minus original10, motif_under1A: -0.0625 [-0.203125, 0.078125].

CA-only validity omits peptide C-N distances and is not a substitute for the unchanged full-backbone validity gate. Geometry remains insufficient for designability. The conditional reflow training used zero condition dropout; this experiment tests its unconditional behavior explicitly.
