# Qualitative-study claim and evidence matrix

**Scope:** Only the 30 main cases. Pilot cases are excluded. `main_submissions/` are the immutable first-pass sources; `ANALYST_ONLY_PAIRED_RESPONSES.csv` is a joined analyst view. This matrix supports interpretation and does not create a correctness key.

| Proposed bounded claim | Case evidence | Contrasts / limits |
|---|---|---|
| Both reviewers sometimes treated a concrete update-linked failure with comparisons or recovery impact as reason to open a lead now. | Q001, Q002, Q008, Q010, Q014, Q016, Q026: both A, with cited post facts in paired responses. | Q003, Q005, Q009, Q018: one reviewer chose B despite specific symptoms. The cases were selected purposefully, so do not say how often this happens generally. |
| Missing distinctions could block immediate investigation even when a problem was reported. | Q006, Q011, Q015, Q017, Q024, Q029: both B, with specific proposed questions. | Q004 and Q010: both A despite additional information being unknown. Thus “missing data” alone is not a decision rule. |
| A reported workaround or fix can be interpreted as either an investigation lead or a reason to monitor. | Q007 and Q012: A/C disagreements; Q019: both A despite a workaround. | The study does not establish whether a fix worked for other users or whether an issue was actually resolved upstream. |
| Existing purpose labels and first triage actions are distinct constructs. | Q026 historically `other` but both A; Q023 and Q028 historically `general_dissatisfaction` with C/cannot-assess and A/C actions respectively. | Three purposively selected boundary cases do not measure the rate of such divergence in the corpus. Do not treat the historical label as a wrong/correct key for actions. |
| Reviewers could cite similar evidence yet make different first-action choices. | Q003, Q005, Q007, Q009, Q012, Q018, Q022, Q023, Q028, with each reviewer’s evidence and reason preserved separately. | No adjudication is planned. Different actions may reflect experience, risk threshold, or reading of the supplied snapshot; causes of disagreement were not experimentally isolated. |
| Some update-related discussion supplied no current fault to triage. | Q021, Q025, Q027, Q030: both D, with reasons tied to planning, positive feedback, checklist discussion, or version lookup. | Deliberately selected negative cases; not a prevalence estimate. |

## Claims excluded from the paper unless new evidence is obtained

- “Information completeness predicts engineering usefulness.” No validated utility outcome exists.
- “A version number, rollback, or error message causes investigation.” No intervention on those fields was performed.
- “The model predicts first actions.” The classifier predicts discussion purpose, not triage action.
- “The two reviewers represent software engineers generally.” Only two qualified external reviewers participated.
- “The decision was objectively correct.” There is no incident-resolution or ground-truth action label.

The final manuscript should use only a small number of de-identified or paraphrased examples permitted by the data-use arrangement; this matrix is analyst-only and includes case IDs for traceability.
