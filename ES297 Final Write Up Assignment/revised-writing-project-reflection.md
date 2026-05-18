# Revised Writing Project Reflection

**Made with assistance from Claude Code**

Responses to peer review feedback. Each entry: comment, response, location.

## Reviewer: Abigail Jiang (`reviews/Abby-review-for-Marcos.pdf`)

### Major comments

- [x] **1. Placement of "Results" section V disrupts flow.** Discussion appears before Results; Figs 5 & 6 (SNR) sit at the end.
    - [x] **1a.** Move Figs 5 & 6 earlier or to supplement.
    - [x] **1b.** Add SNR references on pp. 2–4 where sampling improvements are introduced.

    **Response:** Swapped Discussion ↔ Results (matching what the Outline already promised). Moved Fig. 5 (SNR illustration) to the appendix § *Additional Metrics*; Fig. 6 (SNR-vs-sparsity) stays in Results. Unbracketed an existing draft paragraph in the CS subsection that introduces SNR as the reconstruction-quality metric early in the paper.

    **Location:** `paper/main.tex` (CS subsection, Discussion, Results, Appendix Additional Metrics); commit `1b1c9c6`.

- [x] **2. Unclear which iteration is "our method" / "the best" reconstruction.**
    - [x] **2a.** Add or label a figure showing the "best" reconstruction.
    - [x] **2b.** Clarify in title/abstract/intro whether ASS is a key pillar or just an extension.

    **Response:** Picked the headline-pillars + extension framing: title and abstract feature sparse sampling + drift correction as the two pillars; ASS is named in the abstract once as a quality booster, given its own Methods/Results/Discussion treatment. The Intro was rewritten to correctly attribute the novelty to the *simultaneous acquisition protocol* (the drift-correction algorithm itself is Lawler–Fujita, not novel). Fig. 2 (BSCCO chain) is the headline result; ASS provides further gains demonstrated on CeBi.

    **Location:** `paper/main.tex` (Abstract, Intro, Methods § ASS, Results, Discussion); commit `894b3f9`.

- [x] **3. Attach numerical SNR improvements to each iteration.** Text cites qualitative improvements in sharpness; quantify with SNR for drift correction, adaptive sampling, etc.

    **Response:** Restructured the Results section to tell the cumulative-SNR story explicitly, one sentence per stage: BPDN alone (TBD%), BPDN + drift correction (75%), BPDN + drift correction + ASS (TBD%). Fixed a latent ambiguity in the Outline that previously phrased the 75% as if it referred to BPDN alone. Added a `\TBD` macro to the preamble that renders as a red `[TBD]` in the PDF so the two missing numbers are visually flagged. The two missing numbers (baseline BPDN-only on BSCCO; ASS-vs-uniform on CeBi) are deferred to notebook work and captured as a `% TODO` comment in source.

    **Location:** `paper/main.tex` (preamble, Outline, Results); commit `c79192c`.

### Minor comments

- [x] **4. Material coverage is inconsistent.** Adaptive sampling shown only on CeBi (a Weyl semimetal); drift correction only on BSCCO. Is there a reason, or should both appear on both?

    **Response:** Conceded the point. There is no fundamental reason for the asymmetry; both protocols can in principle be applied to either material. Rewrote the Discussion "Limitations: materials" paragraph to acknowledge the asymmetry and flag cross-application as future work. Concrete cross-application is deferred as a `% TODO` comment in source. (Also caught a separate misclassification mid-revision: the second material had been called a "Kondo insulator" in three places, but it's actually CeBi, a magnetic Weyl semimetal. Corrected.)

    **Location:** `paper/main.tex` (Outline, Fig. 3 caption, SNR fig caption, Discussion § Limitations); commits `3132678` (material correction) and `97090bf` (limitations paragraph).

- [x] **5. Motivate non-linear drift for non-STM audience.** Add concrete examples of non-linear drift situations to emphasize why the method matters beyond STM specialists.

    **Response:** Added two concrete mechanisms to the Introduction paragraph that first motivates drift as a problem: (1) piezoelectric relaxation (piezos continue to creep toward a steady state after the voltage has stabilized, at a speed that itself varies in time); (2) millikelvin-scale temperature variations that deform mechanical parts of the instrument. Cited Lawler et al. Nature 2010 (the foundational Lawler–Fujita paper, whose SM names "piezoelectric mechanical creep and mK temperature variations" verbatim), added to `refs.bib`.

    **Location:** `paper/main.tex` (Introduction); `paper/refs.bib` (new `LawlerNature2010`); commits `b8ca789` and `da1f0c8`.

- [x] **6. Clarify adaptive-sampling targeting.** How is the selective map generated without a priori knowledge? Is it from the topography? What if drift moves regions out of their expected positions?

    **Response:** Two-part clarification. (1) The adaptive mask *does* require a priori knowledge of feature locations, and that knowledge comes from an **initial** full-grid topography scan acquired before the adaptive dI/dV acquisition; the paper previously conflated this with the *simultaneous* topography used for drift correction. (2) Each Gaussian mask concentrates sampling over a finite real-space neighborhood rather than at a single pixel, so the adaptive acquisition remains robust to small drift-induced displacements. Methods, Appendix, and figure caption all rewritten to name the initial topography scan explicitly and distinguish it from the simultaneous one.

    **Location:** `paper/main.tex` (Methods § ASS, Appendix § ASS, Fig. ASS_pipeline caption, CS section); commit `4b9ec43`.

- [x] **7. BPDN/LASSO is over-justified.** These are existing algorithms; repeated justification shifts weight away from the contribution. Move detail to the supplement.

    **Response:** Demoted the BPDN-over-LASSO argument from main text to the appendix. The main text still names BPDN where it matters but no longer argues *why* BPDN over BP/LASSO in the body. All comparative reasoning is consolidated into a single appendix subsection ("Comparison of BPDN and LASSO Performance"). Also added a citation (van den Berg & Friedlander 2008) supporting the BPDN/LASSO equivalence claim in the appendix.

    **Location:** `paper/main.tex` (Outline, § CS, § Discussion, § Results, App. Additional Metrics); `paper/refs.bib` (new `vanDenBergSIAM2008`); commits `700e4f9` and `11d22f1`.

- [x] **8. Inline PDF annotations (typos, small suggestions).** ~35 inline comments in `Marcos Sparse_Sampling-4 AJ-1.pdf`, extracted via `uvx pdfannots` and triaged into seven buckets.

    **Response by bucket:**
    - **Typos:** 8 fixes in one sweep (BSCCO formula subscripts, "sub-Nyquist" capitalization, `\ell_2` notation consistency, "we have" replacing "we've", "pixels" replacing "positions" in the SNR figure caption, stray closing quote, orphan "And" word, etc.). Commit `fd9f62b`.
    - **Language / tone:** rewrote the abstract opening to drop the "energy transmission" application hook (commit `1906e3b`). Rejected with justification the "ASS" acronym swap in the Discussion paragraph "*an idea called adaptive sparse sampling*" — the substitution would read worse.
    - **Citations:** added `\cite{CandesIEEE2006}` at first CS mention, `\cite{ChenDonohoSaundersSIAM1998}` at first BPDN mention, `\cite{Tibshirani1996}` at first standalone LASSO mention in the appendix. Reordered `refs.bib` alphabetically. Commit `beb9aeb`.
    - **Figure formatting (six items):** captured as `% TODO (Marcos, Abby peer review)` comments in `paper/main.tex` co-located with figure environments (figure regeneration deferred to a separate pass). Commit `fe50cc9`.
    - **Clarity / prose (10 items):** ARPES comparison reframed (real-space resolution + occupied/unoccupied states; dropped magnetic-fields claim invalidated by Yu He et al. 2023). Disambiguated "We", dropped "the…method", clarified the "before AND after" prior-art critique citing Oppliger 2022, defined BSCCO on first use, moved ε definition earlier and clarified it bounds the real-space residual, defined TSP parenthetically, added Fig. 2 → Fig. 1(c) cross-reference, deleted a speculative sentence in Results. Commit `d4601c0`.
    - **Structural (2 items):** Discussion-before-Results placement and "Pedagogical illustration of drift correction" placement — both resolved by major comment #1 work.
    - **Already addressed by earlier revisions (6 items):** non-linear drift examples (#5), ASS targeting (#6), BPDN/LASSO over-justification (#7), one positive comment about a clear sentence (preserved as-is).

    **Location:** `paper/main.tex` (across all sections); `paper/refs.bib` (citation additions); commits as listed above. Detailed item-by-item triage in `ES297 Final Write Up Assignment/abby-inline-annotations.md`.

---

## Reviewer: Shicheng Qiu (`reviews/Shicheng Qiu-Review-for-Marcos.docx.pdf`)

### Major comments

- [x] **1. Strengthen the explanation of the drift correction method.** Shicheng asks for (a) a concrete description of how drift phase maps are obtained from topography, (b) a step-by-step description of how correction is applied, and (c) an explicit schematic.

    **Response:** Addressed via the visual route. The drift-correction algorithm is Lawler–Fujita and is described in detail in Lawler 2010 and Hamidian 2012; reproducing that level of detail in body text would be redundant. Instead, the paper now presents the algorithm visually through a 12-panel 1D walkthrough figure that already existed in the source but was orphaned at the end of the appendix and unreferenced from body text. Five actions: deleted the stale "[Figure in preparation]" placeholder; moved the 12-panel walkthrough into the Methods § Drift Correction subsection; updated the Outline reference; added a one-sentence body-text pointer with `\cite{LawlerNature2010, HamidianNJP2012}`; added Hamidian to `refs.bib`.

    **Location:** `paper/main.tex` (Outline, Methods § Drift Correction); `paper/refs.bib` (new `HamidianNJP2012`); commit `d6d27da`.

- [x] **2. Improve organization and flow.** Shicheng cited (a) Discussion before Results, (b) methodological explanations spread across sections, (c) repeated drift motivation. Asked for the standard Intro → Methods → Results → Discussion structure.

    **Response:** Discussion-before-Results swap (Shicheng's main concern) was already done as part of Abby comment #1 in commit `1b1c9c6`. The repeated drift motivation was tightened in commit `c79192c`. The deeper Methods-section restructure (empty `\subsection{Compressed Sensing Methods}` placeholder, "Main Text" vs "Methods" split) is deferred.

    **Location:** commits `1b1c9c6` (section swap), `c79192c` (Outline cleanup).

- [x] **3. Expand discussion of results and interpretation.** Shicheng asks: what does 75% SNR recovery imply practically? Under what conditions does the method perform best? How should one think about the sampling-rate vs accuracy trade-off?

    **Response:** Added three new `\ptitle`-labeled paragraphs to the Discussion section, one per sub-question. (1) *Practical significance of 75% SNR* anchored in QPI's motivation: scattering wavevectors and their dispersion remain resolvable while acquisition time drops from ~2.5 days to ~12 hours. (2) *Where the CS reconstruction performs best*: when the QPI signal is sparse in Fourier space and not dominated by noise. (3) *Sampling rate vs accuracy*: SNR generally rises monotonically with sampling rate; diminishing returns expected at high rates (anchored to the SNR-vs-sparsity figure; quantitative elbow position deferred to CeBi notebook work via TODO).

    **Location:** `paper/main.tex` (Discussion); commit `df7ea6b`.

### Minor comments

- [x] **1. Improve clarity and conciseness of writing.** Shicheng noted long sentences, sentence fragments, and some informal phrasing.

    **Response:** Many specific instances were caught via Abby's inline-annotation clarity sweep (`d4601c0`) and typo sweep (`fd9f62b`). Shicheng's comment is general (no specific sentences cited), so substantive items beyond Abby's flags require follow-up with him for specific examples.

    **Location:** Partial — see Abby commits `d4601c0` and `fd9f62b`.

- [x] **2. Strengthen figure integration.** Shicheng wants body text that more consistently guides the reader on what to notice in each figure.

    **Response:** This is the prose-side complement to Abby's figure-side TODOs. Deferred the prose updates with `% TODO (Marcos, Shicheng peer review)` comments above Fig. 2, Fig. 3, and Fig. 6 environments — pairing prose updates with figure regeneration prevents drift between the two. Rejected with justification a fourth TODO for Fig. 1 on show-don't-tell grounds: Fig. 1's four-panel layout (topography → sparse → reconstruction → ground truth) already does the comparison work visually.

    **Location:** `paper/main.tex` (TODOs above Fig. 2, Fig. 3, Fig. 6); commit `fea8603`.

- [x] **3. Use consistent terminology.** Shicheng flagged "drift phase map", "drift field", and "phase map" being used interchangeably.

    **Response:** Picked **"drift phase map"** as the canonical body-text term and swept all variants (five word substitutions across three edits). Intentional exception: the 1D pedagogical figure caption retains "drift field" because there `u(r)` is explicitly defined as a *displacement* function (units: nm), distinct from the *phase* `θ(r)` (units: radians) related by `u(r) = θ(r)/k`. Renaming `u(r)` would break the math.

    **Location:** `paper/main.tex` (Methods, Discussion); commit `dec6129`.

- [x] **4. Clarify the role of adaptive sampling.** Shicheng wants ASS framed as an extension or future direction.

    **Response:** Already resolved by Abby comment #2 work. The headline-pillars + extension framing is now consistent across abstract, intro, methods, results, and discussion; ASS is explicitly named as a quality-boosting extension on the core sparse-sampling + drift-correction protocol.

    **Location:** commit `894b3f9`.

### Overall evaluation

Shicheng's verdict was positive: *"This is a strong and thoughtful paper that addresses a meaningful problem in QPI measurements. The proposed approach is well motivated and shows promising results. With clearer organization, more detailed explanation of key methods, and stronger interpretation of results, the paper would be significantly improved."*
