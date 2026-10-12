# Beyond Troubleshooting Detection: Diagnostic Evidence and First-Pass Engineering Decisions in Reddit Software Update Discussions

**Manu Mathew Jiss and Solomon Berhe**  
University of the Pacific, School of Engineering and Computer Science  
**Working full-paper draft, 8 October 2026. Not submission-ready.**

## Abstract

Informal discussions after software updates mix fault reports with advice, reactions, and general conversation. A model that finds a technical post does not establish what an engineer can do with it. We examine this gap by connecting discussion-purpose classification, observable diagnostic information, and first-pass engineering decisions in Reddit software update discussions. The study combines a collection of 3,362 posts with classifier evaluation, diagnostic coding, and an exploratory case study involving two independent software-engineering reviewers. Within human-established software-update scope, a title-and-body TF-IDF logistic-regression classifier achieved macro-F1 0.792 on a fresh test, outperforming majority and fixed-keyword baselines. This evaluation followed an earlier reserved test and used the same selected configuration fitted on revised development data. The smaller other-update class remained harder to classify. Diagnostic coding showed that many troubleshooting posts lacked visible reproduction context or error evidence. In 30 purposefully selected cases, reviewers sometimes cited similar facts but chose different actions, including investigation, clarification, and monitoring. Their explanations exposed differing judgments about whether the available evidence justified acting immediately or required further information. These observations are exploratory and do not establish causal effects, population-wide decision patterns, or downstream engineering benefits. Together, the findings distinguish identifying a post’s purpose from interpreting its implications: purpose detection can organize discussions, while first-pass engineering decisions also reflect the available diagnostic evidence and reviewers’ judgments about its sufficiency.

**Index Terms:** software updates, social-media mining, troubleshooting, software engineering, triage, diagnostic evidence

## I. Introduction

Software updates generate feedback about failures, changed behavior, and unmet expectations. Studies of problematic application updates demonstrate the value of examining user feedback after release [1]. However, collecting feedback is only part of the problem. In interviews across product-development companies, Tkalich et al. [2] found continuing difficulties with interpreting feedback and using it in decisions. Reddit and software forums provide additional places where users describe problems outside formal issue-reporting workflows [3], [4]. A post may report a crash, ask whether an upgrade caused a failure, criticize a design change, or discuss a forthcoming release. These messages share vocabulary while serving different purposes.

A useful distinction is between recognizing troubleshooting and interpreting what to do next. Consider two illustrative reports: one says an application stopped working after an update; another also describes the affected version, a working comparison, and a failed remedy. Both can express troubleshooting, while offering different grounds for investigation or clarification. Even when two readers notice the same facts, they may differ about whether to open a lead immediately, ask a question, or monitor similar reports. Here, *first-pass engineering decisions* means this initial response to a saved post, before reproducing the failure or establishing its cause.

Prior work already classifies software feedback [3], analyzes diagnostic information in reports [5], and uses external evidence to generate issue specifications [6]. Our contribution concerns the relationship between these stages in informal update discussion: what a purpose classifier identifies, what evidence remains visible, and how reviewers explain an initial response to that evidence. This is an empirical question about interpreting natural-language reports. A positive troubleshooting label alone does not specify the sufficiency of the information for a particular next action. A recent mapping study likewise identifies practitioner involvement and evaluation beyond prediction accuracy as recurring gaps in issue classification [7].

We investigate three research questions. **RQ1:** Within posts already judged to concern software and an update, how well can title and body text distinguish troubleshooting from other update discussion? **RQ2:** Which diagnostic facts are visible in a reviewed sample of troubleshooting posts? **RQ3:** How do two software-engineering reviewers use those facts when selecting first-pass engineering decisions for intact posts?

The study combines a reviewed candidate collection, a fixed text-classification evaluation, diagnostic coding, and an exploratory multiple-case study. Its contributions are: (1) an explicit conditional purpose-classification task with documented review and evaluation boundaries; (2) an evaluation on previously unseen IDs, accompanied by a descriptive account of observable diagnostic fields; and (3) a case-based analysis of where reviewers' first actions converge or diverge despite citing similar evidence. The semantic contribution is this account of how textual evidence supports different interpretations and response choices. The classifier supplies the first stage of the investigation; the case study does not evaluate a classifier-assisted workflow or establish a causal effect of diagnostic fields.

## II. Related Work

### A. Software feedback in Reddit and community forums

Iqbal et al. [3] examined Reddit as a requirements source and classified posts as bug reports, feature-related feedback, or irrelevant material. Tizard et al. [8] studied requirements information in software forums. Wang et al. [4] later showed that post-level context reveals feedback types and contextual information that sentence-level analysis can miss. These studies establish both the value of community feedback and the need to preserve its context. Our classifier uses the saved title and body, and the qualitative study keeps each post intact. Its target is troubleshooting purpose conditional on an explicit update connection, rather than general requirements relevance.

Recent Reddit research also extends beyond technical fault detection. Zegers et al. [9] investigated software accountability concerns across software-focused communities, including concerns with technical and nontechnical consequences. This supports keeping dissatisfaction distinct from a blanket nontechnical category. Singh et al. [10] studied how Reddit feedback can enrich release notes for update-impact analysis and prioritization. That separate project addresses a related domain with a different unit and outcome: our study neither joins release notes nor evaluates update-impact rankings. We instead ask how individual update-linked posts express troubleshooting and inform an initial response.

### B. Diagnostic information and report quality

Bettenburg et al. [11] documented a mismatch between information developers value and what reporters supply, including reproduction steps and stack traces. Soltani et al. [12] combined developer interviews, a survey, and repository analysis to examine the significance of bug-report elements. Their findings caution against interpreting all fields as equally important. Chaparro et al. [5] studied and detected missing information in bug descriptions. More recently, Wang et al. [13] analyzed initial and final versions of web-application bug reports and found that usage information and diagnostic suggestions can emerge later in a report's lifetime.

These studies provide the basis for treating the saved snapshot as a limited observation. A field absent from our title/body snapshot might appear later or in a comment. Our diagnostic analysis reports field visibility, not an overall quality score. It also differs from ChatBR [14], which detects missing report components and generates candidate additions using ChatGPT. We do not generate missing incident facts. Instead, the human study asks which observed facts and unresolved questions reviewers cite when deciding whether to investigate, request clarification, monitor, or take no update-focused action.

### C. Connecting feedback with engineering work

Several studies evaluate steps beyond classification. Tang et al. [15] matched app reviews with historical bug reports to guide reproduction and reported newly identified bugs to development teams. Laiq et al. [16] studied industrial adoption of invalid-report detection, identifying trust, tool integration, and maintenance of accuracy as practical concerns. These outcomes are stronger evidence of engineering utility than our offline classifier or exploratory reviewer decisions; we therefore do not infer productivity or resolution benefits from our scores.

Two recent studies are especially close to the present framing. Wang et al. [6] proposed an agent-governed retrieval and generation framework that checks evidence sufficiency and produces issue specifications for Firefox and VS Code. K C and Hosseini [17] examined how Moodle forum feature requests connect to issue-tracker records, combining trace-link analysis with stakeholder interviews. Evidence sufficiency and the movement from conversation to engineering work are thus established research concerns. Our specific contribution is a bounded study of first-pass judgments on intact update-linked posts, with paired explanations that expose both agreement and contrasting action choices. It complements work on generated specifications and cross-channel handoffs without claiming a new general theory of triage.

### D. Classification evidence and study boundaries

Devine et al. [18] found that feedback classifiers can behave differently on unseen datasets than on unseen applications within a dataset. Laiq and Dobslaw's mapping study [7] further emphasizes generalizability and practitioner involvement alongside accuracy. We consequently report a protected unseen-ID evaluation separately from development comparisons and do not compare our F1 directly with scores from other papers using different labels or samples. The small human study addresses a separate interpretation question; it does not validate the classifier's effect on reviewers. Across these bodies of work, our distinguishing element is the joint examination of purpose, observed diagnostic evidence, and the reasoning behind first-pass engineering decisions in the software-update setting.

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

Exact and highly similar title/body records were grouped for a subsequent development check so they would not straddle validation folds. Additional development-only analyses restricted the data to Reddit URLs and examined class balancing. A frozen MiniLM sentence-embedding representation, implemented within the Sentence-BERT framework [19], plus logistic regression was evaluated on the same 2,136 audited Reddit-only development posts as a TF-IDF comparator. Its macro-F1 was 0.844 versus 0.839 for TF-IDF; the paired difference was approximately +0.006 with a 95% interval of −0.016 to +0.029. This does not provide reliable evidence that the more complex representation is better. Neither protected test was used to choose the embedding comparator.

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

## References

[1] S. Hassan, C.-P. Bezemer, and A. E. Hassan, “Studying Bad Updates of Top Free-to-Download Apps in the Google Play Store,” *IEEE Transactions on Software Engineering*, vol. 46, pp. 773–793, 2020, doi: [10.1109/TSE.2018.2869395](https://doi.org/10.1109/TSE.2018.2869395).

[2] A. Tkalich, E. Klotins, T. Sporsem, V. Stray, N. B. Moe, and A. Barbala, “User feedback in continuous software engineering: revealing the state-of-practice,” *Empirical Software Engineering*, vol. 30, Art. no. 79, 2025, doi: [10.1007/s10664-024-10557-2](https://doi.org/10.1007/s10664-024-10557-2).

[3] T. Iqbal, M. Khan, K. Taveter, and N. Seyff, “Mining Reddit as a New Source for Software Requirements,” *Proc. IEEE RE*, pp. 128–138, 2021, doi: [10.1109/RE51729.2021.00019](https://doi.org/10.1109/RE51729.2021.00019).

[4] H. Wang, P. Devine, J. Tizard, S. R. Shahamiri, and K. Blincoe, “Conversation in forums: How software forum posts discuss potential development insights,” *Journal of Systems and Software*, vol. 215, Art. no. 112108, 2024, doi: [10.1016/j.jss.2024.112108](https://doi.org/10.1016/j.jss.2024.112108).

[5] O. Chaparro *et al*., “Detecting missing information in bug descriptions,” *Proc. ESEC/FSE*, pp. 396–407, 2017, doi: [10.1145/3106237.3106285](https://doi.org/10.1145/3106237.3106285).

[6] Z. Wang, J. Li, X. Guo, and T. Tsuchiya, “From noisy feedback to evidence-aware issue specifications: an agent-governed retrieval-augmented generation approach,” *Automated Software Engineering*, vol. 33, Art. no. 103, 2026, doi: [10.1007/s10515-026-00640-x](https://doi.org/10.1007/s10515-026-00640-x).

[7] M. Laiq and F. Dobslaw, “Automatic techniques for issue report classification: A systematic mapping study,” *Automated Software Engineering*, vol. 33, Art. no. 72, 2026, doi: [10.1007/s10515-026-00616-x](https://doi.org/10.1007/s10515-026-00616-x).

[8] J. Tizard, H. Wang, L. Yohannes, and K. Blincoe, “Can a Conversation Paint a Picture? Mining Requirements In Software Forums,” *Proc. IEEE RE*, pp. 17–27, 2019, doi: [10.1109/RE.2019.00014](https://doi.org/10.1109/RE.2019.00014).

[9] A. Zegers, N. Preciado, J. Duchnowski, F. Madeiral, and E. Guzmán, “Irresponsibility Killed the Cat: Software Accountability Concerns,” *Proc. IEEE/ACM CHASE*, pp. 131–142, 2025, doi: [10.1109/CHASE66643.2025.00024](https://doi.org/10.1109/CHASE66643.2025.00024).

[10] B. Singh *et al*., “Enriching Release Notes with Reddit Feedback: Understanding How User Feedback Can Augment Maintaining Software Updates,” *Chronicle of Computing*, 2024, doi: [10.55432/978-1-6692-0007-9_7](https://doi.org/10.55432/978-1-6692-0007-9_7).

[11] N. Bettenburg, S. Just, A. Schröter, C. Weiss, R. Premraj, and T. Zimmermann, “What makes a good bug report?,” *Proc. ACM SIGSOFT FSE*, pp. 308–318, 2008, doi: [10.1145/1453101.1453146](https://doi.org/10.1145/1453101.1453146).

[12] M. Soltani, F. Hermans, and T. Bäck, “The significance of bug report elements,” *Empirical Software Engineering*, vol. 25, pp. 5255–5294, 2020, doi: [10.1007/s10664-020-09882-z](https://doi.org/10.1007/s10664-020-09882-z).

[13] D. Wang, M. Galster, and M. Morales-Trujillo, “Information needs in bug reports for web applications,” *Journal of Systems and Software*, vol. 219, Art. no. 112230, 2025, doi: [10.1016/j.jss.2024.112230](https://doi.org/10.1016/j.jss.2024.112230).

[14] L. Bo *et al*., “ChatBR: Automated assessment and improvement of bug report quality using ChatGPT,” *Proc. ASE*, pp. 1472–1483, 2024, doi: [10.1145/3691620.3695518](https://doi.org/10.1145/3691620.3695518).

[15] X. Tang et al., “App review driven collaborative bug finding,” *Empirical Software Engineering*, vol. 29, Art. no. 124, 2024, doi: [10.1007/s10664-024-10489-x](https://doi.org/10.1007/s10664-024-10489-x).

[16] M. Laiq, N. bin Ali, J. Börstler, and E. Engström, “Industrial adoption of machine learning techniques for early identification of invalid bug reports,” *Empirical Software Engineering*, vol. 29, Art. no. 130, 2024, doi: [10.1007/s10664-024-10502-3](https://doi.org/10.1007/s10664-024-10502-3).

[17] P. K C and M. Bokaei Hosseini, “From Community Forums to Issue Trackers: A Moodle Case Study,” arXiv:2606.20876, 2026. Author manuscript reports acceptance at IEEE RE 2026. doi: [10.48550/arXiv.2606.20876](https://doi.org/10.48550/arXiv.2606.20876).

[18] P. Devine, Y. S. Koh, and K. Blincoe, “Evaluating software user feedback classifier performance on unseen apps, datasets, and metadata,” *Empirical Software Engineering*, vol. 28, 2023, doi: [10.1007/s10664-022-10254-y](https://doi.org/10.1007/s10664-022-10254-y).

[19] N. Reimers and I. Gurevych, “Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks,” *Proc. EMNLP-IJCNLP*, pp. 3980–3990, 2019, doi: [10.18653/v1/D19-1410](https://doi.org/10.18653/v1/D19-1410).
