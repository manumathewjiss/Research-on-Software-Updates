# Fresh-test qualitative error review guide

**Status:** codebook frozen for a prospective *interpretive* review, not a change to test labels. Input: `phase3/fresh_test_20261007/saved_error_analysis/all_46_errors.csv` and `matched_correct_examples.csv`. There are 25 false negatives, 21 false positives, and 46 matched correct controls. Existing `provisional_error_codes.csv` must be hidden from any blind reviewer.

## Question

What text-level situations appear in the mistakes, and do the same situations also appear in correctly classified posts? This review describes examples. It does not identify the causal reason for a model score.

## Review material and order

1. Create a shuffled 92-row reading packet from the 46 errors and 46 controls. Show saved title/body only, with an arbitrary packet ID. Hide predicted class, model score, error/control status, provisional codes, and test-set correctness. If the reviewed class is needed to interpret the task, show it only **after** the first text coding pass.
2. Code every row using the categories below. Allow multiple feature tags plus one primary discussion-purpose code. Quote a short supporting phrase. Mark `unclear` rather than inventing missing context.
3. Lock the coding file. Join back to error/control status and true class only after locking. Tabulate category counts separately for false positives, false negatives, and matched controls.
4. Keep the original 344 test labels, 46 error IDs, predictions, and scores unchanged. If a post seems mislabeled, record `possible_label_boundary=yes` and discuss it separately; do not alter the frozen evaluation.

## Codes

| Field | Allowed values | Rule |
|---|---|---|
| `purpose` | `concrete_problem`, `update_advice`, `feature_or_change_question`, `opinion_or_criticism`, `announcement_or_explanation`, `other`, `unclear` | Code the author's main purpose, not the model's answer. A question mark does not automatically mean troubleshooting. |
| `problem_evidence` | `specific`, `vague`, `none`, `unclear` | `specific` names concrete wrong behavior; `vague` says something is bad/broken without a concrete behavior. |
| `update_role` | `reported_cause_or_effect`, `installation_process`, `preventive_or_future_advice`, `background_only`, `unclear` | Code how an update figures in the *post*, not whether an update really caused the issue. |
| `text_availability` | `title_and_body`, `title_only` | Use saved snapshot, never the live page. |
| `possible_label_boundary` | `yes`, `no`, `unclear` | `yes` when the current task definition plausibly supports another discussion type. This is a flag, not a corrected label. |
| `note` | free text | Short phrase supporting any non-obvious code. |

## Reporting rules

- Include denominator and class in every count. The 46 errors were selected *because they are errors*; their category frequencies cannot estimate the frequency of these patterns in all posts.
- Compare with the matched correct controls before saying a pattern is distinctive. The control match is imperfect (38/46 same subreddit), so comparisons remain descriptive.
- Keep model-score distance as a separate numerical observation. Existing saved analysis found 14/46 errors within 0.05 of the threshold, but this is not proof that threshold tuning fixes them.
- Do not combine this fresh-test reading with the 250-post diagnostic-detail study as though the latter annotated the fresh posts. Diagnostic fields were assessed on development posts only.
- If only one person codes, call it a single-analyst qualitative review. Do not report inter-rater agreement.

## Completion criterion

A locked 92-row coding file, code-count table split by false positive/false negative/correct control, two or three representative *short paraphrased* examples per major pattern, and a limitations paragraph. The current provisional 46-case codes may be consulted only after this review is locked.
