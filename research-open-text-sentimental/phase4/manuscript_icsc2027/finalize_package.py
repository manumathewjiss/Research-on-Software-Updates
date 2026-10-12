from pathlib import Path
import re,json
P=Path(__file__).resolve().parent;R=P.parents[1];O=P/'overleaf';p=O/'main.tex';s=p.read_text()
d=json.loads((R/'phase3/experiment_v1/results/model_selection.json').read_text())
model_labels={'majority':'Majority','keyword':'Fixed keywords','tfidf_lr':'TF-IDF LR','tfidf_linear_svm':'TF-IDF linear SVM'}
table=r'''
\begin{table}[t]
\caption{Original development selection: pooled out-of-fold macro-F1 on 2,084 posts}
\label{tab:selection}\centering\footnotesize
\begin{tabularx}{\columnwidth}{Lrr}
\toprule
Model & Title only & Title + body\\\midrule
'''
for model,label in model_labels.items():
 vals=[]
 for setting in ['title','title_body']:
  r=next(x for x in d['ranked_candidates'] if x['model']==model and x['text_setting']==setting)
  vals.append(f"{r['macro_f1']:.3f}")
 table+=label+' & '+' & '.join(vals)+r'\\'+'\n'
table+=r'''\bottomrule
\end{tabularx}
\vspace{2pt}
\parbox{\columnwidth}{\scriptsize Best $C$ per learned model/text setting; default decision thresholds. After selection, the chosen LR threshold was adjusted on development predictions, yielding macro-F1 0.841. These are selection results, not protected-test estimates.}
\end{table}
'''
s=s.replace(r'\subsection{Duplicate controls and sensitivity analyses}',table+'\n'+r'\subsection{Duplicate controls and sensitivity analyses}')
s=s.replace('The selected model was title-plus-body logistic regression',r'Table~\ref{tab:selection} shows that both learned models benefited from body text in the original selection comparison. The selected model was title-plus-body logistic regression')
s=s.replace('The research collection contains 3,362 unique records:', 'The research collection contains 3,362 unique records:')
s=s.replace('The routes supplied candidate pools, not reference labels.', 'The 542 historical records underpinned an earlier ICMLA submission, accepted as a short paper but not published. The present work revises its purpose labels and scope rules, expands review and evaluation, and adds diagnostic coding and an independent exploratory decision study. The routes supplied candidate pools, not reference labels.')
s=s.replace('ScholarlyXX','ScholarlyXX')
p.write_text(s)
b=O/'references.bib';s=b.read_text()
# Include identifiers using fields supported by IEEEtran.bst.
for key,num in [('Tkalich2025Feedback','79'),('Wang2026Evidence','103'),('Laiq2026Mapping','72'),('Tang2024ReviewBugs','124'),('Laiq2024Industrial','130')]:
 pat=r'(@\w+\{'+key+r',.*?)(\n\})'
 s=re.sub(pat,lambda m:m[1]+',\n  note = {Art. no. '+num+'}'+m[2],s,flags=re.S)
# Add URLs where the DOI-only field is not rendered by the standard bibliography style.
s=re.sub(r'(  doi = \{([^}]+)\})(\n\})',lambda m:m[1]+',\n  url = {https://doi.org/'+m[2]+'}'+m[3],s)
s=s.replace('note = {Author manuscript reports acceptance at IEEE RE 2026}','howpublished = {arXiv:2606.20876},\n  url = {https://arxiv.org/abs/2606.20876},\n  note = {Author manuscript; reports acceptance at IEEE RE 2026}')
s=s.replace('Massimiliano Di Penta','{Di Penta}, Massimiliano')
s=s.replace('Siamese BERT-Networks','Siamese {BERT}-Networks')
b.write_text(s)
print('Added saved selection results; fixed flow clipping and bibliography identifiers.')
