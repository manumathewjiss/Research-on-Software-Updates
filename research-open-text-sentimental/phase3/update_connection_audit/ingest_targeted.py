"""Validate the completed targeted review and create a reversible development snapshot."""

from __future__ import annotations

import collections
import hashlib
import json
import shutil
from pathlib import Path

import openpyxl


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCE = Path('/Users/manumathewjiss/Documents/Codex/2026-10-06/i-wi/outputs/Targeted_Update_Connection_254_Completed.xlsx')
BLANK = Path('/Users/manumathewjiss/Documents/Codex/2026-10-02/so-x20/outputs/update_connection_audit_20261008/Targeted_Update_Connection_254_Blind.xlsx')
OUT = HERE / 'targeted_submission'
FIELDS = ('review_id', 'title', 'post_body', 'saved_reply_context', 'about_software', 'update_related', 'discussion_type', 'confidence', 'reason')
LABEL_FIELDS = ('about_software', 'update_related', 'discussion_type')


def read_rows(path: Path) -> list[dict]:
    ws = openpyxl.load_workbook(path, data_only=True).active
    assert tuple(ws.cell(5, c).value for c in range(1, 10)) == FIELDS
    return [dict(zip(FIELDS, row)) for row in list(ws.values)[5:]]


def load_json(path: Path):
    return json.loads(path.read_text())


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def dump_json(path: Path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def dump_jsonl(path: Path, values):
    path.write_text(''.join(json.dumps(value, ensure_ascii=False, sort_keys=True) + '\n' for value in values))


def s2(row):
    return row['about_software'] == 'yes' and row['update_related'] == 'yes' and row['discussion_type'] in ('technical_troubleshooting', 'general_dissatisfaction', 'other')


def main():
    completed, blank = read_rows(SOURCE), read_rows(BLANK)
    assert len(completed) == len(blank) == 254
    assert len({r['review_id'] for r in completed}) == 254
    assert [tuple(r[k] for k in FIELDS[:4]) for r in completed] == [tuple(r[k] for k in FIELDS[:4]) for r in blank]
    assert all(r[k] is None for r in blank for k in FIELDS[4:])
    assert all(r['about_software'] in ('yes', 'no', 'unclear') and r['update_related'] in ('yes', 'no', 'unclear') and r['discussion_type'] in ('technical_troubleshooting', 'general_dissatisfaction', 'other', 'na') and r['confidence'] in ('high', 'medium', 'low') and isinstance(r['reason'], str) and r['reason'].strip() for r in completed)
    assert all((r['about_software'] == 'yes') == (r['discussion_type'] != 'na') for r in completed)

    mapping = {r['review_id']: r for r in load_json(HERE / 'ANALYST_ONLY_TARGETED_MAPPING.json')}
    assert set(mapping) == {r['review_id'] for r in completed}
    adj_mapping = {r['audit_id']: r for r in load_json(ROOT / 'phase3/single_reviewer_audit_20261008/ANALYST_ONLY_MAPPING.json')}
    adj = load_json(HERE / 'submission/final_decisions_resolved.json')
    assert len(adj) == 22 and len({r['audit_id'] for r in adj}) == 22
    old_dev = load_jsonl(ROOT / 'phase3/revised_development_v2/development_v2.jsonl')
    dev_by_id = {r['reddit_id']: r for r in old_dev}
    reserved_ids = {r['reddit_id'] for r in load_jsonl(ROOT / 'phase3/experiment_v1/data/reserved_test.jsonl')}
    assert len(dev_by_id) == len(old_dev) == 3151

    decisions = {}
    reviewed_rows = []
    for r in completed:
        post_id = mapping[r['review_id']]['reddit_id']
        assert post_id in dev_by_id and post_id not in reserved_ids and post_id not in decisions
        decisions[post_id] = {k: r[k] for k in LABEL_FIELDS}
        reviewed_rows.append({'review_id': r['review_id'], 'reddit_id': post_id,
                              'selection_group_audit_only': mapping[r['review_id']]['selection_group_audit_only'],
                              'previous': {k: dev_by_id[post_id][k] for k in LABEL_FIELDS},
                              'final': {k: r[k] for k in LABEL_FIELDS},
                              'confidence': r['confidence'], 'reason': r['reason']})
    for r in adj:
        post_id = adj_mapping[r['audit_id']]['reddit_id']
        assert post_id in dev_by_id and post_id not in reserved_ids and post_id not in decisions
        decisions[post_id] = {k: r['final_' + k] for k in LABEL_FIELDS}
    assert len(decisions) == 276

    updated = []
    for old in old_dev:
        row = dict(old)
        if row['reddit_id'] in decisions:
            row.update(decisions[row['reddit_id']])
            row['s2_in_scope'] = s2(row)
            row['s2_target'] = int(row['discussion_type'] == 'technical_troubleshooting')
            row['review_status_audit_only'] = 'update_connection_audit_20261007'
        updated.append(row)
    assert len(updated) == len(old_dev) and {r['reddit_id'] for r in updated} == set(dev_by_id)

    before, after = collections.Counter((r['about_software'], r['update_related'], r['discussion_type']) for r in old_dev), collections.Counter((r['about_software'], r['update_related'], r['discussion_type']) for r in updated)
    summary = {
        'source_workbook_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'targeted_rows': 254, 'unique_targeted_ids': 254, 'adjudicated_rows': 22,
        'all_276_in_development': True, 'reserved_overlap': 0,
        'targeted_update_answers': dict(collections.Counter(r['update_related'] for r in completed)),
        'targeted_selection_by_update_answer': {f'{group}/{label}': n for (group, label), n in sorted(collections.Counter((mapping[r['review_id']]['selection_group_audit_only'], r['update_related']) for r in completed).items())},
        'targeted_software_answers': dict(collections.Counter(r['about_software'] for r in completed)),
        'targeted_discussion_answers': dict(collections.Counter(r['discussion_type'] for r in completed)),
        'changed_targeted_update_no_to_yes': sum(r['previous']['update_related'] == 'no' and r['final']['update_related'] == 'yes' for r in reviewed_rows),
        'changed_targeted_update_no_to_unclear': sum(r['previous']['update_related'] == 'no' and r['final']['update_related'] == 'unclear' for r in reviewed_rows),
        'dev_s2_before': sum(s2(r) for r in old_dev), 'dev_s2_after': sum(s2(r) for r in updated),
        'dev_s2_class_before': dict(collections.Counter(r['discussion_type'] for r in old_dev if s2(r))),
        'dev_s2_class_after': dict(collections.Counter(r['discussion_type'] for r in updated if s2(r))),
        'all_dev_class_counts_before': {str(k): v for k, v in before.items()},
        'all_dev_class_counts_after': {str(k): v for k, v in after.items()},
        'historical_master_overwritten': False, 'historical_tests_overwritten': False,
        'model_retrained': False,
    }
    OUT.mkdir(exist_ok=True)
    shutil.copy2(SOURCE, OUT / SOURCE.name)
    dump_json(OUT / 'targeted_review_decisions.json', reviewed_rows)
    dump_json(OUT / 'intake_summary.json', summary)
    dump_jsonl(OUT / 'development_after_update_audit.jsonl', updated)
    print(json.dumps({k: v for k, v in summary.items() if k not in ('all_dev_class_counts_before', 'all_dev_class_counts_after')}, indent=2))


if __name__ == '__main__':
    main()
