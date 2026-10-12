import fs from "node:fs/promises";
import crypto from "node:crypto";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Workbook, SpreadsheetFile } from "@oai/artifact-tool";

const dir = path.dirname(fileURLToPath(import.meta.url));
const all = JSON.parse(await fs.readFile(path.join(dir, "packet_source.json"), "utf8"));
const headers = [
  "case_id", "title", "original_post_body", "first_action_A_B_C_D_or_cannot_assess",
  "exact_evidence_from_post", "why_this_action_not_closest_alternative",
  "important_uncertainty", "one_question_and_how_answer_changes_action",
  "confidence_low_medium_high", "reason_if_cannot_assess",
];
const cleanCell = (s) => {
  const value = String(s ?? "");
  return /^[=+\-@]/.test(value) ? `'${value}` : value;
};
const files = [];
for (const cohort of ["pilot", "main"]) {
  for (const reviewer of ["A", "B"]) {
    const rows = all.filter((r) => r.cohort === cohort).sort((a, b) => {
      const key = (r) => crypto.createHash("sha256")
        .update(`phase4-qualitative-v1|20261008|${cohort}|${reviewer}|${r.study_case_id}`)
        .digest("hex");
      return key(a).localeCompare(key(b));
    });
    const wb = Workbook.create();
    const ws = wb.worksheets.add("Review");
    ws.showGridLines = false;
    ws.freezePanes.freezeRows(1);
    ws.getRange("A1:J1").values = [headers];
    ws.getRange(`A2:J${rows.length + 1}`).values = rows.map((r) => [
      cleanCell(r.study_case_id), cleanCell(r.title), cleanCell(r.post_body),
      "", "", "", "", "", "", "",
    ]);
    ws.getRange("A1:J1").format = {
      fill: "#17365D", font: { name: "Aptos", size: 10, bold: true, color: "#FFFFFF" },
      wrapText: true,
    };
    ws.getRange("A1:J1").format.rowHeight = 56;
    ws.getRange(`A2:J${rows.length + 1}`).format.font = { name: "Aptos", size: 10 };
    ws.getRange(`A2:J${rows.length + 1}`).format.verticalAlignment = "top";
    ws.getRange(`B2:C${rows.length + 1}`).format.wrapText = true;
    ws.getRange("A:A").format.columnWidth = 11;
    ws.getRange("B:B").format.columnWidth = 40;
    ws.getRange("C:C").format.columnWidth = 105;
    ws.getRange("D:D").format.columnWidth = 29;
    ws.getRange("E:H").format.columnWidth = 42;
    ws.getRange("I:J").format.columnWidth = 28;
    ws.getRange(`A2:J${rows.length + 1}`).format.rowHeight = 270;
    wb.recalculate();
    const filename = cohort === "pilot"
      ? `Reviewer_${reviewer}_PILOT_6_BLANK.xlsx`
      : `Reviewer_${reviewer}_MAIN_30_HOLD_UNTIL_PILOT.xlsx`;
    const dest = path.join(dir, filename);
    const out = await SpreadsheetFile.exportXlsx(wb);
    await out.save(dest);
    const check = await wb.inspect({
      kind: "table", range: `Review!A1:D${Math.min(rows.length + 1, 4)}`,
      include: "values", tableMaxRows: 4, tableMaxCols: 4,
    });
    const preview = await wb.render({ sheetName: "Review", range: "A1:D3", scale: 1 });
    await fs.writeFile(path.join(dir, `${filename}.preview.png`),
      new Uint8Array(await preview.arrayBuffer()));
    files.push({ filename, cohort, reviewer, n: rows.length,
      case_ids_in_order: rows.map((r) => r.study_case_id),
      sha256: crypto.createHash("sha256").update(await fs.readFile(dest)).digest("hex"),
      inspected: Boolean(check.ndjson), });
  }
}
await fs.writeFile(path.join(dir, "WORKBOOK_MANIFEST.json"),
  JSON.stringify({ version: "qualitative-packet-v1", seed: 20261008, files }, null, 2));
console.log(JSON.stringify(files.map(({ filename, n, sha256 }) => ({ filename, n, sha256 })), null, 2));
