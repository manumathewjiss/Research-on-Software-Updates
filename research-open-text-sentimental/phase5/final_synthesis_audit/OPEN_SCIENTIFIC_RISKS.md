# Open scientific risks

## Critical flaw

There is no saved result that connects valence, purpose classification, diagnostic fields, and engineering action as one chain.

- The sentiment models were not scored on the reserved or fresh tests (`phase5/sentiment_paper/RESULTS.md`: tests not scored).
- The 30-case study does not include VADER and does not measure whether the classifier changed a decision (`phase4` PDF: no causal effect, no classifier-assisted workflow).
- The 237-post field rates describe the saved title and body. They are not an outcome.
- Historical TPS/GDS divergence does not transfer to the current negative class (`RESULTS.md`: 68 dissatisfaction posts, mean difference +0.0036, interval includes zero).

A combined paper that writes these as successive stages of one system — sentiment finds risk, the classifier ranks it, diagnostics show what is missing, reviewers then act — would assert a pipeline the files do not support. That is the flaw to avoid. The coherent paper is the negative one: these are different descriptions, and the links between them are weak or absent.

## Other risks if drafting continues

1. **Label substitution.** Calling the current negative class GDS, or calling the 542 labels the same task as S2, reverses the polarity paper's main correction.
2. **Hiding the lower scores.** Fresh macro-F1 0.792 is lower than reserved 0.863 and lower than development 0.832. The thread hybrid is lower than thread text. Both are findings.
3. **Comment timing.** Stored comments are partial, class-dependent, and at or after the post. They cannot support a prospective or causal sentence.
4. **Empty-body zero.** VADER scores an empty document as 0. 303 of 2,050 bodies are empty (`RESULTS.md` / polarity paper). That zero is not a measured neutral emotion.
5. **Group interval on 797 posts.** It excludes zero, but 790 of 797 groups contain one post (`group_bootstrap.json`). It is not strong cluster-robust confirmation.
6. **BERT and 324-post cohort.** Easy to cite because the files are large. They answer older, differently sampled questions.
7. **ReleaseTrain product claims.** Root `readme.md` marks sentiment as todo. Candidate endpoints and `metadata.predicted` are not labels. The 3% figure remains undocumented.
8. **Annotator provenance.** The 542 `notes` column is empty. "Gold" overstates what `RESEARCH_AUDIT.md` could verify.
9. **Sibling repositories.** Release-note generation, RAG, and update-risk pointers have no evaluation on this labeled set. They are not additional experiments.
10. **Protected tests.** Any draft that refits, tunes, or rescores the 159 or 344 posts breaks the separation the reconciliation file records.

## What was not found

No notebook, archive, or abandoned output contained a human-confirmed "this comment resolved the issue" label, a verified risk prevalence, or a head-to-head test of sentiment features on the fresh IDs. Those absences were checked in `AUDIT.md`, `ADDITIONAL_STUDIES_DECISION.md` in phase2, and the reconciliation file. They are not gaps to fill by rerunning a model before the scientific frame is chosen.
