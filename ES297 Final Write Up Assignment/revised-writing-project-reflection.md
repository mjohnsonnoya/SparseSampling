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

- [ ] **4. Material coverage is inconsistent.** Adaptive sampling shown only on ~~Kondo insulator~~ **CeBi (Weyl semimetal)**; drift correction only on BSCCO. Is there a reason, or should both appear on both?

    **Pre-#4 correction (already committed):** Discovered during a fact-check of CeBi's classification that the paper had been calling the second material a "Kondo insulator" in three places, but the actual data is CeBi (a magnetic Weyl semimetal, per the Liu thesis title and confirmed by Jenny Hoffman over email). SmB₆ (the canonical topological Kondo insulator studied separately by Pirie 2020) was a stale placeholder backed by no actual data. Corrected in three places:
    - `paper/main.tex` line 87 (Outline): "a Kondo insulator" → "the magnetic Weyl semimetal CeBi"
    - line 168 (Fig. 3 caption): "Full-grid topography map of a Kondo insulator" → "Full-grid topography map of CeBi (a magnetic Weyl semimetal) \cite{LiuThesis2023}"
    - line 220 (SNR fig caption): "a Kondo insulator (SmB₆)" → "the magnetic Weyl semimetal CeBi"

    Overleaf commit: `3132678`.

    **Response (to #4 itself, still to be filled in):** _Now with corrected materials in mind: ASS demo uses CeBi, drift correction uses BSCCO. Structural question remains — should both demos appear on both materials?_
    **Location in revised draft:** _(to be filled in once #4 is addressed substantively)_

- [x] **5. Motivate non-linear drift for non-STM audience.** Add concrete examples of non-linear drift situations to emphasize why the method matters beyond STM specialists.

    **Response:** Added two concrete mechanisms to the Introduction paragraph that first motivates drift as a problem. (1) Piezoelectric relaxation: the piezos that position the tip continue to creep toward a steady state after the driving voltage has stabilized, at a speed that itself varies in time. (2) Millikelvin-scale temperature variations that cause mechanical parts of the instrument to deform slightly, shifting the tip relative to the sample. Both mechanisms accumulate over long acquisitions, making a constant-velocity (linear) model of drift a poor fit. Language is taken from `notebooks/Stmpy_102_dfc_tutorial_dev.ipynb` § "Piezo relaxation and thermal fluctuation" so the paper text matches how Marcos explains this to himself.

    Cited Lawler et al. Nature 466, 347–351 (2010) — the foundational Lawler–Fujita drift-correction paper, whose Supplementary § II names "piezoelectric mechanical creep and mK temperature variations" verbatim. Also cites Oppliger 2022 (already in bib; its SM demonstrates the linear-model failure). Dropped atmospheric pressure after searching Lawler SM, Hamidian 2012, the stmpy notebook, and web search without finding a cited STM-drift source for it. (Follow-up cleanup: initial draft used "scan tubes" from Marcos's notebook, but that term isn't in Lawler — replaced with "mechanical parts of the instrument" so the citation cleanly covers the whole sentence.)
    **Location in revised draft:**
    - `paper/main.tex`, § Introduction, paragraph following line 81 — four new sentences inserted after the existing "thermal drift… degrades the QPI signal" sentence.
    - `paper/refs.bib` — new `LawlerNature2010` BibTeX entry (also useful beyond comment #5 since it's the method paper this work builds on).
    - Overleaf commits: `b8ca789` (initial insertion) and `da1f0c8` (citation-scope fix replacing "scan tubes" with "mechanical parts of the instrument").

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

- [ ] **8. Inline PDF annotations (typos, small suggestions).** In `Marcos Sparse_Sampling-4 AJ-1.pdf`. Full raw extraction at `ES297 Final Write Up Assignment/abby-inline-annotations.md` (via `uvx pdfannots`). ~35 inline comments, triaged below.

    **Triage groups:**

    #### Typos & fixable-in-seconds (batch into one sweep commit) — **done, commit `fd9f62b`**
    - [x] **P1 Outline** — `"And"` orphan word: rewrote as *"We further show that adaptive sparse sampling outperforms uniform sampling under certain conditions…"*; preserved the inline TODO.
    - [x] **P2 Fig. 1 caption** — BSCCO formula subscripts: `CaCu$2$O${8+\delta}$` → `CaCu$_2$O$_{8+\delta}$`. (Same typo also fixed on P4 Discussion limitations paragraph — found via post-edit grep.)
    - [x] **P2 CS section** — `"sub nyquist"` → `"sub-Nyquist"`.
    - [x] **P3 Fig. 2 caption** — `"Reconstructe"`: **pdfannots false positive**; all three figure captions already have "Reconstructed" spelled correctly. No action.
    - [x] **P3 Methods** — `\(L_2\)` → `\(\ell_2\)` for consistency with `\(\ell_1\)` and `\(\ell_2\)` used elsewhere.
    - [x] **P4 (Discussion)** — stray closing `"` at end of the drift-correction-improvements paragraph: removed. (Note: pdfannots reported this under "Adaptive Sparse Sampling" but it was actually in the Discussion section.)
    - [x] **P5 Results** — `"we've"` → `"we have"`.
    - [x] **P5 SNR figure caption** — `"positions 0-30"` / `"positions 60-90"` → `"pixels 0-30"` / `"pixels 60-90"` (both occurrences).

    #### Language / tone
    - [x] **P1 Abstract** — removed the *"makes them good candidates for improving energy transmission."* application hook. Rewrote the first two sentences of the abstract as a single capability-first sentence that leads with QPI: *"Quasiparticle interference (QPI) imaging is a powerful probe of the electronic band structure of quantum materials such as cuprate superconductors and topological insulators."* Rationale: the abstract never returned to "energy transmission" so the hook was unearned; PRB readers don't need an applications bridge; the current opening also had a minor grammatical quirk (band *structures* as "candidates for improving energy transmission"). Overleaf commit `1906e3b`.
    - [x] **P3 Discussion** — `"adaptive sparse sampling"` → `"ASS"`: **rejected with justification.** The specific phrase *"an idea called adaptive sparse sampling"* would become *"an idea called ASS"*, which reads awkwardly — acronyms don't work naturally after *"an idea called"*. Making the swap naturally would require a sentence restructure for no real clarity gain, and the full name in a prior-art Discussion paragraph aids skimming readers. Cost of non-compliance is ~zero; cost of rewording is a sentence that reads worse. Applied the same reasoning to line 224 (Results) and did not swap.
    - [x] _(FYI, no action needed)_ **P3** — `"Adaptive sparse sampling (ASS)"`: Abby: *"brutal acronym lol… i really liked this paragraph though it was extremely clear"* — acknowledged; not changing the acronym.

    #### Citations needed — **done / deferred, commit `beb9aeb`**
    - [x] **P1 Intro** — `"compressed sensing (CS)"`: moved `\cite{CandesIEEE2006}` from the Nyquist-rate sentence to immediately after `(CS)` for explicit term attribution at first use. The Nyquist recovery math in the next sentence remains covered by `\cite{CandesCommPure2006}` at line 99.
    - [x] **P1 Intro** — `"BPDN"`: added `\cite{ChenDonohoSaundersSIAM1998}` (Chen, Donoho, Saunders, SIAM J. Sci. Comput. 20(1):33–61, 1998) at first BPDN use in the Intro outline paragraph. Verified via websearch; DOI 10.1137/S1064827596304010.
    - [x] **Appendix** — `"LASSO"` (note: Intro mention mooted by #7 revisions): added `\cite{Tibshirani1996}` (JRSS B 58(1):267–288) where LASSO is first introduced as a standalone algorithm in the "Comparison of BPDN and LASSO Performance" appendix paragraph. Deliberately placed at line 245 (algorithm comparison), NOT at line 243 alongside `NakanishiOhnoJPSJ2016` — co-locating would have misleadingly implied Tibshirani worked on STM/QPI.
    - [x] _(deferred)_ **P7** — `"[1]"`: too vague to act on without specific claims. Flag for final read-through pass or Jenny's review — identify specific unsourced claims then and decide which need sources.

    **Also in the same commit:** reordered `refs.bib` alphabetically by first-author last name per Hoffman lab guideline (captured in `CLAUDE.md` "Bibliography conventions" so future sessions default to insert-in-place rather than append).

    #### Figure formatting
    - [ ] **P2 Fig. 1** — panels c/d/g/h hard to read at single-column size: Abby asks if we can span 2 columns or rearrange panels for larger rendering.
    - [ ] **P2 Fig. 1** — scale bar placement (middle-right vs bottom-right): Abby flags as slightly distracting, notes it may be lab standard so feel free to ignore.
    - [ ] **P2 Fig. 1 caption** — `"(QPI) scattering wavevectors and Bragg peaks"`: Abby: *"could be useful to label which are bragg peaks and which are qpi signal in the fig?"*
    - [ ] **P3 Fig. 2** — color-bar sides inconsistent between figures; H/L labels on color bars: Abby asks for consistent side (left vs right) across figures, and suggests clarifying "H vs L = High vs Low" in the caption (or dropping the labels).
    - [ ] **P3 Fig. 2** — `"the QPI features appear sharper after correction."`: Abby: *"from my untrained eye, it's not immediately obvious which features i'm looking for that correspond to QPI… labeling with arrow/circle or two around representative features."*
    - [ ] **P5 SNR figure** — `"blue (noise floor) and red (signal)"`: Abby: *"can you make the colors match between panels a and b? i assume that the red area in both panels are supposed to refer to the same thing, but it looks orange in panel b so i got confused."*

    #### Clarity / prose — **done, commit `d4601c0`**
    - [x] **P1 Intro, ARPES comparison** — Replaced *"QPI advantageous over ARPES (works in B-fields)"* with the durable contrast: real-space resolution + occupied AND unoccupied states, framed as complementary. Dropped the `OppligerPRR2020` citation (claim is textbook-level, and Yu He et al. *Rev. Sci. Instrum.* 94, 093902 (2023), arXiv:2305.02625, has now made ARPES feasible in B-fields — invalidating the old hook). Avoided "momentum" per the Fourier-space convention; used "band structure" instead.
    - [x] **P1 Intro, ambiguous "We"** — Changed *"We can reconstruct the QPI signal"* to passive *"The QPI signal can be reconstructed"* to disambiguate from the later *"Here, we develop"* (which is unambiguously the Hoffman team).
    - [x] **P1 Outline, "the compressed sensing method"** — Dropped *"the…method"*. Compressed sensing is a framework, not a named method.
    - [x] **P2 Intro, "ℓ₂ constraint"** — Mooted by #7 revisions (the bracketed paragraph that mentioned `ℓ_2 constraint` was removed in commit `700e4f9`). Equation 1's `\|·\|_2` subscript is standard math notation. Appendix retains `\ell_2` where appropriate.
    - [x] **P2 Drift Correction, "before or after" → "before AND after"** — Corrected per Oppliger MethodsX 2022 §"Linear drift correction": the prior-art procedure does take topographies before AND after, fitting linear drift between them. The actual failure mode (linear interpolation can't capture nonlinear drift during the scan) is now named, citing `OppligerMethodsX2022`.
    - [x] **P2 Fig. 1 caption, undefined "BSCCO"** — Defined `(BSCCO)` on first use in the Fig. 1 caption; simplified the two later re-definitions (Discussion line 197 and SNR fig caption line 220) to plain `BSCCO`.
    - [x] **P2 CS section, ε definition** — Two-fer. Moved the ε-definition sentence earlier (after `y` definition, before `A` definition) per Abby's suggestion; AND clarified per Marcos that ε bounds the *real-space* residual (since `||Ax - y||_2` is computed on the real-space sampled pixels, not in Fourier space).
    - [x] **P3 Discussion, "traveling salesman problem"** — Added a parenthetical definition: *"the combinatorial optimization of finding the shortest route visiting a set of points"*. Used parentheses (no em dashes per new style preference). Attribution stays with `OppligerPRR2020` (TSP is their method, not ours).
    - [x] **P3 Fig. 2 caption, "Reconstructed" cross-reference** — Confirmed Fig. 2(a) and Fig. 1(c) are the same image. Added cross-reference: *"The reconstructed dI/dV map from Fig.~\ref{fig:SS_overview}(c), shown here prior to drift correction."* Dropped the redundant "$-22$ mV" since it's already in Fig. 1 caption.
    - [x] **P5 Results, "It may be possible…"** — Deleted the speculative sentence. ASS results are already shown in Fig. 3, so the hedge undersold the work. Full ASS-framing cleanup belongs to major #2.

    **Side products:**
    - New CLAUDE.md "Writing conventions" entry: **no em dashes** (use parentheses or semicolons instead). Backed by `feedback_no_em_dashes.md` memory.

    #### Structural (overlap with major comment #1)
    - [ ] **P4** — `"Pedagogical illustration of drift correction"`: Abby: *"seems like the drift correction figure would be better placed earlier as figure 3 and on the previous page if possible?"* (will be resolved during the #1 figure-reordering pass).
    - [ ] **P5 Results** — `"RESULTS"`: Abby: *"i was confused that the results showed up here after all the discussion about the limitations of your technique etc."* (this IS major comment #1; resolving that resolves this inline comment too).

    #### Already addressed by earlier revisions (verify during final read-through)
    - [x] **P1 Abstract** — `"tip drift scales linearly with time."`: asks for non-linear example. **Resolved by #5** (commit `da1f0c8`).
    - [x] **P1 Intro** — `"nonlinear."`: asks for non-linear example. **Resolved by #5** (commit `da1f0c8`).
    - [x] **P3 CS** — `"either by localizing key features in real space (e.g., near impurities) or by filtering in Fourier space around Bragg or QPI peaks"`: asks how priors are generated and how drift affects them. **Resolved by #6** (commit `4b9ec43`).
    - [x] **P4** — `"the literature could be improved,"`: asks what "the literature" means. **Partially resolved by #7** (BPDN/LASSO demotion, commit `700e4f9`); full paragraph restructure deferred to #2.
    - [x] **P6 Acknowledgements** — `"BPDN and LASSO"`: distracting in main text. **Resolved by #7** (demoted to appendix, commit `700e4f9`).
    - [x] **P3 (positive)** — `"The key point is that the full-grid topography map has the exact same tip movement history and pixel registration as the sparsely sampled map…"`: Abby: *"this sentence was super clear and helped clarify what you were explaining earlier"* — no action needed; preserve this wording in any future edits to that section.

    **Response:** _(to be filled in as items are addressed — expect a summary entry per commit)_
    **Location in revised draft:** _(to be filled in — Overleaf commits will accumulate as we work through the list)_

---

## Reviewer: (second reviewer)

_To be added when we process the second peer review._
