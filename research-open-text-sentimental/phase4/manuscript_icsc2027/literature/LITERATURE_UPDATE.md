# Literature update — 8 October 2026

## Scope

DRAFT_V2.md expands the Introduction and Related Work to 19 selected references, including 11 from 2024–2026. This was a targeted search, not a systematic review or an exhaustive novelty proof. Searches covered Reddit requirements mining, forum feedback, bug-report information needs, evidence sufficiency, feedback-to-issue workflows, industrial adoption, and classifier generalization. Primary publisher pages, author manuscripts, conference pages, and bibliographic metadata were preferred. Links are in the manuscript and references.bib.

The agreed abstract is unchanged. No dataset, experiment, numerical result, or study design was changed. Sentence-BERT was added as a framework reference in the methods.

## Contribution supported by the literature

Report quality, missing information, evidence sufficiency, and conversion of feedback into engineering artifacts are established research topics. Our contribution is the empirical connection between purpose classification, visible diagnostic evidence, and reviewers’ explanations of first-pass actions on selected intact update discussions. It does not establish causality, correct decisions, or productivity. Related studies with stronger downstream evaluation are acknowledged explicitly.

## Source selection and reading depth

Reference numbers match DRAFT_V2.md. Earlier review means existing project literature records were used, not a complete rereading this turn.

| Ref | Study | Contribution to our framing | Reading boundary |
|---|---|---|---|
| 1 | Hassan et al., Bad Updates, 2020 | Update-feedback motivation | Earlier author-paper review |
| 2 | Tkalich et al., Continuous software engineering feedback, 2025 | Industrial interpretation difficulties | Publisher abstract/introduction |
| 3 | Iqbal et al., Mining Reddit, 2021 | Reddit purpose classification | Author PDF including methods |
| 4 | Wang et al., Conversation in forums, 2024 | Value of post context | Publisher abstract/highlights and earlier record |
| 5 | Chaparro et al., Missing information, 2017 | Established information-gap problem | Earlier author-paper review |
| 6 | Wang et al., Evidence-aware issue specifications, 2026 | Close evidence-sufficiency comparator | Publisher HTML, introduction and methods |
| 7 | Laiq and Dobslaw, Classification mapping, 2026 | Generalization and practitioner evaluation | Publisher abstract/introduction |
| 8 | Tizard et al., Forum requirements, 2019 | Conversation-level requirements | Earlier author-paper review |
| 9 | Zegers et al., Accountability concerns, 2025 | Broader Reddit feedback purposes | Official conference abstract only |
| 10 | Singh et al., Release-note enrichment, 2024 | Update-domain background | Earlier full-paper comparison; separate project per author clarification |
| 11 | Bettenburg et al., Good bug reports, 2008 | Developer/reporter information mismatch | Author PDF |
| 12 | Soltani et al., Bug report elements, 2020 | Different significance of fields | Publisher abstract/introduction |
| 13 | Wang et al., Web-application information needs, 2025 | Information added over report lifetime | Publisher abstract/highlights; full page restricted |
| 14 | Bo et al., ChatBR, 2024 | Detecting missing components and generating additions | Author manuscript and institutional record |
| 15 | Tang et al., Collaborative bug finding, 2024 | Reproduction and downstream bug reporting | Publisher abstract/introduction |
| 16 | Laiq et al., Industrial adoption, 2024 | Trust and integration | Publisher abstract/introduction |
| 17 | K C and Hosseini, Moodle, 2026 | Forum-to-issue handoffs | Author HTML manuscript including methods |
| 18 | Devine et al., Classifier generalization, 2023 | Unseen datasets versus unseen applications | Author abstract and earlier record |
| 19 | Reimers and Gurevych, Sentence-BERT, 2019 | Embedding framework | ACL record; local SentenceTransformer use checked |

## Bibliographic cautions

- Moodle’s manuscript reports RE 2026 acceptance; a proceedings DOI was not verified. It is explicitly cited as an arXiv manuscript.
- The web-application information-needs article has a 2024 DOI/online date and a 2025 issue year. We use the issue year.
- ChatBR’s author manuscript and institutional abstract contain differing similarity numbers. Our comparison uses only the methodological description, with no such number.
- Tang’s publisher page links a correction. No specific performance or bug-count result is used in our manuscript comparison.
- Some Crossref requests were rate-limited. Publisher metadata was used for those entries; crossref_additions.json records request outcomes. Not every entry was independently verified through Crossref.
- We do not compare F1 scores directly across papers with different datasets, labels, and evaluation designs.

## Exclusions and final checks

Redundant model comparisons, broad LLM papers, and an AI-agent report-quality study with a different target were not added merely to enlarge the bibliography. Additional formal-report reproduction work was unnecessary for the present argument.

Checked: 19 numbered references, all cited in first-appearance order; 19 BibTeX entries; agreed abstract unchanged. Final IEEE layout and page-budget checks remain. The existing source-provenance wording discrepancy elsewhere in the draft is not resolved by this literature edit and needs separate reconciliation before submission.
