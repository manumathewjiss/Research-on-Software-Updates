# Why this draft is stronger

Internal review note. Not part of the manuscript or the Overleaf ZIP. The new framing does not raise any saved score.

## What changed

The draft is a standalone IEEE conference manuscript under `phase5/final_synthesis_paper/`. It treats valence, troubleshooting purpose, visible diagnostic facts, and first-pass judgment as separate descriptions, not an evaluated pipeline. The abstract keeps three decision facts: fresh text-only macro-F1 0.792, a sentiment addition whose grouped interval includes zero, and different first actions in 9 of 30 cases. Reserved macro-F1 0.863, the 2,050-row ablation (title and body 0.831932, title 0.750534, body 0.781424), and the VADER, TextBlob, contextual, and MiniLM scores are in the results. Each augmented sentiment interval includes zero. MiniLM is 0.847561, delta +0.015629, and that interval also includes zero. The 542-row secondary cohort stays a different label system. Diagnostic counts match `phase3/diagnostic_results/analysis.json`. The 30 cases are a sibling sample, not a subset of the 237. The study-design figure has no arrow from sentiment to reviewer action. Cassee et al. 2024 and Wang et al. 2026 are cited from Crossref; Wang is an evaluated workflow this paper does not repeat.

The public manuscript does not cite the project GitHub URL, because these phase 2–5 artifacts are local and were not verified on that remote. There is no data-availability section. Acknowledgment names OpenAI Codex and Cursor for different roles and states that neither tool created human labels or engineer choices. Author verification of the final wording is still pending.

## Novelty, stated narrowly

Negative tone, troubleshooting purpose, and a first engineering action are not interchangeable. The evidence for that separation is the null VADER increment on the same development text, the disappearance of the mean valence gap against 68 confirmed dissatisfaction posts, missing reproduction context and error evidence in the 237, and reviewer disagreements in the 30 cases despite overlapping facts. The paper does not claim a new classifier, a new sentiment lexicon, or an evaluated triage pipeline.

## Reviewer-facing strengths

- Every primary denominator is labeled, including the 30 non-Reddit URL records inside the 3,362.
- Held-out purpose scores stay text-only. Sentiment was not attached to the reserved or fresh tests, and those tests were not rescored.
- The lower fresh score, the null development difference, and the lower thread subset are in the paper rather than omitted.
- Diagnostic field rules and the 20-post body split point at the signed analysis file.
- The design figure shows branches. Six overlapping case identifiers are disclosed instead of drawn as nesting.

## Remaining weaknesses

Review provenance for the full collection is mixed, so it is not an independent gold set. The diagnostic sample has no separate field-level agreement. The 30 cases were purposefully varied and involve two readers. Comment coverage is far below the predeclared both-role bar, and comment features are retrospective. VADER, TextBlob, and one frozen contextual score were added to the same development text. None has a sentiment gold label, 188 of 2,050 contextual inputs were truncated at 512 tokens, and the new arms were not scored on the reserved or fresh tests. The MiniLM interval includes zero. The fresh and reserved scores come from separate fits. No saved result links valence, purpose class, visible fields, and the chosen action in one model. Local artifacts are unpublished.

## Future work

TextBlob and a frozen contextual score have now been run on the same folds; both augmented intervals include zero. An independent field recode of the 237 would supply an agreement estimate this joint review does not have. Further case reading would need a new sample and a frozen guide; adding posts after seeing the 30 responses would not repair the current design. None of that work is a reason to rescore the protected tests or to pool the 542-row labels with the current task.
