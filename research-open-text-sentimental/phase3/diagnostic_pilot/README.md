# Diagnostic-detail pilot: ready for Manu's review

This is the first implementation step from `../RESEARCH_EXPANSION_PLAN.md`. It is a **50-post feasibility pilot**, not a prevalence estimate, model test, or finished diagnostic taxonomy.

## Files

- `CODEBOOK_DRAFT.md`: provisional rules and synthetic examples.
- `outputs/diagnostic-pilot-20261007/Pilot_Diagnostic_Details_50.xlsx`: reviewer workbook; all answer cells blank.
- `pilot_review_text.json`: the same 50 titles/bodies, without source/model information.
- `analyst_mapping.json`: private mapping to source IDs and collection metadata. Keep separate from the reviewer workbook while labeling.
- `sampling_manifest.json` and `build_sample.py`: reproducible sample rules.

## Sample design

Drawn only from revised-development S2 troubleshooting decisions. The original reserved test and all 30 Stack Overflow records are excluded. Seed 20261007. Fifty unique post texts: 8 from Phase 1, 12 from the Oct-5 GDS candidate pool, and 30 from the Oct-5 TPS candidate pool. Ten have no saved post body. These quotas deliberately enrich unusual sources and short posts so the draft codebook is challenged. **Do not use the 50-post field frequencies as corpus prevalence.**

The first workbook question lets Manu flag a sampled post whose existing troubleshooting label appears wrong. Such flags do not silently modify the Phase 2 dataset. Only the title and original body should be used for field judgments; saved comments are not shown.

## Immediate work

1. Manu reads `CODEBOOK_DRAFT.md` and fills the yellow answer columns in the workbook.
2. After all 50 are returned, validate completeness and allowed values. Summarize fields that were hard to distinguish, inspect `no`/`unclear` troubleshooting checks, and revise the codebook. Preserve the returned workbook unchanged.
3. Review a masked subset under the revised guide to check whether the new distinctions work. Since the rules changed, compare decisions descriptively; do not call this a within-reviewer consistency score or independent inter-annotator agreement.
4. Only then design the larger diagnostic-detail sample and any model/error analysis using those labels.

The workbook is a labeling artifact. It does not imply that a sole labeler is the sole author of the paper; authorship and annotation role must be described separately.
