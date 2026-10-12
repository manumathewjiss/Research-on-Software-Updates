"""Development-only fixed-model check after confirmed label revisions."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT / 'experiment_v1'))
sys.path.insert(0, str(ROOT / 'experiment_v1/followup'))
from run_experiment import build_lr, keyword_predict, make_text, metrics_bundle  # noqa: E402
from run_followup import audit_within_dev  # noqa: E402

HERE = Path(__file__).resolve().parent
IN = HERE / 'targeted_submission/development_after_update_audit.jsonl'
OUT = HERE / 'targeted_submission/post_audit_grouped_validation.json'
NEAR_DUP = {'1t0wme9', '1wrqch6'}
THRESHOLD = 0.5877137791150834


def main():
    rows = [json.loads(line) for line in IN.read_text().splitlines() if line]
    master = {r['reddit_id']: r for r in json.loads((REPO / 'phase2/combined_dataset/master_records.json').read_text())}
    assert len(rows) == 3151 and len({r['reddit_id'] for r in rows}) == 3151
    rows = [r for r in rows if r['s2_in_scope'] and r['reddit_id'] not in NEAR_DUP]
    assert len(rows) == 2166
    domains = [urlparse(master[r['reddit_id']]['url']).netloc.lower().removeprefix('www.') for r in rows]
    assert all(domain in ('reddit.com', 'stackoverflow.com') for domain in domains)
    assert sum(domain == 'stackoverflow.com' for domain in domains) == 30
    results = {}
    for population, subset in [('mixed', rows), ('reddit_only', [r for r, host in zip(rows, domains) if host == 'reddit.com'])]:
        texts = [make_text(r, 'title_body') for r in subset]
        y = np.array([int(r['s2_target']) for r in subset], dtype=int)
        _, groups = audit_within_dev(subset)
        splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
        pred = np.full(len(subset), -1, dtype=int)
        majority = np.full(len(subset), -1, dtype=int)
        keyword = np.full(len(subset), -1, dtype=int)
        score = np.full(len(subset), np.nan)
        fold_ids = np.full(len(subset), -1, dtype=int)
        for fold, (train, test) in enumerate(splitter.split(np.zeros(len(subset)), y, groups)):
            model = build_lr(4.0)
            model.fit([texts[i] for i in train], y[train])
            scores = model.predict_proba([texts[i] for i in test])[:, 1]
            score[test] = scores
            pred[test] = (scores >= THRESHOLD).astype(int)
            majority[test] = int(Counter(y[train].tolist()).most_common(1)[0][0])
            keyword[test] = keyword_predict([texts[i] for i in test])
            fold_ids[test] = fold
        assert np.isfinite(score).all() and min(pred) >= 0 and min(fold_ids) >= 0
        results[population] = {
            'n': len(subset),
            'class_counts': {'troubleshooting': int(sum(y)), 'other_update': int(len(y) - sum(y))},
            'fixed_tfidf_lr': metrics_bundle(y, pred, score),
            'majority': metrics_bundle(y, majority),
            'keyword': metrics_bundle(y, keyword),
            'oof_predictions_file': f'post_audit_{population}_oof.jsonl',
        }
        with (OUT.parent / results[population]['oof_predictions_file']).open('w') as f:
            for r, label, prediction, probability, fold in zip(subset, y, pred, score, fold_ids):
                f.write(json.dumps({'reddit_id': r['reddit_id'], 'y_true': int(label), 'y_pred': int(prediction), 'score': float(probability), 'fold': int(fold)}) + '\n')
    report = {
        'input_sha256': hashlib.sha256(IN.read_bytes()).hexdigest(),
        'method': '5-fold StratifiedGroupKFold, seed 42, exact/near duplicate groups; fixed title+body TF-IDF logistic regression C=4, balanced class weights, threshold 0.5877137791150834',
        'no_tuning': True,
        'reserved_test_scored': False,
        'fresh_test_scored': False,
        'important_comparison_limit': 'The audited population and duplicate-group folds differ from the historical v2 run; score differences are not same-fold paired effects.',
        'results': results,
    }
    OUT.write_text(json.dumps(report, indent=2) + '\n')
    for population, value in results.items():
        print(population, value['n'], value['class_counts'], 'model', value['fixed_tfidf_lr']['macro_f1'], 'majority', value['majority']['macro_f1'], 'keyword', value['keyword']['macro_f1'])


if __name__ == '__main__':
    main()
