# Revised Writing Project Reflection

Running log of how we responded to peer review feedback on the sparse sampling paper. Organized by reviewer. Each item tracks: the suggestion → what we changed → where to find it in the revised draft.

---

## Process narrative (2-3 paragraphs)

_To be written after the revisions are complete. Will cover: how the writing process developed over the semester, what challenges came up, how peer review shaped the draft._

---

## Reviewer: Abigail Jiang (`reviews/Abby-review-for-Marcos.pdf`)

### Major comments

- [x] **1. Placement of "Results" section V disrupts flow.** After the implications/limitations on p.4 the text feels like it should lead into the conclusion, but Results come next. Also unclear whether Figs 5 & 6 (SNR) reflect data before or after drift correction.
    - [x] **1a.** Moved Fig. 5 (SNR illustration) to the appendix § *Additional Metrics* where SNR computation is documented in detail; Fig. 6 (SNR-vs-sparsity, the actual quantitative result) stays in Results. Section reordering (1a's other half) handled below.
    - [x] **1b.** Unbracketed the SNR-introduction paragraph already drafted in the Compressed Sensing subsection at line 117. SNR is now introduced in Section II.A (well before Results) as one of two reconstruction-quality metrics, with a forward reference to the appendix figure.

    **Response:** Three edits in `paper/main.tex` (medium-tier per Marcos's choice):
    1. **Swapped Discussion ↔ Results sections.** New Section IV = Results, new Section V = Discussion. The Outline paragraph was already written for this order ("*In Section~IV, we show that combining BPDN reconstruction with our drift correction protocol recovers 75% SNR; In Section~V, we contextualize our contributions*"), so the swap aligned the paper with its own Outline. The fix was structural (block swap), not prose-level.
    2. **Moved Fig. 5 (SNR illustration) to appendix § *Additional Metrics*.** This figure is methodology-documenting (shows *how* SNR is computed) rather than result-presenting, so it lives more naturally in the appendix that already discusses SNR computation. The TODO comment about RGB color matching across panels (a) and (b) traveled with the figure.
    3. **Unbracketed the SNR-introduction paragraph in CS subsection** (line 117). The paragraph was already drafted with `[...]` markers; the brackets indicated draft uncertainty. Removing them turned the paragraph into body text that introduces SNR as our reconstruction-quality metric early in the paper.

    **Hidden insight:** the Outline's promised structure (II=theory, III=methods, IV=Results, V=Discussion) was already what Abby asked for — the paper's actual section ordering had drifted from the Outline somewhere along the way. The fix was largely mechanical because the Outline didn't need any rewording to match the post-swap structure.

    **Location in revised draft:**
    - `paper/main.tex` lines 117 (unbracketed SNR-intro paragraph in CS subsection).
    - `paper/main.tex` lines 194–232 (Results section now in former Discussion slot; Discussion now in former Results slot).
    - `paper/main.tex` lines 247–254 (Fig. 5 SNR_illustration moved into appendix § *Additional Metrics*).
    - Overleaf commit: `1b1c9c6`.

    **Out of scope (deliberate, deferred):**
    - Renaming `\section{Main Text}` → `\section{Theory}` (heavy-tier polish).
    - Cleaning up the empty `\subsection{Compressed Sensing Methods}` placeholder in Methods (heavy-tier polish).
    - Adding SNR mentions to Drift Correction and Adaptive Sparse Sampling subsections individually. The CS-subsection unbracketing introduces SNR globally; specific layered SNR claims live in Results (with `\TBD`s from comment #3 work).

- [x] **2. Unclear which iteration is "our method" / "the best" reconstruction.**
    - [x] **2a.** *(Folded into 2b's framing decision.)* The "best" reconstruction is established as Fig. 2 (BSCCO chain: sparse sampling + drift correction → 75% SNR), with ASS providing further gains demonstrated separately on CeBi. Fig. 2 caption already cross-references Fig. 1(c) per peer-review #8 clarity sweep.
    - [x] **2b.** Picked **framing (A): headline pillars + extension.** Title and abstract feature the two pillars (sparse sampling + drift correction); ASS is named in the abstract once as a quality booster, given its own Methods/Results/Discussion treatment, and explicitly described as a quality booster on top of the core protocol.

    **Crucial conceptual correction from Marcos:** The drift-correction *algorithm* is not novel — it's Lawler–Fujita (Lawler 2010, Hamidian 2012). What IS novel is the *simultaneous acquisition protocol* that records full-grid topography alongside the sparse dI/dV map, which makes Lawler–Fujita applicable to sparsely-sampled data (something Oppliger's linear-interpolation approach doesn't achieve). The Intro now correctly attributes the contribution.

    **Response:** Five edits in `paper/main.tex` that lock in the headline-pillars + extension framing:
    - **Intro line 84** rewritten: *"Here, we develop an acquisition protocol that simultaneously records a full-grid topography alongside the sparsely measured dI/dV map, enabling Lawler–Fujita drift correction \cite{LawlerNature2010} of the reconstructed sparse data. We further show that integrating adaptive sparse sampling \cite{OppligerMethodsX2022} with this protocol provides further gains in reconstruction quality."* This kills the previous conflation that called the contribution an "ASS approach that corrects for nonlinear drift" and correctly attributes the novelty to the simultaneous acquisition.
    - **Abstract** gained one ASS sentence near the end: *"Integrating adaptive sparse sampling with this protocol provides further gains in reconstruction quality."*
    - **Discussion future-directions paragraph** rewritten end-to-end. Old paragraph framed ASS as future work with implementation details duplicating Methods, and used "high coherence" in a non-standard sense + two "scattering centers" instances. New two-sentence paragraph: *"\ptitle{Adaptive sparse sampling and future ML extensions} Integrating adaptive sparse sampling further improves reconstruction quality compared to uniform sparse sampling (Sec.~II.C, Fig.~\ref{fig:ASS}). A natural future extension is to use machine learning to optimize the adaptive sampling distribution based on preliminary maps \cite{LiuThesis2023}."*
    - **Results section** gained a bridging sentence: *"Adaptive sparse sampling further improves reconstruction quality beyond uniform sparse sampling (Fig.~\ref{fig:ASS})."* + LaTeX TODO for the pending quantitative SNR.
    - **Fig. 3 caption** gained a parallel LaTeX TODO marker (no prose change).

    **Location in revised draft:**
    - `paper/main.tex`: Intro (line 84), Abstract, Discussion (the rewritten ASS/ML paragraph), Results paragraph (last sentence), Fig. 3 caption header.
    - Overleaf commit: `894b3f9`.

    **Carry-over items from #6 — now resolved:**
    - [x] **Discussion future-directions paragraph restructure** — resolved by the full rewrite above. Paragraph no longer frames ASS as future work; ML is now the only forward-looking element.
    - [x] **"high coherence" non-standard usage** — resolved by paragraph rewrite (the entire sentence using that term is gone).
    - [x] **"scattering centers" (two occurrences in this paragraph)** — resolved by paragraph rewrite. `rg -n 'scattering center' paper/main.tex` now returns zero hits.

    **Open hooks for comment #3 (numerical SNR per iteration):**
    - LaTeX `% TODO` comments at two locations in `paper/main.tex` (Fig. 3 caption header and Results paragraph) mark where the quantitative ASS-vs-uniform SNR will slot in once notebook work produces the numbers.
    - The framing now anticipates a cumulative-SNR story: *baseline sparse sampling → +drift correction (75% SNR) → +ASS (TBD additional gain)*. Comment #3 work will populate the numbers without further structural change.

- [x] **3. Attach numerical SNR improvements to each iteration.** Text cites qualitative improvements in sharpness; quantify with SNR for drift correction, adaptive sampling, etc.

    **Wave 1 (prose framework, commit `c79192c`):** Restructured Results section to tell the cumulative-SNR story explicitly, with one sentence per stage of the protocol:
    - *BPDN reconstruction alone, without drift correction, recovers \TBD% of the ground truth SNR at a 25% sampling rate on BSCCO.*
    - *Combining BPDN reconstruction with our drift correction protocol raises this to 75% (Fig.~\ref{fig:SNR_vs_Sparsity}).*
    - *Combining adaptive sparse sampling with the protocol provides a further \TBD% gain on the CeBi data set (Fig.~\ref{fig:ASS}).*

    Also fixed a latent ambiguity in the Outline (line 87) that previously phrased the 75% as if it referred to BPDN alone with drift correction adding more. Marcos confirmed: 75% is the combination (BPDN + Lawler–Fujita drift correction). The Outline now matches the Results.

    Added a `\TBD` macro to the preamble that renders as a red `[TBD]` in the PDF, so the two missing numbers are visually flagged at-a-glance in the rendered output (not just in source).

    **Wave 2 (deferred — notebook work):** Two numbers still to be computed and slotted into the `\TBD` placeholders:
    1. **Baseline BPDN-only SNR on BSCCO** without drift correction (same 25% sampling rate, same data as the existing 75% measurement).
    2. **ASS-vs-uniform SNR gain on CeBi** (paired comparison at the same sampling fraction).

    Both tasks are captured as a consolidated `% TODO (Marcos)` comment in `paper/main.tex` immediately following the cumulative-SNR paragraph, and as a `% TODO` comment above the Fig. 3 caption (legacy from commit `894b3f9`, now redundant with the Results-side TODO but kept for figure-side visibility).

    **Location in revised draft:**
    - `paper/main.tex` line 29: new `\TBD` macro.
    - `paper/main.tex` Outline (line 88): rewrote 75% attribution.
    - `paper/main.tex` Results (lines ~227–229): added cumulative-SNR paragraph with two `\TBD` placeholders + consolidated Wave 2 TODO comment.
    - Overleaf commit: `c79192c`.

### Minor comments

- [x] **4. Material coverage is inconsistent.** Adaptive sampling shown only on ~~Kondo insulator~~ **CeBi (Weyl semimetal)**; drift correction only on BSCCO. Is there a reason, or should both appear on both?

    **Pre-#4 correction (commit `3132678`):** Discovered during a fact-check that the paper had been calling the second material a "Kondo insulator" in three places, but the actual data is CeBi (a magnetic Weyl semimetal, per the Liu thesis title and confirmed by Jenny Hoffman over email). SmB₆ (the canonical Kondo insulator studied separately by Pirie 2020) was a stale placeholder backed by no actual data. Corrected line 87 (Outline), line 168 (Fig. 3 caption, with `\cite{LiuThesis2023}` added), and line 220 (SNR fig caption).

    **Response to #4 itself (commit `97090bf`):** Conceded the point. There is no fundamental reason that drift correction is on BSCCO and ASS is on CeBi; both protocols can in principle be applied to either material. Rewrote the Discussion "Limitations: materials" paragraph to acknowledge the asymmetry honestly and flag cross-application as future work, with possible supplemental-material extension. The previous paragraph claimed only "single material BSCCO", which was already inaccurate after the CeBi correction.

    Concrete cross-application work (drift correction on CeBi, ASS on BSCCO, and reporting the comparison) is **deferred as a TODO**, captured both in the reflection here and as a `% TODO (Marcos)` comment in `paper/main.tex` immediately above the rewritten paragraph.

    **Location in revised draft:**
    - `paper/main.tex`, Discussion § "Limitations of our research and directions for future research: materials" — paragraph rewritten end-to-end. LaTeX `% TODO` comment inserted on the line above the paragraph.
    - Overleaf commits: `3132678` (material correction) and `97090bf` (limitations paragraph rewrite).

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

    #### Figure formatting — **decisions captured, figure work deferred (commit `fe50cc9`)**

    All six items have been triaged and captured as `% TODO (Marcos, Abby peer review)` comments in `paper/main.tex` adjacent to the relevant figure environments. No figure-script / notebook work has been done; the rendered PDF is unchanged.

    - [x] **P2 Fig. 1** — panels c/d/g/h hard to read at single-column size. **Accepted.** TODO above Fig. 1: switch to `figure*` environment for two-column width.
    - [x] **P2 Fig. 1** — scale bar placement. **Accepted** (Marcos confirmed mid-right is not a Hoffman lab standard). TODO above Fig. 1: move scale bars to bottom-right of each panel.
    - [x] **P2 Fig. 1 caption** — label which features are Bragg vs QPI. **Accepted.** TODO above Fig. 1: add Bragg vs QPI annotation callouts (arrows/circles with labels) to FT panels (e), (g), (h).
    - [x] **P3 Fig. 2** — color-bar side consistency + H/L labels. **Accepted both sub-items** (applies across all figures). TODO above Fig. 2: standardize color-bar side and drop H/L letters (or define them in captions if kept).
    - [x] **P3 Fig. 2** — label QPI features. **Accepted as "ask-Jenny" TODO** (per Marcos's request). TODO above Fig. 2: ask Jenny about whether to add arrow/circle annotations highlighting QPI features and confirm Hoffman-lab convention for feature callouts before implementing.
    - [x] **P5 SNR figure** — blue/red color match between panels. **Accepted.** TODO above SNR illustration figure: use same RGB hex codes for blue (noise floor) and red (signal) across panels (a) and (b).

    All six TODOs reference "Abby peer review" by name (not by issue number) so future-Marcos can interpret them after the chat context fades.

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

## Reviewer: Shicheng Qiu (`reviews/Shicheng Qiu-Review-for-Marcos.docx.pdf`)

Shicheng's review focuses on three major axes: clarity of the drift correction method, overall paper organization, and depth of results interpretation. Many of his concerns overlap with Abby's review and are already addressed by the same revisions; some open issues remain.

### Major comments

- [x] **1. Strengthen the explanation of the drift correction method.** Shicheng asks for (a) a more concrete description of how drift phase maps are obtained from topography, (b) a clearer step-by-step description of how correction is applied, and (c) an explicit schematic / conceptual workflow figure.

    **Response:** Addressed via the **visual contribution route** rather than expanded body-text exposition. The Lawler–Fujita drift correction algorithm is described in detail in the foundational papers (Lawler 2010, Hamidian 2012); reproducing that level of detail in body text would be redundant. Instead, the paper now presents the algorithm visually through a 12-panel 1D walkthrough that already existed in the source (`fig:drift_correction_1d`) but was orphaned at the end of the appendix and unreferenced from body text. Five concrete actions (commit `d6d27da`):

    1. **Added `HamidianNJP2012`** to `paper/refs.bib` (Hamidian et al., New J. Phys. 14, 053017, 2012; DOI 10.1088/1367-2630/14/5/053017) so we can co-cite Lawler and Hamidian when introducing the algorithm.
    2. **Deleted the stale Fig. 4 placeholder** (`fig:drift_pedagogical`). Its caption was *"[Figure in preparation]"* and dated to before Marcos's PI-discussion-driven breakthrough on what the drift figure should actually show.
    3. **Moved the 12-panel 1D walkthrough figure** (`fig:drift_correction_1d`) from the end-of-appendix orphan position into the Methods § Drift Correction subsection, adjacent to the body text that introduces drift correction. The figure now has a strengthened caption title (`\textbf{Visual workflow of the Lawler–Fujita drift correction algorithm on a 1D toy example.}`).
    4. **Updated the Outline reference at line 88** from `\ref{fig:drift_pedagogical}` to `\ref{fig:drift_correction_1d}` so the Outline's promised drift-correction figure now points at the figure that actually exists.
    5. **Added a body-text sentence** in the Drift Correction subsection: *"We use the Lawler–Fujita drift correction algorithm \cite{LawlerNature2010, HamidianNJP2012}; the workflow is illustrated visually in Fig.~\ref{fig:drift_correction_1d} for a 1D toy example."* Single sentence; full step-by-step lives in the figure.

    **Hidden insight:** Shicheng's #1c (explicit schematic) was already 90% solved by an existing figure that wasn't being surfaced. The Fig. 4 / Fig. 8 split was a revision-time accumulation: an early placeholder (Fig. 4) survived in body-text references even after the more developed figure (Fig. 8) was added separately at the end of the appendix. Deleting Fig. 4 and surfacing Fig. 8 in its place addressed the comment without writing significant new prose.

    **Bonus cleanups during the move:**
    - Replaced two em dashes in the caption with commas (per `feedback_no_em_dashes` memory).
    - Added inline `\cite{HamidianNJP2012}` where the caption references *"Hamidian Eqs.~(1a)/(1b)"*.

    **Location in revised draft:**
    - `paper/main.tex` line 88 (Outline reference updated).
    - `paper/main.tex` line 124 (new body-text sentence in Drift Correction subsection).
    - `paper/main.tex` lines 126–131 (Fig. 8 moved into Methods § Drift Correction).
    - `paper/refs.bib` line 36 (new `HamidianNJP2012` entry).
    - Overleaf commit: `d6d27da`.

- [x] **2. Improve organization and flow.** Shicheng cited (a) Discussion before Results, (b) methodological explanations spread across multiple sections, (c) repeated drift motivation. Asked for the standard Intro → Methods → Results → Discussion structure.

    **Status (substantively addressed):** **already resolved by Abby comment #1 work** in commit `1b1c9c6`. The Discussion-before-Results swap explicitly addresses Shicheng's (a). The Outline cleanup during the cumulative-SNR framework work (commit `c79192c`) tightened the repeated drift motivation by removing one redundant clause.

    **Open sub-item:** Shicheng's (b) "methodological explanations spread across multiple sections" — this is the heavier "Main Text vs Methods" structural debt (an empty `\subsection{Compressed Sensing Methods}` placeholder, and the split between `\section{Main Text}` and `\section{Methods}`) — flagged as out-of-scope for this revision pass.

    **Response:** Section swap done; deeper Methods restructure deferred.
    **Location in revised draft:** Overleaf commits `1b1c9c6` (section swap), `c79192c` (Outline cleanup).

- [x] **3. Expand discussion of results and interpretation.** Shicheng asks: what does 75% SNR recovery imply in practical experimental terms? Under what conditions does the method perform best or struggle? How should one think about the trade-off between sampling rate and accuracy?

    **Response:** Added three new `\ptitle`-labeled paragraphs to the Discussion section, one per sub-question, between "How our data is different" and "Limitations: materials". Three-paragraph structure (rather than one combined paragraph) was chosen to match the Discussion's existing rhythm of focused topics and to give each TBD/TODO a clean home.

    1. **\ptitle{Practical significance of the 75% SNR recovery}.** Anchored in QPI's motivation (investigating electronic band structure): the QPI scattering wavevectors and their dispersion with bias remain resolvable at 75% SNR while acquisition time drops from approximately 2.5 days to 12 hours. Concrete claim, no TBD.
    2. **\ptitle{Where the compressed sensing reconstruction performs best}.** Scoped narrowly to the CS reconstruction step (per Marcos's request): best when QPI signal is sparse in Fourier space and not dominated by measurement noise. Concrete claim, no TBD.
    3. **\ptitle{Sampling rate vs reconstruction accuracy}.** Qualitative claim (SNR generally rises monotonically with sampling rate; diminishing returns expected at high rates) anchored to Fig.~\ref{fig:SNR_vs_Sparsity}. Quantitative claim about *where* the elbow occurs is deferred to future work with CeBi data via inline `% TODO (Marcos, Shicheng peer review)` comment. Marcos added "generally" to soften "rises monotonically" before commit.

    **Location in revised draft:**
    - `paper/main.tex` lines 223, 225, 227 (three new paragraphs); line 228 (Wave 2 TODO).
    - Overleaf commit: `df7ea6b`.

    **Open hook for Wave 2 (CeBi notebook work):**
    - LaTeX `% TODO (Marcos, Shicheng peer review)` at line 228 marks where the quantitative elbow position will slot in once the CeBi SNR-vs-sampling-rate data is computed. Hook integrates with the broader CeBi notebook TODOs from Abby comment #3.

### Minor comments

- [x] **1. Improve clarity and conciseness of writing.** Shicheng noted long sentences, sentence fragments, and some informal phrasing.

    **Status (addressed at editorial level; specifics need reviewer follow-up):** the Abby clarity/prose sweep (commit `d4601c0`) and typo sweep (`fd9f62b`) targeted many specific instances that were flagged via inline PDF annotations. Shicheng's comment is general — he doesn't cite specific sentences he found long, fragmentary, or informal — so it's hard to know which sentences he had in mind beyond the ones Abby already flagged.

    **Response:** Acknowledged. Plan to follow up with Shicheng directly to ask which sentences he had in mind. If he points to specific instances, those land in a focused copyedit pass; if his comment was general, the existing Abby-driven edits are the substantive response and any further tightening is captured under a general "copyedit before submission" TODO.

    **Location in revised draft:** Partial — see Abby commits `d4601c0` (clarity sweep) and `fd9f62b` (typo sweep). No new paper edits in this pass for Shicheng's comment.

    **Action item (Marcos):** ask Shicheng for specific sentences he found long, fragmentary, or informal so the comment can be addressed concretely if needed.

- [x] **2. Strengthen figure integration.** Shicheng wants body text that more consistently guides the reader on what to notice in each figure ("explicitly stating what improvement is visible in each panel").

    **Status (deferred with TODO breadcrumbs):** Abby's figure-formatting bucket (commit `fe50cc9`) handles the *figure-side* (annotation callouts, color-bar consistency, etc.). Shicheng's ask is *prose-side* — body text pointing readers at specific panels. We chose to defer the prose updates with TODO breadcrumbs rather than write the panel-pointing prose now, since the prose describes panels that may change when figures are regenerated. Pairing prose updates with figure regeneration prevents drift between the two.

    **Response:** Three new `% TODO (Marcos, Shicheng peer review)` comments added above figure environments where body-text pointing is missing:
    - Above Fig. 2 (`fig:Methodology`): extend the existing panel-(d) pointer ("Bragg peaks become sharper") to panels (a)-(c).
    - Above Fig. 3 (`fig:ASS`): add panel-pointing prose at body-text references for panels (a)-(f).
    - Above Fig. 6 (`fig:SNR_vs_Sparsity`): point readers at diminishing-returns regime once CeBi curves are added.

    **Rejected with justification: Fig. 1 panel-pointing TODO.** The original plan included a fourth TODO above Fig. 1 (`fig:SS_overview`) suggesting *"compare BPDN reconstruction in panel (c) against ground truth in panel (d)"*-style prose. **Rejected on show-don't-tell grounds:** Fig. 1's four-panel + four-FT-panel layout (topography → sparse → reconstruction → ground truth, with each FT below) already does the comparison work visually. Adding prose telling the reader to compare panels would tell rather than show what the figure layout already invites. The figure carries its own pedagogical structure; pointing prose would be redundant.

    **Location in revised draft:**
    - `paper/main.tex` lines 133, 172, 203 (three new TODOs).
    - Overleaf commit: `fea8603`.
    - The figure-side annotation TODOs (Abby commit `fe50cc9`) remain in place; the prose-side TODOs from this commit will land alongside the figure regeneration when that work happens.

- [x] **3. Use consistent terminology.** Shicheng flagged "drift phase map", "drift field", and "phase map" being used somewhat interchangeably.

    **Response:** Picked **"drift phase map"** as the canonical body-text term and swept all variants. Three edits in `paper/main.tex` (five word/phrase substitutions): line 141 `\ptitle` ("phase maps" → "drift phase maps"); line 142 ("drift maps" → "drift phase maps"); line 199 `\ptitle` + body ("drifting field" → "drift phase map" ×2, "phase maps" → "drift phase maps" ×1).

    **Intentional exception:** Fig. 4 caption (`fig:drift_pedagogical`, line 278) retains "drift field" because there `u(r)` is explicitly defined as a *displacement* function (units: nm), distinct from the *phase* `θ(r)` (units: radians) related by `u(r) = θ(r)/k`. Renaming `u(r)` would create equation/naming inconsistency with the explicit math. The body text uses "drift phase map" as the operational object; the figure caption uses "drift field" only where the math explicitly defines `u(r)` as a displacement function.

    **Location in revised draft:**
    - `paper/main.tex` lines 141, 142, 199 (three edits, all in body text).
    - `paper/main.tex` line 278 (Fig. 4 caption) intentionally untouched.
    - Overleaf commit: `dec6129`.
    - Verified post-edit: 0 hits for "drifting field", bare "drift map(s)", or bare "phase map(s)" outside the canonical form.

- [x] **4. Clarify the role of adaptive sampling.** Shicheng wants ASS framed clearly as an extension or future direction; his concern was that its role relative to the main contribution wasn't clear.

    **Status (resolved):** **already addressed by Abby comment #2 work** in commit `894b3f9`. The headline-pillars + extension framing is now consistent across abstract, intro, methods, results, and discussion. ASS is explicitly named as a quality-boosting extension on the core sparse-sampling + drift-correction protocol.
    **Response:** Resolved.
    **Location in revised draft:** Overleaf commit `894b3f9`.

### Overall evaluation

Shicheng's verdict was positive: *"This is a strong and thoughtful paper that addresses a meaningful problem in QPI measurements. The proposed approach is well motivated and shows promising results. With clearer organization, more detailed explanation of key methods, and stronger interpretation of results, the paper would be significantly improved."* His three "would be improved" axes track his major comments #2 (organization), #1 (drift method explanation), and #3 (results interpretation), in roughly that order of importance.

### Cross-cutting summary (Abby ↔ Shicheng overlap)

Significant overlap that resolved together:
- Shicheng major #2 (organization) ↔ Abby major #1 (Results placement). **Resolved together** by commit `1b1c9c6`.
- Shicheng minor #4 (ASS role) ↔ Abby major #2 (what is "our method"). **Resolved together** by commit `894b3f9`.
- Shicheng minor #2 (figure integration, prose-side) ↔ Abby figure-formatting bucket (figure-side). **Partially resolved**; figure-side TODOs captured in commit `fe50cc9`.

Distinct asks Shicheng raises that Abby didn't:
- Shicheng major #1 (drift correction step-by-step) — partially deferred via Fig. 4 placeholder.
- Shicheng major #3 (interpret results practically) — distinct from Abby #3's numerical-SNR-per-iteration. Open TODO.
- Shicheng minor #3 (terminology consistency) — specific copyedit. Open TODO with a clear sweep target.
