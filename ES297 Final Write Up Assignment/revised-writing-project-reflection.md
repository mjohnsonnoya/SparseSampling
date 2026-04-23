# Revised Writing Project Reflection

Running log of how we responded to peer review feedback on the sparse sampling paper. Organized by reviewer. Each item tracks: the suggestion → what we changed → where to find it in the revised draft.

---

## Process narrative (2-3 paragraphs)

_To be written after the revisions are complete. Will cover: how the writing process developed over the semester, what challenges came up, how peer review shaped the draft._

---

## Reviewer: Abigail Jiang (`reviews/Abby-review-for-Marcos.pdf`)

_Inline PDF annotations are in `reviews/Marcos Sparse_Sampling-4 AJ-1.pdf` — not yet catalogued below._

### Major comments

- [ ] **1. Placement of "Results" section V disrupts flow.** After the implications/limitations on p.4 the text feels like it should lead into the conclusion, but Results come next. Also unclear whether Figs 5 & 6 (SNR) reflect data before or after drift correction.
    - [ ] **1a.** Move Figs 5 & 6 (SNR) earlier in the text to introduce SNR as the figure of merit — or move to supplement if their purpose is just the SNR calculation method.
    - [ ] **1b.** SNR isn't mentioned on pp. 2–4 where sampling improvements are introduced. Add SNR references there so it's clear SNR improves with each iteration.

    **Response:** _(to be filled in)_
    **Location in revised draft:** _(to be filled in)_

- [ ] **2. Unclear which iteration is "our method" / "the best" reconstruction.**
    - [ ] **2a.** Add (or clearly label) a figure showing the combined drift correction + adaptive sampling result as the headline reconstruction. It wasn't obvious whether Fig. 1 is "the best" or just an initial try.
    - [ ] **2b.** Clarify in title/abstract/intro whether adaptive sampling is a key pillar of the method, or whether the pillars are just sparse sampling + drift correction.

    **Carry-over items to resolve in this pass** (deferred here from the #6 revision because they require the structural "what is our method?" decision that #2 addresses):
    - [ ] **Discussion § future-directions paragraph (lines 199–200 in pre-revision `main.tex`; line numbers will have shifted)** currently frames ASS as *future work* with different parameters than Methods demonstrates (5%/5% in Methods vs. 80%/20% here; topography-based in Methods vs. "bias-tested map" here). Decide whether this paragraph is proposing genuine future refinements, or whether it's just an outdated pre-Methods draft that needs to be cut or rewritten to match Methods.
    - [ ] In the same paragraph, the phrase **"resulting in high coherence"** uses "coherence" in a non-standard sense. Standard compressed-sensing coherence is the maximum inner product between the measurement basis and the sparsity basis (low is good for recovery). The paper's usage seems to mean "spatially concentrated / localized", which is misleading. Either replace with clearer wording ("spatially localized signals", "concentrated support") or drop the sentence.
    - [ ] Same paragraph still contains "scattering centers" (two occurrences) — left untouched during comment #6 revisions to avoid a half-measure inside a paragraph slated for restructure. Sweep these to "defects" per the `CLAUDE.md` writing convention once the paragraph structure is decided.

    **Response:** _(to be filled in)_
    **Location in revised draft:** _(to be filled in)_

- [ ] **3. Attach numerical SNR improvements to each iteration.** Text cites qualitative improvements in sharpness; quantify with SNR for drift correction, adaptive sampling, etc.

    **Response:** _(to be filled in)_
    **Location in revised draft:** _(to be filled in)_

### Minor comments

- [ ] **4. Material coverage is inconsistent.** Adaptive sampling shown only on Kondo insulator; drift correction only on BSCCO. Is there a reason, or should both appear on both?

    **Response:** _(to be filled in)_
    **Location in revised draft:** _(to be filled in)_

- [ ] **5. Motivate non-linear drift for non-STM audience.** Add concrete examples of non-linear drift situations to emphasize why the method matters beyond STM specialists.

    **Response:** _(to be filled in)_
    **Location in revised draft:** _(to be filled in)_

- [x] **6. Clarify adaptive-sampling targeting.** How is the selective map generated without a priori knowledge of interesting regions? Is it from the topography? What happens if drift moves those regions out of their expected positions?

    **Response:** Two-part clarification based on a chat exchange with my postdoc mentor Richard. (Part 1 — a priori source:) The adaptive mask *does* require a priori knowledge of feature locations, and that knowledge comes from an **initial** full-grid topography scan acquired before the adaptive dI/dV acquisition. We take the FT of that initial topo, select the Bragg peak and QPI feature regions in Fourier space, inverse-FT back to real space to recover the distribution of the lattice and defects, then build the Gaussian sampling mask from those real-space positions. This is separate from the *simultaneous* topography acquired during the sparse dI/dV scan, which serves drift correction — the paper previously conflated the two, which drove Abby's confusion. (Part 2 — drift robustness:) Because each Gaussian mask concentrates sampling over a finite real-space neighborhood rather than at a single pixel, the adaptive acquisition remains robust to small displacements of features between the initial and adaptive scans. Deliberately avoided a stronger Fourier-invariance argument (Fourier magnitudes are shift-invariant via the shift theorem) because that only applies to fully-sampled images, not to the sparse reconstruction.
    **Location in revised draft:**
    - `paper/main.tex`, Methods § Adaptive Sparse Sampling ("Implementation of Adaptive Sampling" paragraph): rewrote the pipeline sentence to name the initial topography scan and distinguish it from the simultaneous one; swapped "scattering centers (e.g., impurities)" → "defects" (two occurrences); inserted one-sentence drift-robustness clause.
    - `paper/main.tex`, Appendix § Adaptive Sparse Sampling → "ASS Strategy" paragraph: mirrored the initial-topography clarification; swapped "impurity-bound states or QPI peaks" → "Defects and QPI patterns".
    - `paper/main.tex`, figure caption for `figure_ASS_pipeline.pdf`: dropped the "stand-in for topography in this simulation" hedge, replaced with a clarification that the real protocol operates on the initial topography. Swept three panel-caption "impurity/scattering center" references to "defect".
    - `paper/main.tex`, § Compressed Sensing line 99: swapped "sparse in momentum space" → "sparse in Fourier space" per project-level writing convention.
    - `CLAUDE.md`: added a new "Writing conventions" section encoding the math/CS-vocabulary default and the two specific preferences (Fourier space, defects).
    - Overleaf commit: `4b9ec43` ("Clarify a priori source and drift robustness for ASS (peer review #6)").
    - **Deferred:** Discussion § future-directions paragraph (lines 199–200) still frames ASS as future work (conflicts with Methods demonstrating it) and uses "high coherence" in a non-standard sense. Both will be handled in the comment #2 revision pass.

- [x] **7. BPDN/LASSO is over-justified.** These are existing algorithms; repeated justification shifts weight away from our contribution. Move some BPDN/LASSO detail to the supplement, merge with the "Additional Metrics" text already written.

    **Response:** Demoted the BPDN-over-LASSO argument from main text to the appendix. The main text still names BPDN where it matters (abstract, intro, figure caption, methods, results) so a reader always knows which algorithm we used, but no longer argues *why* BPDN over BP/LASSO in the body. All comparative reasoning is now consolidated into a single appendix subsection — "Comparison of BPDN and LASSO Performance" — which absorbed the literature-gap framing from the old Discussion paragraph and the noise-robustness rationale from the old CS-section bracketed block. The Results section's three-sentence BPDN justification was compressed to one sentence with a pointer to the appendix.
    **Location in revised draft:**
    - `paper/main.tex`, outline paragraph (§ Introduction): dropped the "We also justify the choice of BPDN over LASSO" clause; now names BPDN once.
    - `paper/main.tex`, § Compressed Sensing: deleted the bracketed "Briefly Discuss Optimization Scheme" paragraph.
    - `paper/main.tex`, § Discussion: deleted the "What could be improved: algorithm comparison" paragraph; stripped the "our exploration of optimal algorithms" sentence from the Implications paragraph.
    - `paper/main.tex`, § Results: compressed three sentences of BPDN justification into one, with `\ref{sec:additional_metrics}` pointer to the appendix.
    - `paper/main.tex`, App. § Additional Metrics: expanded "Comparison of BPDN and LASSO Performance" into three paragraphs (literature framing → algorithmic rationale → empirical comparison); added `\label{sec:additional_metrics}`.
    - Overleaf commit: `700e4f9` ("Demote BPDN/LASSO justification to appendix (peer review #7)").
    - **Follow-up:** Added a verified citation (van den Berg & Friedlander, SIAM J. Sci. Comput. 31(2):890–912, 2008, DOI 10.1137/080714488) supporting the BPDN/LASSO equivalence claim in the appendix. The paper explicitly proves the three formulations (BP_σ, QP_λ, LS_τ) coincide for appropriate parameter choices but that the equivalent parameters cannot be known a priori — which supports both the "formal equivalence" and "requires more precise tuning" halves of the sentence. Added as `vanDenBergSIAM2008` to `paper/refs.bib`; cited in `paper/main.tex` App. § Additional Metrics. Overleaf commit: `11d22f1`.

- [ ] **8. Inline PDF annotations (typos, small suggestions).** In `Marcos Sparse_Sampling-4 AJ-1.pdf`. Not yet enumerated.

    **Response:** _(to be filled in — once PDF is read)_
    **Location in revised draft:** _(to be filled in)_

---

## Reviewer: (second reviewer)

_To be added when we process the second peer review._
