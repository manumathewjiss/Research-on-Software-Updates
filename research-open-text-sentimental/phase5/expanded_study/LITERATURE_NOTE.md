# Literature note for a later manuscript revision

Verified 9 October 2026 from Crossref (`api.crossref.org`), not from the request text alone. This note does not change `run_expanded.py`, its outputs, or `phase5/final_synthesis_paper/main.tex`.

## Cassee et al. 2024

- Title: Transformers and meta-tokenization in sentiment analysis for software engineering
- Authors: Nathan Cassee, Andrei Agaronian, Eleni Constantinou, Nicole Novielli, Alexander Serebrenik
- Journal: Empirical Software Engineering
- Volume 29, issue 4, article number 77
- Published: 3 June 2024
- DOI: https://doi.org/10.1007/s10664-024-10468-2
- The request's "29:77" matches volume 29 and article number 77. Crossref has no page range.

Not yet cited in the current manuscript. Relevant because it studies transformer sentiment models on software-engineering text, which is the comparison the development-only run is attempting with a frozen social-media RoBERTa. Cite it only after the saved scores exist, and do not treat the paper as evidence that those models help on this Reddit task.

## Wang et al. 2026

- Title: From noisy feedback to evidence-aware issue specifications: an agent-governed retrieval-augmented generation approach
- Authors: Zhiyao Wang, Jialong Li, Xiujing Guo, Tatsuhiro Tsuchiya
- Journal: Automated Software Engineering
- Volume 33, issue 3, article number 103
- Published: 31 July 2026
- DOI: https://doi.org/10.1007/s10515-026-00640-x

A search of `phase5/final_synthesis_paper/references.bib` and `main.tex` finds neither `Wang2026Evidence` nor Cassee, and neither DOI. The current manuscript does not cite Wang et al. Both sources should be added only in a later rewrite, after the full bibliographic details are copied into `references.bib`. Do not describe the present draft as already citing Wang.

## Implication for the later rewrite

If Wang et al. are added later, cite them as an evaluated end-to-end evidence-aware workflow that this paper does not repeat. Any workflow figure here has to be labeled unevaluated. The novelty claim stays with the Reddit measurements that keep valence, troubleshooting purpose, visible diagnostic facts, and first-pass actions separate. Do not describe those four descriptions as a tested pipeline, and do not say the current draft already cites this work.

Neither source is a reason to change the frozen 2,050-row protocol, the grouped folds, or the held-out tests.
