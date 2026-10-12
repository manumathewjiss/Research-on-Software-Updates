# Eight-page regular-paper structure (working)

**Core question:** Among already identified software-update discussions, can post text distinguish concrete troubleshooting from other discussion, and what diagnostic details are visible in troubleshooting posts?

1. **Introduction and contributions (~0.75 page):** motivate update triage; state conditional scope; list task/corpus, fixed evaluation, diagnostic profile. Avoid a sentiment or resolution claim.
2. **Related work (~0.75 page):** compare directly with Iqbal et al.'s Reddit software-post classification; then bad updates, software forums, missing bug-report information, and classifier transfer. Use `RELATED_WORK_NOVELTY_MATRIX.md` and `NOVELTY_CHECKPOINT.md` to make the difference specific.
3. **Data and annotation (~1.25 pages):** collection flow, 3,362 unique combined records, 30 non-Reddit records, Phase 2 review provenance, S2 definition, class composition, duplicate policy, reserved/fresh split. Include independent-agreement study only if completed.
4. **Methods (~1 page):** fixed TF-IDF logistic regression; baselines; grouped development validation; threshold selection; what information the classifier sees. Add the frozen MiniLM development-only comparison with inner-fold threshold selection and 256-word-piece truncation.
5. **Classifier results (~1 page):** historical revised 2,080 development, 159 reserved S2, 344 fresh S2. Report both class F1s, macro-F1, intervals, confusion matrix, and class imbalance. Present 2,166 audited-development sensitivity separately. MiniLM gives +0.006 macro-F1 versus TF-IDF on the same 2,136 Reddit-only development folds, with a paired interval spanning zero; it is not the fresh-test model.
6. **Diagnostic evidence (~0.75 page):** 250 random sample, 237 confirmed troubleshooting; field rates, uncertainty, title-only context, exploratory association with grouped development misses.
7. **Error analysis and validity (~1 page):** 46 fresh errors and matched correct cases using the explicitly exploratory `ERROR_ANALYSIS_MANUSCRIPT.md`; source/selection bias, review provenance, limited class sizes, observed-only diagnostic fields, conditional task, and test-set provenance.
8. **Conclusion (~0.25 page):** bounded supported claim and next steps. No promise of automated resolution or Reddit-wide prevalence.

**Draft now:** the full paper can be drafted from the evidence ledger, including the reported independent first-pass agreement and the bounded exploratory error reading. Do not describe the unfinished 92-case blind coding as completed. Reconcile the final figure/table budget against the venue's current instructions before formatting.

Before locking the introduction and related-work prose, pass the novelty checkpoint in `NEXT_WORK.md`: direct comparison with the closest studies, a defensible gap, a precise contribution, and a bounded use case.
