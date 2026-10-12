# Data rights and ethics check before publication or release

**Status:** unresolved factual review, not a legal opinion and not a finding of a violation. Checked 2026-10-08 against current [Reddit Data API Terms](https://redditinc.com/policies/data-api-terms), [Reddit developer/research guidance](https://support.reddithelp.com/hc/en-us/articles/14945211791892-Reddit-Developer-Interfaces), [Researcher Program](https://support.reddithelp.com/hc/en-us/articles/49381918834964-Reddit-for-Researchers-Program), and [IEEE conference submission policies](https://conferences.ieeeauthorcenter.ieee.org/author-ethics/guidelines-and-policies/submission-policies/). The current rights for the particular `releasetrain.io` pipeline, historical snapshots, and model were not supplied in the repo.

## Why this matters

The latest Reddit Data API Terms restrict use and redistribution of user content and say AI/ML training requires express permission from applicable rightsholders. Reddit's researcher guidance says academic research outputs may be published under conditions, while redistribution of data or derived models is restricted and advance notice may be required. Our corpus came via a third-party API, so the exact collection route, agreement, and permissions must be checked. These policies may have changed over the collection period and might apply differently under a research or commercial arrangement. We should **not assume** that public visibility alone permits releasing full post text, a trained model, or example quotations.

## Facts to obtain from Professor Berhe / the platform owner

1. Which source system collected each Reddit snapshot? Was it Reddit's official Data API, Research API, an approved third-party feed, or another authorized route?
2. Under what account or agreement was collection done, and what uses does it permit for research, model training, paper excerpts, code/data release, and saved copies?
3. Does the earlier [Singh et al. 2024](https://doi.org/10.55432/978-1-6692-0007-9_7) study share underlying posts, tooling, or contractual rights with this study? If so, document overlap and attribution.
4. Are any deletion/retention obligations attached to the stored post text? Who will maintain the corpus after publication?
5. Has the University of the Pacific made an IRB/exemption or other ethics determination for this use of public posts? If not, ask the appropriate institutional office rather than claiming approval or exemption.

## Safe preparation while those answers are pending

- Write methods using aggregate counts and reproducible processing steps. Do not promise a public raw-text dataset or trained weights.
- Prefer post IDs/metadata or controlled-access instructions only if the applicable terms permit; review before release. Consider paraphrased, nonidentifying examples where scientifically sufficient.
- Keep the existing private research snapshots intact. Do not delete or redistribute them based on this checklist alone.
- Check IEEE's AI-content disclosure, author approval, prior-publication, and human-subject statements before the final submission. AI-generated manuscript passages require the disclosure described by [IEEE](https://conferences.ieeeauthorcenter.ieee.org/author-ethics/guidelines-and-policies/submission-policies/); do not state that every label was unaided or independently human-produced when provenance is mixed.

**Gate:** The paper can be outlined without these answers, but claims about a releasable dataset/model and the final ethics/data-availability statement should not be locked until the source agreement and institutional guidance are known.
