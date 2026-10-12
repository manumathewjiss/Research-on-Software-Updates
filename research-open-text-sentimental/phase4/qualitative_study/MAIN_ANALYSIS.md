# Intact-post qualitative study: first-pass analysis

**Status:** Descriptive intake and PI qualitative analysis of two submitted first passes. All 30 paired responses were inspected for action, cited evidence, uncertainty, and reasoning, and the bounded claims are mapped in `CLAIM_EVIDENCE_MATRIX.md`. This is not a manuscript draft. The private ethics/permission documentation remains to be archived. Pilot cases are excluded.

## Provenance and checks

- Both 30-row workbooks are archived unchanged in `main_submissions/`; hashes and validation are in `MAIN_INTAKE.json`.
- Every study ID, title, and body matches the frozen main packet exactly. All required answers are present and action/confidence values are valid.
- Manu reports that the two external reviewers completed separate first passes, did not see or discuss each other's answers before saving, and reported no guide confusion or outside lookup. Those process facts are user-reported; the files alone cannot establish them.
- No action is treated as a correct answer. The historical discussion label was hidden and is not a decision key.
- `ANALYST_ONLY_PAIRED_RESPONSES.csv` retains each original answer next to the other reviewer’s answer; it is analyst-only and must not be used as a reviewer packet.

## Descriptive decisions

Across the **30 purposefully selected cases**, the reviewers chose the same first action on **21** and different actions on **nine**. This is a descriptive count for two people and these cases, not a reliability estimate for a wider reviewer population.

| First action | Reviewer A | Reviewer B |
|---|---:|---:|
| A — open an update-focused investigation lead | 16 | 11 |
| B — ask a specific clarification first | 7 | 10 |
| C — monitor/group similar reports | 1 | 5 |
| D — no update-focused action | 5 | 4 |
| Cannot assess | 1 | 0 |

Ten cases received A from both reviewers (Q001, Q002, Q004, Q008, Q010, Q013, Q014, Q016, Q019, Q026). Six received B from both (Q006, Q011, Q015, Q017, Q024, Q029). One received C from both (Q020). Four received D from both (Q021, Q025, Q027, Q030). These are **sample observations**, not category prevalence.

## Evidence-to-action patterns, with limits

1. **Specific failures plus useful contrasts often supported immediate investigation in these cases.** Examples include the application comparison in Q001, multiple inaccessible Home Assistant pages in Q002, failed iPhone recovery attempts in Q010, graphics-path comparison in Q016, and the M365 channel change plus application breakage in Q026. Both reviewers chose A for these. The update is still a suspected connection, not established causality.

2. **A concrete symptom was not sufficient by itself when a key distinction remained unresolved.** Both reviewers chose B for the normal-versus-incognito Chrome crash (Q006), the uncertain ZFS space metric (Q011), the uncertain Kile update timing plus working clean VM (Q015), and the sparse WhatsApp lag report (Q024). Their questions target different missing facts that would change the next action. This is more informative than simply labeling fields present/absent.

3. **Already-solved or lower-severity posts exposed a threshold between investigation and monitoring.** In Q007 and Q012, Reviewer A chose A while Reviewer B chose C even though both cited essentially the same reported regression and workaround. In Q028, both noted concrete Chrome UI changes, but A would investigate and B would first group reports to distinguish intended design from a defect. Q020 elicited C from both for a visual change with uncertain intended behavior.

4. **Purpose classification did not dictate triage action.** Q026 was historically `other` but both reviewers chose A because the post reports application breakage after a channel change. Q023 and Q028 were historically `general_dissatisfaction` yet contain concrete changed behavior. Q023 yielded `cannot_assess` versus C; Q028 yielded A versus C. The sample cannot establish how often this occurs across the corpus.

5. **The same evidence could lead to different action thresholds.** In all nine action-disagreement cases, both reviewers identified overlapping or closely related evidence in the post. They usually differed about whether the evidence was *enough now* for A, whether one missing fact required B, or whether impact/scope made C more proportionate. The distinction is not simply that one reviewer noticed a version number and the other missed it.

## All nine action disagreements

| Case | A / B | What the explanations reveal |
|---|---|---|
| Q003 | A / B | Both cite the dark-screenshot contrast. A treats its specificity as enough for a lead; B wants to separate file content from HDR display behavior first. |
| Q005 | A / B | Both note the persistent microphone indicator. A weighs privacy concern and recurrence; B wants the active process identified first. |
| Q007 | A / C | Both recognize missing Firefox controls and the temporary workaround. A sees an actionable regression; B wants more reports to establish scope. |
| Q009 | A / B | Both see the build/update mismatch. A opens a lead; B wants the error code and update source first. |
| Q012 | A / C | Both cite autorotation after Fedora 44 and the reported driver workaround. A sees an upstream investigation lead; B sees a solved individual case to group and pass along. |
| Q018 | B / A | Both cite MySQL startup status and socket error. A notices the captured service status was only one second into startup and asks whether failure persisted; B treats the reported inaccessibility as sufficient to open a lead. |
| Q022 | D / B | Both understand this is prospective Fedora-upgrade advice. A sees no current incident to triage; B wants the details of earlier startup warnings before advising. |
| Q023 | Cannot assess / C | Both identify multiple concrete One UI changes. A cannot identify one main engineering target; B would group the reports despite the mixed complaints. Do not coerce A into an action. |
| Q028 | A / C | Both see changed tab placement and a seemingly ignored setting. A would investigate; B would first separate intentional UI changes from a reproducible fault through similar reports. |

## Contrary and negative cases

- **Technical detail does not automatically produce A.** Q011 gives a command and before/after space observations, yet both reviewers ask for a measurement clarification. Q015 gives a segmentation fault and a clean VM comparison, yet both ask for a version/trace distinction.
- **Emotional language does not automatically produce D.** Q028 contains strong dissatisfaction and concrete behavior; its two actions are A and C. Q023 likewise contains multiple specific symptoms, but its lack of one main target causes divergence.
- **Update discussion need not be a current fault.** Both reviewers chose D for Q021 (upgrade-strategy discussion), Q025 (positive update report), Q027 (preflight checklist), and Q030 (firmware-version question). These were selected contrasts, not a prevalence estimate.
- **A workaround can still leave an engineering lead.** Both reviewers chose A for Q019 (VS Code terminal workaround), while they split A/C on Q007 and Q012. A single “fix present” field cannot determine action.

## Conservative synthesis

The strongest supported finding is **a conditional account of first-pass reasoning**: reviewers used update timing and technical details alongside severity, comparisons, alternative causes, missing facts, prior fixes, and possible wider scope. The same cited evidence sometimes supported different actions because reviewers applied different thresholds for investigation, clarification, or monitoring. This connects the paper's post-purpose and diagnostic-field work to a realistic triage decision, but only for two reviewers and 30 deliberately varied snapshots.

We must **not** claim that a field caused an action, that either reviewer was correct, that these action frequencies estimate engineer behavior, or that the posts represent all Reddit update discussions. The study examines saved title/body snapshots; edits and comments may change a live decision. The reviewer descriptions and independence are user-reported; keep that provenance explicit.

## Remaining audit before manuscript writing

1. **Done:** All 30 paired rows were inspected for action, cited evidence, uncertainty, and reasoning, including contrary cases. `CLAIM_EVIDENCE_MATRIX.md` records the bounded claims and supporting cases. No separate follow-up appears necessary from the first-pass answers.
2. **Pending factual record:** Confirm the private project archive contains the actual institutional determination, text-sharing permission basis, reviewer qualifications, and consent/process record. Codex has only Manu's confirmation, not those documents.
3. **Done:** The cross-phase evidence lock is in `FINAL_EVIDENCE_LOCK.md`. Resolve the private documentation item, then begin manuscript writing.
