# Update-related scope conflict found after the 22-row adjudication

The completed 22-row workbook was validated and preserved. Its answers are human final decisions **under the guide supplied for that workbook**. They have not been merged into the master.

Before releasing the 254-row packet, a definition conflict must be resolved:

- `phase2/TASK_DEFINITION.md` section 2.2 defines `update_related=yes` broadly: connected to an update, upgrade, new release, patch, version bump, or a problem/change that followed one. Under that definition, release announcements and substantive update advice can be in S2 as `discussion_type=other`.
- The later `update_connection_audit/REVIEW_GUIDE.md` told the reviewer to count an update connection mainly when it caused or changed an **issue** or when the update process failed. That instruction is narrower. It could exclude the very other-update discussions used as the comparison class.
- The user-requested update-connection rule was an *inclusion* clarification: when an author explicitly suspects or asks whether an update caused or affected a problem, count it. It did not state that announcements and update advice should be excluded.

Example affected decisions include `A022` (preventive firmware update advice, final `update_related=no`) and `A049` (a new app-bundle version central to getting an app reviewed, final `update_related=no`). Under the earlier broad definition, these are plausible `yes` cases. This does **not** make the submitted judgments errors; the supplied guide encouraged the narrower reading.

Recommended resolution: keep `update_related` broad for the S2 population, with `yes` for posts substantively about a specific software update/release/patch or its effects, including announcements, update planning, failed updates, and explicit author suspicion of an update-caused issue. Keep `no` for incidental version numbers, unrelated uses of “update,” and updates merely tried as generic fixes for an otherwise unconnected problem. If the author/reply evidence is insufficient, use `unclear`. Record a separate `update_problem_connection` field in future work only if the paper needs the narrower causal-link concept.

Resolution for the working materials: use the **original broad Phase 2 definition**. The later guide has been corrected to match it. This restores the announced S2 question: troubleshooting versus other discussion about software updates. The 22 submitted decisions remain preserved as submitted; none have been silently changed.

Two submitted decisions received a targeted human recheck under the corrected wording on 2026-10-07:

- `A022`: Manu confirmed `update_related=no`. The firmware update is preventive advice for a known defect; it did not cause or change the reported issue.
- `A049`: Manu changed the workbook answer to `update_related=yes`. A new app version changed the Play Console review outcome.

The original completed workbook remains unchanged. The resolved 22 decisions, with this chat clarification and its provenance, are in `submission/final_decisions_resolved.json` and `submission/FOLLOWUP_DECISIONS.json`. The 254-row workbook remains blank and can be reviewed using the corrected guide. Historical labels and model results remain unchanged. A future master merge must use the resolved decisions, not the earlier workbook-only JSON.
