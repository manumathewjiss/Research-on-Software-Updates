# Fresh-test error analysis, first pass

This pass reads only the already frozen 344 predictions. It does not change labels, model settings, or test scores. Reproduce with `python3 phase3/fresh_test_20261007/analyze_saved_errors.py` from the project root. The complete error list and numerical summary are `all_46_errors.csv` and `summary.json`.

## Verified counts

- 344 S2 test posts: 298 correct, 25 troubleshooting posts missed (false negatives), and 21 other-update posts incorrectly flagged as troubleshooting (false positives).
- The model score is within 0.05 of its fixed threshold for 14 of the 46 mistakes. Other mistakes are farther from the threshold, so threshold adjustment alone cannot be assumed to solve the problem.
- Only six of 344 test posts have no saved body, including two errors. This test cannot support a stable title-only subgroup conclusion.
- Subreddit counts are descriptive only; small and unequal class counts prevent causal or broad community claims.

## Provisional reading of all 46 errors

The full saved text of each error was read and assigned one **descriptive** primary pattern in `provisional_error_codes.csv`; the corresponding counts and a reproducible 46-case correct-control sample are in `provisional_coding_summary.json` and `matched_correct_examples.csv`. Recreate those outputs with `python3 phase3/fresh_test_20261007/saved_error_analysis/code_saved_errors.py` from the project root. These codes are analyst interpretations after the test was scored. They are not new human-confirmed labels, a causal explanation, or an independently validated error taxonomy.

Among the 25 false negatives, the largest pattern is a post describing a specific malfunction (6 cases). Three describe update-installation trouble, three are very brief malfunction reports, three are resolved incident narratives, and three ask for configuration help. The remaining seven span performance, changed features, UI behavior, documentation, and design criticism. This variety argues against a single simple explanation such as “all misses lack technical words.”

Among the 21 false positives, five ask for preventive update advice, four observe a feature or change, and two primarily criticize design. The others include general questions, explanations, an alternatives list, and several cases close to the troubleshooting boundary. The model can therefore treat update vocabulary or help-seeking wording as troubleshooting even when the reviewed label says “other update.” The exact cause of the model's score is not proven by these examples.

Twenty-two errors were flagged for **possible task-boundary adjudication**, not declared annotation mistakes. Examples include a post that cannot find a newly added feature (`T20261007-181`) and a post where cumulative updates are missing after a management-system migration (`T20261007-473`), both reviewed as other update, and a detailed critique of a changed Copilot interface (`T20261007-411`), reviewed as troubleshooting. Do not change these labels after seeing model predictions. A separate blinded re-review would be needed to assess consistency.

The correct-control sample matches each error on reviewed class and, when possible, subreddit (38 of 46 pairs). It shows that broad surface descriptions overlap: correctly classified other-update posts also ask questions or criticize interface changes, while correctly classified troubleshooting posts also mention updates and behavior changes. In this matched sample, question marks appear in 17/21 false positives versus 15/21 correct other-update controls and 16/25 false negatives versus 16/25 correct troubleshooting controls. Thus a question mark is not a useful explanation by itself. Error posts were closer to the fixed threshold than their matched controls in this selected sample (14/46 versus 4/46 within 0.05), but the sample is small and post-selected. Its purpose is to challenge simple stories, not estimate population effects.

## Remaining manuscript check

Before turning this into a manuscript error table, freeze a compact set of patterns and have a second analyst review disputed cases without seeing the model prediction. Report both clear examples and boundary cases, with no claim that these codes identify a causal failure mechanism. The current numerical result remains the frozen 344-post test score.

For the 250-post diagnostic sample, use only its saved grouped out-of-fold development predictions. Those diagnostic fields were **not** annotated on the fresh test, so they cannot directly explain the 46 fresh-test mistakes. The two analyses can be discussed together as separate evidence, with that limit explicit.
