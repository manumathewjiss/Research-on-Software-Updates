# Beyond Troubleshooting Detection: Diagnostic Evidence and First-Pass Engineering Decisions in Reddit Software Update Discussions

**Manu Mathew Jiss and Solomon Berhe**  
University of the Pacific, School of Engineering and Computer Science  
**Working full-paper draft, 8 October 2026. Not submission-ready.**

## Abstract

Informal discussions after software updates mix fault reports with advice, reactions, and general conversation. A model that finds a technical post does not establish what an engineer can do with it. We examine this gap by connecting discussion-purpose classification, observable diagnostic information, and first-pass engineering decisions in Reddit software update discussions. The study combines a collection of 3,362 posts with classifier evaluation, diagnostic coding, and an exploratory case study involving two independent software-engineering reviewers. Within human-established software-update scope, a title-and-body TF-IDF logistic-regression classifier achieved macro-F1 0.792 on a fresh test, outperforming majority and fixed-keyword baselines. This evaluation followed an earlier reserved test and used the same selected configuration fitted on revised development data. The smaller other-update class remained harder to classify. Diagnostic coding showed that many troubleshooting posts lacked visible reproduction context or error evidence. In 30 purposefully selected cases, reviewers sometimes cited similar facts but chose different actions, including investigation, clarification, and monitoring. Their explanations exposed differing judgments about whether the available evidence justified acting immediately or required further information. These observations are exploratory and do not establish causal effects, population-wide decision patterns, or downstream engineering benefits. Together, the findings distinguish identifying a post’s purpose from interpreting its implications: purpose detection can organize discussions, while first-pass engineering decisions also reflect the available diagnostic evidence and reviewers’ judgments about its sufficiency.

**Index Terms:** software updates, social-media mining, troubleshooting, software engineering, triage, diagnostic evidence

## I. Introduction

Users frequently describe software changes outside an issue tracker. Their posts may report a crash after an update, ask whether a new version caused a failure, complain about an interface change, or simply discuss an upcoming release. These texts offer a potential source of post-release feedback, but the same update vocabulary appears across different purposes. Engineers first need to know whether a post concerns a technical problem, then decide whether the post supplies enough context to investigate or whether another first response is more appropriate.

The distinction matters because a broad negative category such as *general discontent* hides several kinds of discussion. A post that announces a release and a post that criticizes a design change need not be handled in the same way. Likewise, a post labeled troubleshooting can contain a concrete comparison, a vague symptom, or a reported workaround. Classifying purpose and choosing an engineering action are therefore related but separate tasks.

Prior studies have mined Reddit for software requirements [1], connected Reddit feedback with release notes [2], examined information in forum conversations [3], and studied missing information in formal bug reports [4]. Our study asks a narrower question in the software-update setting. **RQ1:** Within posts already judged to concern software and an update, how well can title and body text distinguish troubleshooting from other update discussion? **RQ2:** Which diagnostic facts are visible in a reviewed sample of troubleshooting posts? **RQ3:** How do two software-engineering reviewers use such facts when selecting an initial response to intact posts?

We make three empirical contributions. First, we define a conditional discussion-purpose task and document the collection, review, and split boundaries that make its evaluation interpretable. Second, we evaluate a fixed text classifier against simple baselines on a new-ID test and report the minority-class errors rather than relying on accuracy alone. Third, we connect post-level diagnostic observations to a small, exploratory human case study of first-pass decisions. We do not claim a new semantic representation, an end-to-end Reddit monitor, or demonstrated improvements in engineer productivity.

## II. Related Work

Iqbal et al. [1] classified Reddit software posts for requirements-related uses. Singh et al. [2], a separate study involving one of the present authors, connected Reddit feedback with release notes to study update impact and prioritization. That work asks how external feedback augments a release-note workflow. Our unit is an individual post, our predicted target is troubleshooting purpose within reviewed update discussion, and our human study examines the first action taken on the saved post. We neither reproduce the release-note join nor evaluate impact prioritization. The available records describe different post-creation periods; we make no claim of a measured improvement over [2].

Software-forum studies have shown that useful development information appears in conversations and context beyond isolated sentences [3], [5]. Studies of bad application updates motivate attention to post-release effects [6]. Yet a forum post's purpose, the details it contains, and a possible engineering action are distinct constructs. Our work measures each at a different stage rather than treating a troubleshooting label as a validated actionability score.

Formal bug-report research identifies missing expected behavior and reproduction details [4]; more recent work assesses or improves report quality [7]. We do not introduce a new completeness detector or generate issue reports. Our diagnostic coding describes information visible in informal update posts, where a user may be unsure whether the update caused the symptom. Research on classifier transfer [8] further motivates reporting performance on an unseen-ID sample instead of presenting development validation alone. A frozen sentence-embedding comparison serves only as a development sensitivity check; it does not establish a new semantic model or a reliable gain over lexical features.

## III. Collection, Review, and Study Population

### A. Candidate collection and labels

The combined research collection contains 3,362 unique IDs: 542 from the original project and 2,820 additional records obtained from two ReleaseTrain API candidate pools after overlap removal. The API's `tps` and `gds` pool names describe retrieval routes, **not** reference labels. Thirty records in the combined collection point to Stack Overflow, so the collection is not wholly Reddit. It is also a selected research collection rather than a random sample of all update discussion.

Phase 2 review separated three questions: whether the text is about software, whether it connects to an update, and the main discussion type. The update rule includes an author who explicitly states, suspects, or asks whether an update, patch, release, or upgrade caused or affected a problem. The discussion types distinguish technical troubleshooting, general dissatisfaction, other discussion, and cases that are out of scope or cannot be classified. The binary modeling task, called S2 in the project records, includes posts with `about_software=yes` and `update_related=yes`. Its positive class is technical troubleshooting. Its negative class is **all other update discussion**, including but not limited to dissatisfaction.

Review provenance varies across the combined collection. Most Phase 2 decisions were reviewed with assistance; other portions were jointly reviewed or used for pilots and protected tests. These statuses must not be described as a corpus-wide independent double annotation. A later selected 200-post development check produced identical submitted categorical decisions across two reported separate first passes, but that selected check does not establish correctness or independent provenance for every master record. Five combined records retained unresolved Phase 2 decisions. We preserve the historical review and model snapshots rather than retroactively changing them after test results were known.

### B. Development and test roles

Table I separates the collection from the populations used in model evaluation. An initial model-selection experiment used 2,084 eligible development posts and a 159-post reserved test (135 troubleshooting, 24 other). After label-quality repairs, the same selected configuration and threshold were fitted on a revised set of 2,080 eligible development posts (1,686 troubleshooting, 394 other). This revised fit was evaluated once on a fresh set. The fresh collection began with 500 unseen-ID candidates sampled after overlap and duplicate exclusions; joint review found 344 S2-eligible posts (277 troubleshooting, 67 other). Many new-ID posts were written before the October collection, so this is not a wholly prospective temporal test. Test eligibility was established by review: the classifier was **not** asked to detect software or update scope from the original 500.

**TABLE I. Distinct roles of the saved data**

| Record set | Count | Role and boundary |
|---|---:|---|
| Combined collection | 3,362 unique IDs | Candidate collection and review history; includes 30 Stack Overflow URLs |
| Original development fit | 2,084 S2 | Chosen configuration behind reserved test |
| Reserved test | 159 S2 | Earlier one-time test; 135 troubleshooting, 24 other |
| Revised development fit | 2,080 S2 | Same chosen configuration behind fresh test; 1,686 troubleshooting, 394 other |
| Fresh review batch | 500 candidates | New IDs screened without consulting classifier scores |
| Fresh test | 344 S2 | One-time evaluation; 277 troubleshooting, 67 other |

*Figure 1 should show the collection and the two distinct model fits. Its counts must be generated from the frozen manifests, not copied from this draft.*

## IV. Purpose Classification Method

The input to the classifier is a post's saved title and body. We use word unigrams and bigrams weighted by term frequency–inverse document frequency (TF-IDF), followed by logistic regression with balanced class weights. The selected regularization parameter is `C=4`; the development-selected troubleshooting probability threshold is 0.5877. Vectorization was fitted within training folds during model selection. Development comparisons included title-only and title-plus-body features, a linear support-vector machine, an always-troubleshooting majority rule, and a fixed troubleshooting-keyword rule. The selected configuration used title plus body.

Exact and highly similar title/body records were grouped for a subsequent development check so they would not straddle validation folds. Additional development-only analyses restricted the data to Reddit URLs and examined class balancing. A frozen MiniLM embedding plus logistic-regression comparator was evaluated on the same 2,136 audited Reddit-only development posts as a TF-IDF comparator. Its macro-F1 was 0.844 versus 0.839 for TF-IDF; the paired difference was approximately +0.006 with a 95% interval of −0.016 to +0.029. This does not provide reliable evidence that the more complex representation is better. Neither protected test was used to choose the embedding comparator.

We report macro-F1 because it gives the two classes equal weight, alongside each class's precision, recall, and F1. This is important for the minority other-update class. The reserved and fresh tests used the same model **specification and threshold**, but different fitted development snapshots and different evaluated posts. Their difference is descriptive, not a controlled estimate of domain shift.

## V. Purpose-Classification Results

Table II presents the two protected results without merging their training histories. The reserved test reached macro-F1 0.863. The revised fit reached macro-F1 0.792 on the fresh S2 sample; its 95% bootstrap interval was 0.731–0.845. On that fresh sample, the majority rule reached 0.446 and the fixed keyword rule 0.474. The stronger text result supports the presence of usable lexical signal for this conditional task. It does not show that the system can screen arbitrary Reddit posts end to end.

**TABLE II. Protected purpose-classification results**

| Evaluation and model | Fit n | Test n (other / trouble) | Macro-F1 | Other F1 | Trouble F1 |
|---|---:|---:|---:|---:|---:|
| Reserved, selected TF-IDF LR | 2,084 | 159 (24 / 135) | 0.863 | 0.766 | 0.959 |
| Fresh, revised TF-IDF LR | 2,080 | 344 (67 / 277) | 0.792 | 0.667 | 0.916 |
| Fresh, majority rule | — | 344 (67 / 277) | 0.446 | 0.000 | 0.892 |
| Fresh, fixed keyword rule | — | 344 (67 / 277) | 0.474 | 0.396 | 0.552 |

On the fresh set, 46 of 67 other-update posts were correctly classified and 21 were false troubleshooting alarms. Of 277 troubleshooting posts, 252 were correctly classified and 25 were missed. The other-update F1 of 0.667 and its small support limit strong claims about non-troubleshooting discussions. The lower fresh score compared with the reserved score should be visible to readers; because both fit and test populations changed, the decrease cannot be assigned to a single cause. Exploratory reading of the 46 fresh errors suggests that missing body context and mixed purpose can matter, but the proposed error categories were not validated by a separate blind coding study and are not presented as a prevalence taxonomy.

## VI. Observable Diagnostic Evidence

A separate simple random sample of 250 posts was drawn from the then-current 1,658 Reddit-only S2 troubleshooting development records before diagnostic answers were recorded. Closer review retained the troubleshooting designation for 237 posts, marked four as not troubleshooting, and marked nine unclear. We report field rates conditional on the 237 confirmed cases, without changing the historical classifier test labels. A field was counted only when visible in the saved title or body; absence from this snapshot does not imply absence from the full conversation or incident.

**TABLE III. Details visible among 237 reconfirmed troubleshooting posts**

| Detail | Posts | Percent |
|---|---:|---:|
| Software product | 218 | 92.0 |
| Identifiable release | 122 | 51.5 |
| Device or environment | 137 | 57.8 |
| Specific symptom | 237 | 100.0 |
| Reproduction context | 108 | 45.6 |
| Error evidence | 40 | 16.9 |
| Attempted remedy | 118 | 49.8 |
| Explicit request for help | 168 | 70.9 |

The 100% symptom rate partly follows from reconfirming the troubleshooting category and should not be interpreted as an independent discovery. Error evidence and reproduction context were less often visible. Twenty confirmed cases lacked a saved body; reproduction context appeared in only two of these, compared with 106 of 217 cases with body text. These figures describe what the collected snapshots reveal; they are not a validated report-quality scale or a measure of an engineer's ability to fix the problem.

An exploratory join with grouped development predictions found 16 misses among the 237 confirmed cases, including eight of the 20 without a saved body. Because this is a small, development-derived comparison, we do not attribute a causal effect to missing text or to any one diagnostic field.

## VII. First-Pass Engineering Decisions

To study how an engineer might use the evidence in a post, we conducted an exploratory multiple-case study. After a six-post pilot, two reviewers with software-engineering knowledge read 30 purposefully selected intact title/body snapshots. The main cases varied by community, update situation, symptom, evidence, and expected difficulty; pilot cases were excluded. The reviewers were asked to choose a first response: open an update-focused investigation lead, request a specific clarification, monitor or group similar reports, take no update-focused action, or indicate that the case could not be assessed. They also recorded the evidence they used and explained the choice. The old discussion label was hidden. Manu reports that the two reviewers completed separate first passes without discussion or outside lookup. We preserve their submitted answers rather than constructing a correctness key.

The two reviewers chose the same first action in 21 of the 30 cases and different actions in nine. Both selected investigation in ten cases, clarification in six, monitoring in one, and no update-focused action in four. These are counts from deliberately varied cases and two reviewers, not estimates of how frequently engineers would make these choices in practice.

The explanations reveal three useful contrasts. First, concrete update-linked failures together with comparisons or a recovery impact could support immediate investigation in these cases. Second, even a concrete symptom did not always settle the next action: in one Chrome crash case both reviewers wanted to distinguish normal from incognito behavior before opening a lead, and in a ZFS case both wanted to clarify the space measurement. Third, a reported workaround did not map to one action. Both reviewers opened a lead for one VS Code case with a workaround, whereas in two other cases one reviewer opened a lead and the other preferred monitoring. In nine disagreement cases, reviewers often cited overlapping facts yet differed about whether those facts were sufficient to act now, which question should be answered first, or whether wider impact should be established.

Purpose and first action also diverged in selected boundary cases. One historically `other` post described application breakage after a channel change; both reviewers chose to investigate it. Some dissatisfaction-labeled posts described concrete changed behavior but led to different actions. These examples illustrate why an old purpose label cannot serve as an action key. They do not measure how often such divergence occurs in the collection.

## VIII. Discussion and Threats to Validity

The evidence supports a staged interpretation. A simple text model can organize *reviewed* software-update discussion by purpose better than basic rules. Diagnostic coding shows that many troubleshooting snapshots lack an error trace or reproduction context. Yet an engineer's first action depends on more than a checklist: reviewers considered severity, contrasts, alternative explanations, reported remedies, and possible wider scope. The qualitative cases make this distinction visible, but they do not prove that any field causes an action or that either reviewer chose the objectively correct one.

Several boundaries limit the findings. **Selection:** the combined collection arose from historical data and API candidate routes, not random Reddit sampling. Its class proportions are not population prevalence. **Labels:** review provenance is mixed and some work was assisted or joint; the selected independent-check files cannot validate the full corpus. The fresh test uses jointly reviewed labels and only 67 other-update cases. **Evaluation:** S2 scope was supplied by human review, so the classifier result is conditional. The reserved and fresh scores belong to separate fits, and many fresh IDs were not temporally new. Development-only robustness checks do not replace protected tests. **Diagnostic coding:** field observations use saved title/body text, exclude 13 uncertain or rejected sampled cases, and have no independent field-level agreement estimate for that 250-post study. **Human study:** two reviewers and 30 purposefully chosen snapshots support exploratory reasoning patterns, not population frequencies or causal effects. Comments, edits, or incident knowledge unavailable in the snapshot could change real-world decisions. The study did not observe issue resolution, engineer time, or deployment outcomes.

The paper's practical use is therefore a possible *organizing step*, not a validated triage system. An analyst could use a purpose filter to find update-linked problem reports and then inspect their evidence before deciding whether to investigate, ask, or monitor. A future study could evaluate this workflow in a real queue with measured decisions and outcomes.

## IX. Conclusion

In a reviewed collection of software-update discussions, title and body text distinguished troubleshooting from other discussion more effectively than majority or fixed-keyword rules on an unseen-ID test. The fresh-test macro-F1 was 0.792, with weaker performance on the smaller other-update class. A separate diagnostic sample showed that error evidence and reproduction context were often absent from saved troubleshooting text. In 30 intact cases, two reviewers sometimes made different first-action choices while citing similar evidence. Together, these findings show why post-purpose classification can support, but cannot replace, evidence-based human triage. The results are conditional on the reviewed scope and do not establish end-to-end monitoring or downstream engineering benefit.

## Acknowledgment and required statements — author verification before submission

**Human-participant oversight and consent.** IEEE requires a statement naming the institutional oversight body or explaining why review was not conducted, and a statement about participant consent or why it was not obtained. The university determination and reviewer consent/process record were reported as confirmed but have not been inspected for this draft. Insert accurate wording from those records before submission. Do not invent an approval number.

**AI-assisted manuscript drafting.** This draft contains substantive text generated with OpenAI Codex under author direction and review. IEEE requires disclosure in acknowledgments identifying the AI system, the affected sections, and the level of use. Proposed text for author review: “OpenAI Codex assisted with initial prose drafting and organization across the manuscript. The authors verified the research records, analyses, citations, and final wording and take responsibility for the content.” Revise to describe the actual final workflow.

**Prior work.** Confirm whether the ICMLA version was published or merely accepted and withdrawn. If it was published, cite it and explicitly describe the changes in this paper; if it was only submitted, follow the venue's disclosure process for similar prior submissions. Do not copy its prose or figures into this manuscript without checking the relevant rights and novelty requirements.

## References (working list; format with IEEE bibliography style)

[1] T. Iqbal, M. Khan, K. Taveter, and N. Seyff, “Mining Reddit as a New Source for Software Requirements,” *Proc. IEEE RE*, pp. 128–138, 2021, doi: 10.1109/RE51729.2021.00019.

[2] B. Singh *et al*., “Enriching Release Notes with Reddit Feedback: Understanding How User Feedback Can Augment Maintaining Software Updates,” *Chronicle of Computing*, 2024, doi: 10.55432/978-1-6692-0007-9_7.

[3] H. Wang, P. Devine, J. Tizard, S. R. Shahamiri, and K. Blincoe, “Conversation in forums: How software forum posts discuss potential development insights,” *Journal of Systems and Software*, vol. 215, Art. no. 112108, 2024, doi: 10.1016/j.jss.2024.112108.

[4] O. Chaparro *et al*., “Detecting missing information in bug descriptions,” *Proc. ESEC/FSE*, pp. 396–407, 2017, doi: 10.1145/3106237.3106285.

[5] J. Tizard, H. Wang, L. Yohannes, and K. Blincoe, “Can a Conversation Paint a Picture? Mining Requirements In Software Forums,” *Proc. IEEE RE*, pp. 17–27, 2019, doi: 10.1109/RE.2019.00014.

[6] S. Hassan, C.-P. Bezemer, and A. E. Hassan, “Studying Bad Updates of Top Free-to-Download Apps in the Google Play Store,” *IEEE Transactions on Software Engineering*, vol. 46, pp. 773–793, 2020, doi: 10.1109/TSE.2018.2869395.

[7] L. Bo *et al*., “ChatBR: Automated assessment and improvement of bug report quality using ChatGPT,” *Proc. ASE*, pp. 1472–1483, 2024, doi: 10.1145/3691620.3695518.

[8] P. Devine, Y. S. Koh, and K. Blincoe, “Evaluating software user feedback classifier performance on unseen apps, datasets, and metadata,” *Empirical Software Engineering*, vol. 28, 2023, doi: 10.1007/s10664-022-10254-y.
