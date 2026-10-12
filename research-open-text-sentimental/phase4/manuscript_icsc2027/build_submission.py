from pathlib import Path
import json,re,csv,hashlib,shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
import numpy as np
R=Path(__file__).resolve().parents[2]; P=Path(__file__).resolve().parent; O=P/'overleaf'; O.mkdir(exist_ok=True)
D=json.loads((R/'phase3/diagnostic_results/analysis.json').read_text())
V=json.loads((R/'phase3/icsc_full_paper/RESULT_VERSION_RECONCILIATION.json').read_text())
rows=list(csv.DictReader((R/'phase4/qualitative_study/ANALYST_ONLY_PAIRED_RESPONSES.csv').open()))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'pdf.fonttype':42,'ps.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
# All diagrams use saved records; no predictions are generated.
fig,ax=plt.subplots(figsize=(7.12,2.12));ax.set(xlim=(0,10),ylim=(-.12,2.87));ax.axis('off')
def box(x,y,w,h,s,color='#edf2f6'):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.04,rounding_size=0.07',lw=.65,edgecolor='#3c5060',facecolor=color));ax.text(x+w/2,y+h/2,s,ha='center',va='center',fontsize=7.6)
def arrow(a,b):ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=9,lw=.7,color='#3c5060'))
box(.05,1.05,2.15,1,'Reviewed collection\n3,362 unique records\n542 historical + 2,820 new')
box(2.8,1.85,3.15,.85,'Purpose classification\nOriginal fit: 2,084 → reserved: 159\nRevised fit: 2,080 → fresh: 344')
box(2.8,.83,3.15,.78,'Diagnostic coding\n250 sampled → 237 reconfirmed\nEight observable fields')
box(2.8,-.02,3.15,.66,'Intact-post case study\n6 pilot + 30 main; 2 reviewers')
box(6.6,1.86,3.1,.82,'RQ1: Detect discussion purpose\nConditional software/update scope')
box(6.6,.83,3.1,.78,'RQ2: Describe visible evidence\nSnapshot presence, not utility')
box(6.6,-.02,3.1,.66,'RQ3: Explain initial action choices\nExploratory; no causal intervention')
for y in (2.27,1.22,.31):arrow((2.2,1.55),(2.75,y));arrow((5.98,y),(6.55,y))
fig.subplots_adjust(left=.005,right=.995,top=.995,bottom=.045);fig.savefig(O/'study_flow.pdf');fig.savefig(O/'study_flow.png',dpi=240);plt.close(fig)
# Diagnostic prevalence with existing Wilson intervals.
fields=D['conditional_field_rates']; keys=list(fields)
labels=['Software product','Identifiable release','Environment','Specific symptom','Reproduction context','Error evidence','Attempted remedy','Explicit help request']
rates=np.array([fields[k]['rate']*100 for k in keys]); ci=np.array([fields[k]['wilson_95'] for k in keys])*100
fig,ax=plt.subplots(figsize=(3.45,2.5));y=np.arange(8)
ax.barh(y,rates,color=['#738f9b']*4+['#24566d','#24566d','#738f9b','#738f9b'],height=.60)
ax.errorbar(rates,y,xerr=[rates-ci[:,0],ci[:,1]-rates],fmt='none',ecolor='#252525',capsize=2,lw=.75)
ax.set_yticks(y,labels,fontsize=7);ax.invert_yaxis();ax.set_xlim(0,118);ax.set_xticks([0,25,50,75,100]);ax.set_xlabel('Present in saved title/body (%)',fontsize=7.5);ax.spines[['top','right','left']].set_visible(False);ax.tick_params(axis='y',length=0)
for i,k in enumerate(keys):ax.text(116,i,str(fields[k]['present']),va='center',ha='right',fontsize=7)
fig.subplots_adjust(left=.37,right=.98,top=.98,bottom=.19);fig.savefig(O/'diagnostic_evidence.pdf');fig.savefig(O/'diagnostic_evidence.png',dpi=240);plt.close(fig)
# Pairwise descriptive decisions.
actions=['A','B','C','D','cannot_assess']; m=np.zeros((5,5),dtype=int)
for row in rows:m[actions.index(row['reviewer_a_action']),actions.index(row['reviewer_b_action'])]+=1
assert m.sum()==30 and np.trace(m)==21
fig,ax=plt.subplots(figsize=(3.4,2.6));ax.imshow(m,cmap='Blues',vmin=0,vmax=10)
for i in range(5):
 for j in range(5):ax.text(j,i,str(m[i,j]),ha='center',va='center',color='white' if m[i,j]>5 else '#202020',fontsize=9)
lab=['Investigate','Clarify','Monitor','No action','Cannot\nassess'];ax.set_xticks(range(5),lab,rotation=35,ha='right',fontsize=7);ax.set_yticks(range(5),lab,fontsize=7);ax.set_xlabel('Reviewer B',fontsize=8);ax.set_ylabel('Reviewer A',fontsize=8);ax.tick_params(length=0);fig.subplots_adjust(left=.25,right=.96,top=.98,bottom=.31);fig.savefig(O/'reviewer_actions.pdf');fig.savefig(O/'reviewer_actions.png',dpi=240);plt.close(fig)
# Preserve approved abstract and the expanded literature wording.
md=(P/'DRAFT_V2.md').read_text(); sections={}
parts=re.split(r'^## ',md,flags=re.M)
for part in parts[1:]:
 heading,_,s=part.partition('\n');sections[heading]=s.strip()
keys_bib=['Hassan2020BadUpdates','Tkalich2025Feedback','Iqbal2021Reddit','Wang2024Forums','Chaparro2017Missing','Wang2026Evidence','Laiq2026Mapping','Tizard2019Forums','Zegers2025Accountability','Singh2024ReleaseNotes','Bettenburg2008GoodReport','Soltani2020Elements','Wang2025InformationNeeds','Bo2024ChatBR','Tang2024ReviewBugs','Laiq2024Industrial','KC2026Moodle','Devine2023Transfer','Reimers2019SBERT']
def tex(s):
 s=s.replace('—','---').replace('–','--').replace('’',"'").replace('“','``').replace('”',"''").replace('≈',r'$\approx$').replace('≥',r'$\geq$')
 for x,y in [('&',r'\&'),('%',r'\%'),('_',r'\_')]:s=s.replace(x,y)
 s=re.sub(r'\[(\d+)\]',lambda m:r'\cite{'+keys_bib[int(m[1])-1]+'}',s)
 s=re.sub(r'\*\*(.+?)\*\*',r'\\textbf{\1}',s);s=re.sub(r'\*(.+?)\*',r'\\emph{\1}',s);s=re.sub(r'`([^`]+)`',r'\\texttt{\1}',s)
 s=re.sub(r'^### [A-D]\. (.+)$',r'\\subsection{\1}',s,flags=re.M)
 return s
preamble=r'''\documentclass[conference,letterpaper]{IEEEtran}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{cite}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs,tabularx,array}
\usepackage{xcolor}
\usepackage[hidelinks]{hyperref}
\newcommand{\authorcheck}[1]{\par\noindent\textcolor{red}{\textbf{Author confirmation required:} #1}\par}
\newcolumntype{L}{>{\raggedright\arraybackslash}X}
\title{Beyond Troubleshooting Detection: Diagnostic Evidence and First-Pass Engineering Decisions in Reddit Software Update Discussions}
\author{\IEEEauthorblockN{Manu Mathew Jiss and Solomon Berhe}
\IEEEauthorblockA{School of Engineering and Computer Science\\
University of the Pacific, Stockton, California, USA\\
m\_jiss@u.pacific.edu, sberhe@pacific.edu}}
\begin{document}
\maketitle
\begin{abstract}
'''
abstract=sections['Abstract'].split('**Index Terms:**')[0].strip()
main=preamble+tex(abstract)+r'''
\end{abstract}
\begin{IEEEkeywords}
software updates, Reddit, troubleshooting, diagnostic evidence, engineering triage
\end{IEEEkeywords}
\section{Introduction}
'''+tex(sections['I. Introduction'])+r'''
\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{study_flow.pdf}
\caption{Study organization and distinct evidence roles. The fresh test was sampled separately from unseen IDs outside the combined collection. Diagnostic and qualitative studies use development posts; they are not additional test sets. Arrows describe research questions, not an evaluated automated triage pipeline.}
\label{fig:flow}
\end{figure*}
\section{Related Work}
'''+tex(sections['II. Related Work'])
main+=r'''
\section{Collection, Review, and Study Population}
\subsection{Candidate collection and target}
The research collection contains 3,362 unique records: 542 historical posts and 2,820 additional records from ReleaseTrain's technical-problem-solving (\texttt{tps}) and general-discussion (\texttt{gds}) candidate routes after ID overlap removal. The routes supplied candidate pools, not reference labels. These keyword-selected records do not constitute a random sample of Reddit. Thirty records have inconsistent source metadata: the investigators identify them as Reddit records with a source-labeling error, while the archived URLs indicate another platform. Historical fits retain them; separate URL-restricted development checks exclude them. We retain this provenance limitation rather than silently rewriting the evaluated populations.

Review separated three decisions: whether the text concerns software, whether it connects to an update, and its main discussion purpose. An update connection includes an author explicitly stating, suspecting, or asking whether an update, patch, release, or upgrade caused or affected a problem; it does not establish causality. Troubleshooting includes a concrete software malfunction or an attempt to understand or fix it, even without an explicit help question. General dissatisfaction expresses an unfavorable reaction; \emph{other} includes discussion that is neither troubleshooting nor dissatisfaction. Concrete malfunction reports can contain emotional language without losing their technical purpose.

The binary modeling population, denoted S2 in the records, requires software-related and update-related decisions of yes. Its positive class is troubleshooting. Its negative class combines general dissatisfaction and other update discussion. We call the latter \emph{other update}, rather than treating every negative as dissatisfaction. Scope is provided by review, not predicted by the classifier.

\subsection{Annotation provenance and version control}
Review proceeded in batches using explicit scope and purpose rules. Provenance includes machine-proposed decisions subsequently reviewed by an author and jointly completed human review; it is not independent double annotation of the entire corpus. Five combined records remained unresolved and were excluded from supervised experiments. A later, deliberately stratified 200-post development check had matching categorical answers across reported separate first passes. Agreement in that selected check does not establish correctness of the master labels or validate its full provenance. Subsequent diagnostic and scope checks also exposed disagreements with earlier labels.

We therefore preserve historical labels, test results, and training snapshots. Revised development labels support separately identified sensitivity analyses. We do not transfer a later training-set count to an earlier result or retroactively repair test labels to increase performance. Figure~\ref{fig:flow} distinguishes the studies; Table~\ref{tab:data} separates the main classifier populations.

\begin{table}[t]
\caption{Populations used for purpose classification}
\label{tab:data}\centering\footnotesize
\begin{tabularx}{\columnwidth}{Lrrr}
\toprule
Population & Total & Trouble & Other\\\midrule
Original development fit & 2,084 & 1,689 & 395\\
Reserved test & 159 & 135 & 24\\
Revised development fit & 2,080 & 1,686 & 394\\
Fresh test & 344 & 277 & 67\\\bottomrule
\end{tabularx}
\end{table}

\subsection{Reserved and fresh evaluations}
An initial model-selection experiment used 2,084 eligible development posts and 159 eligible cases from a 200-post reserved review set. After development-label repairs, the selected specification and threshold were fitted on a revised population of 2,080 posts for a separate fresh evaluation. The reserved and fresh reference decisions were jointly reviewed; they do not supply independent annotator-agreement estimates.

For the fresh evaluation, an update-related API candidate route returned 3,718 unique records. Removing 2,842 IDs already in the master left 876; excluding 12 near-identical text matches left 864. From sorted IDs, 500 were sampled without replacement using seed 20261007, before consulting classifier outputs. Joint review retained 344 S2 cases. The original 500 spanned 66 communities, but only 45 were dated October 5, 2026 or later. Accordingly, this is an \emph{unseen-ID} test, not a wholly prospective temporal test. Its sampling frame remains an API-filtered candidate pool.

\section{Purpose Classification}
\subsection{Models and model selection}
We compared a majority rule, a fixed troubleshooting-keyword rule, TF-IDF logistic regression, and a linear support-vector machine (SVM), each using title-only or title-plus-body input. The majority rule predicts troubleshooting. The keyword rule uses predefined malfunction, assistance, and recovery cues, including crash, error, inability to start, workaround, and rollback. Source route, community, timestamps, review fields, and model-generated labels are not predictors. Comments are excluded; an absent body contributes no text.

Preprocessing removes URLs, collapses whitespace, and lowercases the saved text. TF-IDF uses word unigrams and bigrams, a minimum document frequency of two, at most 20,000 features, and sublinear term frequency. The vectorizer is fitted on each training fold only. Logistic regression uses balanced class weights, the liblinear solver, and at most 2,000 iterations. Both learned models were tested with $C\in\{0.25,1,4\}$ using common stratified five-fold splits (seed 42). Selection used pooled out-of-fold macro-F1, with troubleshooting F1 and recall as tie-breakers.

The selected model was title-plus-body logistic regression with $C=4$. Its probability threshold, 0.5877, was chosen on development predictions by comparing the default cutoff with 37 score quantiles from 0.05 to 0.95. This development selection is not an unbiased final performance estimate. The specification and cutoff were fixed before reserved testing and retained for the revised fit used on the fresh test.

\subsection{Duplicate controls and sensitivity analyses}
Before evaluation, exact matches to reserved records were removed from development, and two further development cases were excluded for title/body character-five-gram Jaccard similarity of at least 0.92 to reserved cases. The fresh sample applied the same near-duplicate threshold against the existing collection. Subsequent grouped validation kept exact and high-similarity development records together. The original selection used stratified folds, so grouped validation is a robustness check rather than a retrospective claim that selection had used groups.

Additional development-only analyses restricted records by Reddit URL, compared balanced weights with no weights and random oversampling, and examined a frozen \texttt{all-MiniLM-L6-v2} embedding using the Sentence-BERT framework~\cite{Reimers2019SBERT}. The embedding comparison used the same saved outer folds on 2,136 audited Reddit-URL development records. Each training split selected its threshold with three inner grouped folds over 0.20--0.80 in increments of 0.05. The embedding head used balanced logistic regression with $C=1$; the lexical comparator used $C=4$. The encoder was not fine-tuned. Neither test set selected the comparator or its threshold.

\subsection{Metrics and uncertainty}
Macro-F1 is the mean of the two class F1 scores, giving the smaller class equal weight. We also report class precision, recall, F1, and confusion counts. Saved 95\% percentile intervals use 1,000 bootstrap resamples of evaluated posts. Paired model comparisons resample the same posts for both models. These intervals capture sampling variability conditional on the fixed labels and predictions; they do not incorporate uncertainty about annotation, collection bias, or model selection.

\subsection{Protected-test results}
Table~\ref{tab:test} reports each test with its own fit history. The reserved macro-F1 was 0.863. The revised fit reached 0.792 on the fresh sample (95\% interval 0.731--0.845), versus 0.446 for the majority rule and 0.474 for keywords. This supports usable text signal within reviewed software-update scope. It does not establish end-to-end discovery in an unfiltered Reddit stream.

\begin{table}[t]
\caption{Protected-test F1 scores; separate fits and samples}
\label{tab:test}\centering\footnotesize
\begin{tabularx}{\columnwidth}{Lrrr}
\toprule
Test / model & Macro & Other & Trouble\\\midrule
Reserved / selected TF-IDF LR & .863 & .766 & .959\\
Fresh / revised TF-IDF LR & .792 & .667 & .916\\
Fresh / majority & .446 & .000 & .892\\
Fresh / fixed keywords & .474 & .396 & .552\\\bottomrule
\end{tabularx}
\end{table}

On the fresh test, 46 of 67 other-update posts were correctly classified and 21 were false troubleshooting alarms; 252 of 277 troubleshooting posts were detected and 25 were missed. Other-update precision/recall were 0.687/0.687; troubleshooting precision/recall were 0.923/0.910. The smaller class remains the harder target, with only 67 supporting cases. The lower fresh score cannot be attributed to a single source of drift because both the fitted development population and the test population changed. Exploratory inspection of the 46 errors suggested mixed-purpose text and limited context, but these explanations were not independently validated as an error taxonomy.

\subsection{What the development checks establish}
Grouping similar records yielded macro-F1 0.835 on the 2,080-post revised population. The URL-restricted 2,050-post check scored 0.836, compared with 0.447 for majority and 0.657 for keywords. Removing records rebuilt the folds, so the small cross-snapshot difference is not a paired improvement. On those same restricted folds, random oversampling scored 0.838 versus 0.836 for balanced weights at the fixed cutoff; the paired interval for the difference included zero. Threshold adjustment on development predictions brought the balancing alternatives close together.

On the later 2,136-post audited population, the fair inner-threshold comparison gave macro-F1 0.839 for TF-IDF and 0.844 for MiniLM. The paired difference was +0.006 (95\% interval $[-0.016,0.029]$). MiniLM was higher in one nondominant source pool and lower in another. Its 256-word-piece limit truncated 512 posts (24\%). These results do not establish a reliable overall benefit from the frozen semantic representation. All checks are development evidence and do not replace the protected test results.

\section{Observable Diagnostic Evidence}
\subsection{Sample and coding}
A simple random sample of 250 posts was drawn before coding from the then-current 1,658 Reddit-URL troubleshooting development records. A 50-post feasibility exercise and a 15-post rule check preceded the final diagnostic guide. Under that guide, the authors jointly reviewed saved title/body text and first reconfirmed troubleshooting: 237 yes, four no, and nine unclear. Field summaries are conditional on the 237 confirmed cases. The other 13 remain in the historical classifier snapshot; their diagnostic exclusion does not retroactively change the tested labels.

Eight fields were coded as present, not observed, or unclear: software product, identifiable release, environment, specific symptom, reproduction context, error evidence, attempted remedy, and explicit help request. An identifiable release requires a version, build, named release, or unambiguous cycle; ``latest update'' alone is insufficient. Reproduction context requires an action or condition associated with the failure, not timing alone. Error evidence requires a specific message, code, log, trace, or described diagnostic output. An unavailable linked image can make this field unclear. A remedy must have actually been attempted. No overall usefulness score was assigned.

\begin{figure}[t]
\centering\includegraphics[width=\columnwidth]{diagnostic_evidence.pdf}
\caption{Visible diagnostic fields among 237 reconfirmed troubleshooting snapshots. Error bars are saved 95\% Wilson intervals; numbers at right are present counts. Not present includes unobserved or unclear evidence, not proof of absence from the incident.}
\label{fig:diagnostic}
\end{figure}

\subsection{Findings and relation to classification}
Figure~\ref{fig:diagnostic} shows that software product was usually visible (218/237), whereas error evidence (40/237, 16.9\%) and reproduction context (108/237, 45.6\%) were less common. Seven error-evidence decisions were unclear; these are not converted to confirmed absence. Identifiable release was visible in 122 posts, environment in 137, an attempted remedy in 118, and a help request in 168. The 100\% symptom rate partly reflects reconfirming troubleshooting and is not an independent discovery.

Twenty confirmed cases had no saved body. Reproduction context appeared in two of these versus 106 of 217 with a body; an attempted remedy appeared in two versus 116. A post lacking saved text should therefore not automatically be interpreted as an uninformative original report. Nine confirmed cases also occurred in the earlier feasibility pilot by chance; excluding them changes the descriptive field rates only slightly.

Joining the 237 cases to grouped out-of-fold development predictions found 16 troubleshooting misses: eight among the 20 title-only cases and eight among the 217 with bodies. Reproduction context was present in three of the missed cases. These small, overlapping descriptive comparisons suggest text availability matters, but they are not preselected causal tests. They concern development predictions, not diagnostic annotations of the fresh test. Joint coding provides no independent field-level reliability estimate.

\section{First-Pass Engineering Decisions}
\subsection{Design, selection, and reviewer task}
We conducted an exploratory intact-post multiple-case study with two external reviewers with software-engineering knowledge. Thirty main cases were purposefully selected from reviewed development records, excluding reserved and fresh-test IDs and duplicate matches. The cases span 18 communities, at most three cases per community, and varied symptoms, update situations, comparison evidence, remedies, and uncertainty. Historical categories comprised 20 troubleshooting, four dissatisfaction, and six other posts. These labels guided diversity, not expected actions. Six separate pilot cases tested the instructions; no confusion was reported and the guide was retained. Pilot responses are excluded from main results.

Each reviewer received the same intact title/body snapshots in a different order, with historical labels and selection reasons hidden. The guide prohibited live lookup, comments, and discussion before both first passes were saved. It instructed reviewers to focus on the author's main request when multiple changes appeared, judge the entire saved snapshot including reported fixes, and avoid equating emotional language with lack of technical evidence. The coordinator reports that the reviewers followed independent first passes without outside lookup.

For each post, reviewers chose one first action: (A) open an update-focused investigation lead, (B) ask a specific clarification first, (C) monitor or group similar reports, (D) take no update-focused action, or cannot assess. A does not assert that the update caused the problem. Reviewers identified the most influential fact, explained their choice over the closest alternative, stated uncertainty, proposed one question and how its answer could affect the next action, and recorded confidence. No correct-action key was provided.

\subsection{Analysis procedure}
The two submitted workbooks were preserved unchanged and joined by case ID. All 30 paired responses were examined for selected action, cited evidence, uncertainty, and reasoning. A cross-case evidence matrix recorded converging explanations, differing action thresholds, counterexamples, and negative cases. We retained disagreements rather than adjudicating them into one label. Counts describe these cases only; we do not infer population frequencies or claim thematic saturation. This is an investigator synthesis supported by the response record, not a separately validated multi-coder thematic analysis.

\begin{figure}[t]
\centering\includegraphics[width=\columnwidth]{reviewer_actions.pdf}
\caption{Paired first actions for 30 purposefully selected cases. Diagonal counts total 21 agreements; nine cases differ. This is descriptive concordance, not decision accuracy or a population estimate.}
\label{fig:actions}
\end{figure}

\subsection{Convergence, disagreement, and negative cases}
The reviewers chose the same first action in 21 cases and different actions in nine (Fig.~\ref{fig:actions}). Both chose investigation in ten cases, clarification in six, monitoring in one, and no action in four. Reviewer A selected investigation 16 times and Reviewer B 11 times; B selected monitoring five times versus A's one. These differences motivate examination of explanations, not a claim that either reviewer was better calibrated.

\textbf{Concrete evidence can support a lead without resolving causality.} Both reviewers chose investigation for a post describing two affected applications and an unaffected comparison after an OS upgrade. They also agreed for a report of several inaccessible home-automation pages, including backups. Their reasons treated specificity and recovery impact as grounds to investigate while leaving the cause open.

\textbf{A missing distinction can matter more than the amount of detail.} Both reviewers requested clarification for a Chrome crash case to distinguish normal from incognito behavior. A ZFS case supplied commands and before/after space observations, yet both first wanted to clarify the measured quantity. A Kile case described a segmentation fault and a working clean virtual machine, but both wanted a version or trace distinction. Thus, technical detail alone did not dictate investigation.

\textbf{A remedy can support different next actions.} For Firefox controls and Fedora autorotation reports containing workarounds, one reviewer would investigate while the other preferred grouping reports or monitoring wider scope. In a VS Code terminal case with a workaround, both still chose investigation. A single ``remedy present'' field therefore did not map consistently to one first action in these cases.

\textbf{Similar cited facts can support different thresholds for action.} In a screenshot case, both noticed the same visual contrast, but one opened a lead while the other wanted to distinguish image content from display behavior. For a microphone indicator, one weighed recurrence and privacy implications while the other requested identification of the active process. In a MySQL case, one reviewer asked whether the failure persisted beyond the captured startup instant, whereas the other treated reported inaccessibility as sufficient to investigate. These are interpretations of their explanations; the study did not isolate the causes of disagreement.

\textbf{Purpose labels and actions are distinct.} Both reviewers chose investigation for a historically other-labeled post reporting application breakage after a release-channel change. Dissatisfaction-labeled posts with concrete UI changes yielded investigation/monitoring or cannot-assess/monitoring pairs. Conversely, both chose no update-focused action for selected strategy, positive-feedback, preflight-checklist, and version-lookup cases. These contrasts demonstrate conceptual distinctions in this sample, not the frequency of mislabeled posts in the corpus.

\section{Discussion and Threats to Validity}
\subsection{Meaning for software-update triage}
The three studies answer different questions. Purpose classification locates likely troubleshooting within reviewed update scope. Diagnostic coding describes available facts. The case study examines how readers interpret those facts relative to an initial action. Their combination shows why a purpose label or a count of visible fields should not be treated as an action recommendation.

The practical implication is a possible organizing workflow: surface a relevant report, preserve its evidence and uncertainty, and let an engineer decide whether to investigate, clarify, or monitor. A useful representation would retain the relationship between an update, a symptom, a comparison, and a reported remedy, rather than only counting field names. This is an implication for future design, not an evaluated system. The present study observes neither issue resolution nor engineering time saved.

\subsection{Validity boundaries}
\textbf{Collection and generalization.} Keyword/API selection, source--class associations, the 30 source-metadata conflicts, and restriction to reviewed scope limit representativeness. Source-restricted development checks preserve the broad classifier conclusion but do not revalidate the historical tests on a corrected corpus. Neither class proportions nor qualitative action frequencies estimate Reddit-wide behavior. Fresh IDs are not necessarily later events, and developers of the affected products were not recruited as incident owners.

\textbf{Labels and construct validity.} Annotation includes assisted and joint review. A selected independent check cannot establish corpus-wide reliability, and diagnostic reconfirmation exposed scope discrepancies. A visible version, error, or remedy is not a verified cause or a usefulness measure. Other update combines heterogeneous discussion types. The classifier does not predict first actions or independently determine update scope.

\textbf{Evaluation and conclusion validity.} Development selection, subsequent audits, and different fits require explicit version boundaries. Bootstrap intervals condition on the saved labels and predictions; they do not resolve correlated incidents or annotation uncertainty. Duplicate controls reduce obvious overlap but may miss paraphrased reports. The fresh minority class is small. Grouped and representation comparisons remain development-only. The absence of a reliable MiniLM gain does not establish equivalence of all lexical and semantic models.

\textbf{Human-study validity.} Two reviewers and 30 deliberately varied cases support an exploratory account, not saturation, population reliability, correct decisions, or causal influence of evidence. Independence and qualifications are coordinator-reported process facts. Investigator interpretation may favor the proposed purpose/evidence/action distinction; contrary and negative cases were retained to challenge it. Saved bodies can include later fixes, omit comments or inaccessible media, and differ from the information available at first publication. No passage was experimentally removed and no real queue was observed.

\subsection{Research ethics and reproducibility}
Reviewer files use study IDs, and the manuscript paraphrases examples without usernames or direct post links. The qualitative task used saved text and did not contact post authors. Versioned manifests, source hashes, review guides, analysis outputs, and model settings support internal traceability. We make no claim here that raw text or reviewer responses are publicly redistributable.

\authorcheck{Insert the name of the institutional oversight body, its actual determination, and the reviewer-consent statement from the private study record before submission. Completion of these checks has been reported by the study coordinator; exact wording has not yet been supplied.}

\section{Conclusion}
Within human-established software-update scope, title/body TF-IDF logistic regression separated troubleshooting from other discussion more effectively than majority and keyword rules, reaching macro-F1 0.792 on a fresh unseen-ID sample. Diagnostic coding showed that reproduction context and error evidence were often not visible in saved troubleshooting text. In 30 intact cases, two external reviewers sometimes selected different first actions while citing similar facts. Together, these findings distinguish discussion purpose from the interpretation of diagnostic evidence: identifying troubleshooting can organize feedback, while first-pass engineering decisions also reflect uncertainty and judgments about whether the evidence is sufficient. The study supports this bounded distinction, not an automated or causally validated triage policy.

\section*{Acknowledgment}
OpenAI Codex assisted with prose drafting and organization throughout the manuscript, LaTeX preparation, and plotting code for figures drawn from saved research results. The authors are responsible for verifying the claims, citations, and final manuscript. Annotation provenance is described separately in the methods.

\bibliographystyle{IEEEtran}
\bibliography{references}
\end{document}
'''
# Correct fresh precision from frozen confusion counts: 46/(46+25), not recall.
main=main.replace('Other-update precision/recall were 0.687/0.687','Other-update precision/recall were 0.648/0.687')
(O/'main.tex').write_text(main)
bib=(P/'references.bib').read_text()
# BibTeX-safe diacritics and acronym protection.
for a,b in [('ö',r'{\"o}'),('ü',r'{\"u}'),('ä',r'{\"a}'),('á',r"{\'a}"),('é',r"{\'e}")]:bib=bib.replace(a,b)
for a in ['Reddit','ChatGPT','ChatBR','Sentence-BERT','Google Play','Moodle','VS Code']:
 bib=re.sub(r'(?m)^(  title = .*)$',lambda m:m[0].replace(a,'{'+a+'}'),bib)
(O/'references.bib').write_text(bib)
manifest={'source_files':{},'figure_notes':{'study_flow':'Counts from version reconciliation, diagnostic analysis, qualitative selection','diagnostic_evidence':'Saved rates and Wilson intervals; denominator 237','reviewer_actions':'Counts from unchanged paired reviewer responses'},'no_new_models_or_scores':True}
for s in ['phase3/diagnostic_results/analysis.json','phase3/icsc_full_paper/RESULT_VERSION_RECONCILIATION.json','phase4/qualitative_study/ANALYST_ONLY_PAIRED_RESPONSES.csv','phase4/qualitative_study/SELECTION_VALIDATION.json']:
 manifest['source_files'][s]=hashlib.sha256((R/s).read_bytes()).hexdigest()
(O/'FIGURE_SOURCES.json').write_text(json.dumps(manifest,indent=2))
(O/'README.md').write_text('''# ICSC 2027 manuscript

Compile main.tex with pdfLaTeX and BibTeX (Overleaf default). IEEEtran conference mode, US Letter, unchanged template margins. The IEEEtran class and bibliography style are from CTAN. Vector PDF figures are generated from frozen research outputs; PNG copies are supplied for convenience.

This is a complete author-review manuscript, not a certification that submission conditions have been met. A visible red author-confirmation statement remains for the exact institutional determination and reviewer consent. Replace it only with supported facts. Keep the AI-assistance acknowledgment accurate. Check the EasyChair track instructions for anonymity before final export. Prior ICMLA work was reported accepted but unpublished; verify it did not enter proceedings. Thirty source metadata conflicts are described transparently and historical evaluations remain unchanged.

Files: main.tex; references.bib; IEEEtran.cls; IEEEtran.bst; study_flow.pdf; diagnostic_evidence.pdf; reviewer_actions.pdf; corresponding PNGs; FIGURE_SOURCES.json. Do not upload private reviewer workbooks or raw post data with the manuscript.
''')
print('Created LaTeX manuscript, bibliography, three PDF/PNG figures and provenance files.')
