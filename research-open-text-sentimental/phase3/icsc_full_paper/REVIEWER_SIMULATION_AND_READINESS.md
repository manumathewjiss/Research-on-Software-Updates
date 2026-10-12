# Three-reviewer simulation and final prewriting decision

**Status:** an internal critical exercise, not real reviews or an acceptance probability. Based on saved evidence and `FINAL_LITERATURE_AUDIT.md` as of 2026-10-08. No manuscript was written.

## Reviewer 1 — machine learning

- **Strongest contribution:** A fixed model specification compared with simple baselines on reviewed data, with duplicate-aware development work and a separately collected fresh-ID sample. Both class F1s and the lower fresh score are reported.
- **Biggest weakness:** The 0.863 reserved test and 0.792 fresh test use **different training versions** (2,084 versus 2,080) and different test compositions. The negative classes are small (24 and 67). Later audits changed development labels, but no newly refitted model has an untouched test. A model only sees already human-scoped S2 posts.
- **Likely rejection reason:** The paper implies broad, end-to-end or stable generalization from conditional, source-selected tests, or it reports the two test rows as the same fitted model.
- **Best repair before writing:** Use `RESULT_VERSION_RECONCILIATION.json`; make conditional scope and model-fit versions explicit; show both class supports/intervals and avoid causal claims about score changes. Do not tune on either seen test.

## Reviewer 2 — software engineering

- **Strongest contribution:** A useful distinction between a concrete troubleshooting purpose and other update talk; the 237-case diagnostic field profile shows what is and is not visible in actual post snapshots.
- **Biggest weakness:** [Singh et al. 2024](https://doi.org/10.55432/978-1-6692-0007-9_7), coauthored by Berhe, already mined Reddit software-update feedback; [Iqbal et al. 2021](https://doi.org/10.1109/RE51729.2021.00019) and [Wang et al. 2024](https://doi.org/10.1016/j.jss.2024.112108) cover Reddit/forum software feedback; [Chaparro et al. 2017](https://doi.org/10.1145/3106237.3106285) covers missing bug details. We have no evidence that the checklist improves developer decisions or that output is actionable.
- **Likely rejection reason:** Incremental task renaming plus conventional classification, with practical utility asserted but not measured; ambiguous overlap with the same lab's earlier work.
- **Best repair before writing:** Explicitly compare task/data/unit/outcome with Singh, Iqbal, and Wang. If the authors want an *actionability* claim, run a separately designed practitioner study; otherwise remove that word as a measured result. Clarify API/data relationship with the 2024 work.

## Reviewer 3 — semantic computing

- **Strongest contribution:** A meaning-level distinction (problem-solving intent versus other discussion) and a structured profile of visible diagnostic evidence in informal text.
- **Biggest weakness:** The actual system is TF-IDF logistic regression after human scope selection; frozen MiniLM gives no reliable improvement and no knowledge representation, semantic reasoning, issue graph, or developer-facing interpretation was evaluated. A [2026 evidence-aware issue-specification study](https://doi.org/10.1007/s10515-026-00640-x) already does richer evidence-governed post-release triage and human artifact evaluation.
- **Likely rejection reason:** The paper appears to be ordinary text classification with a conference-specific “semantic” label added to the introduction.
- **Best repair before writing:** Explain the semantics as an empirical problem of **discussion purpose and observed diagnostic attributes**, not as a novel architecture. Show hard boundary examples and the codebook. If that contribution still reads thin in an eight-page mock outline, consider adding a genuine downstream question or selecting a more natural software-engineering venue.

## Final answers to the requested readiness questions

1. **Are we ready to begin writing?** **Conditionally yes.** The research evidence is sufficient for a bounded empirical manuscript, but first lock the exact claim, approve the completed result-version reconciliation, and clarify the 2024 same-lab relationship. `FINAL_PREWRITING_RESEARCH_AUDIT.md` lists those decisions. Do not begin writing automatically after this audit; review them with the human authors, as requested.
2. **What is essential before writing?** Resolve whether the paper is explicitly conditional S2 triage; review the corrected 2,084/2,080 version distinction already documented in `RESULT_VERSION_RECONCILIATION.json`; confirm authorship/provenance and the relationship to Singh et al. 2024. Check project-specific data rights and institutional ethics before promising dataset or model release or finalizing the methods disclosure. The literature screen and candidate bibliography are prepared. No new model run or bulk review is essential for the bounded claim.
3. **What is optional?** A practitioner outcome study or untouched end-to-end scope-plus-purpose test would materially strengthen a larger claim. Blind 92-case error coding can improve qualitative trust if error patterns become central. Extra model families, more keyword-pool labels, issue clustering, and sentiment are low priority for this paper.
4. **Should research stop and manuscript writing start?** For the bounded empirical question, **yes after the essential decisions**. For a claim of a novel semantic-computing system or developer impact, **no**—the current evidence does not support it, and a new study would be needed.
5. **PI next move:** Hold a short author decision meeting using the corrected audit, novelty comparison, and display plan. Choose either (A) submit a candid conditional triage + diagnostic profile study, or (B) invest in a predesigned downstream evaluation before targeting an ICSC regular paper. Then freeze the exact data/claim sheet and draft. Do not use the historical 20% venue acceptance figure as a paper-specific forecast.
