# Next work for the ICSC full paper

## Parallel work now

**Codex**
1. **Done:** reconciled manuscript counts and claim boundaries in `EVIDENCE_LEDGER.md`.
2. **Done for drafting:** close-paper comparison and qualified novelty decision in `RELATED_WORK_NOVELTY_MATRIX.md` and `NOVELTY_CHECKPOINT.md`. Recheck citations during manuscript writing.
3. **Reported independent 200-post review complete:** Manu clarified that the reviewers made separate first passes without seeing or discussing answers beforehand. Both files are archived in `reliability_packet/submissions/2026-10-07-independent/`. They match on every categorical and diagnostic answer; all 200 reason texts differ. Exact agreement and Cohen's kappa are 1.0 on each eligible field under that reported workflow. Twenty-nine selected posts differ from prior development labels. A versioned development-only overlay and grouped check are complete; no tests were scored.
4. **Exploratory report done:** `ERROR_ANALYSIS_MANUSCRIPT.md` reports the saved 46 errors with provisional codes and limitations. The planned blinded 92-case coding remains undone and must not be claimed.
5. **Done:** `PAPER_STRUCTURE.md` gives a working eight-page structure. Manuscript prose remains to be drafted.

**Cursor**
1. **Done:** the single semantic comparison is saved in `phase3/semantic_comparator/`. MiniLM's +0.0059 development macro-F1 difference has a paired 95% interval crossing zero; 512/2,136 inputs were truncated. No second embedding model is needed to support the current paper.
2. **Done:** reserved and fresh tests were not scored. Keep the historical fixed TF-IDF model as the primary tested model.

**Manu / a second reviewer**
1. No new human file is required for the 200-post agreement study. The exact agreement is unusual; report the user-confirmed review sequence, prior-exposure limitation, and the difference between agreement and correctness transparently.
2. The 29 changed development decisions are recorded in `changed_decisions.json` and applied in a separate sensitivity snapshot. Keep the historical test records and scores unchanged.

## Gate to manuscript results

The independent-agreement study is complete under the user-reported separate first-pass workflow. The exploratory error report is usable only with its stated limits. The semantic comparison is complete as a development-only indeterminate result. None of these studies changes the historical fixed-model fresh-test result. The next main task is manuscript drafting with the novelty checkpoint and evidence ledger beside it.

## Novelty and related-work checkpoint before full manuscript drafting

Use `RELATED_WORK_NOVELTY_MATRIX.md` as the starting record, then complete these checks:

1. Inspect recent close papers on Reddit/software-update issue mining, software forum classification, and missing bug-report information. Read methods and evaluation, not just abstracts.
2. For the closest 3–5 papers, state their input data, unit of analysis, target categories, evaluation design, and what they already established.
3. Write a narrow contribution statement that survives these comparisons. The candidate is conditional triage of software-update discussion plus an observable diagnostic-evidence profile, with a fixed fresh-set evaluation and explicit transfer limits.
4. Explain who benefits and in what bounded way: sorting already collected update discussions for further human inspection. Do not claim automatic issue resolution, developer usefulness, or novel sentence embeddings.
5. Have Manu review the comparison and contribution statement before locking the introduction and related-work section. A weak or unsupported novelty claim should be revised here, not patched during final formatting.

**Completion artifact:** a short comparison table and a 1–2 paragraph contribution/gap statement, supported by primary citations, ready to insert into the manuscript.
