import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const here = path.dirname(new URL(import.meta.url).pathname);
const rows = JSON.parse(await fs.readFile(path.join(here, 'blind_rows.json'), 'utf8'));
if (rows.length !== 200 || new Set(rows.map(r => r.review_id)).size !== 200) throw new Error('Sample integrity failed');
const columns = [
  'review_id', 'title', 'post_body', 'discussion_context',
  'about_software', 'update_related', 'discussion_type', 'confidence', 'reason',
  'software_product', 'identifiable_release', 'environment', 'specific_symptom',
  'reproduction_context', 'error_evidence', 'attempted_remedy', 'help_request',
];

async function build(letter) {
  const wb = Workbook.create();
  const sh = wb.worksheets.add('Review');
  sh.showGridLines = false;
  sh.tabColor = '#1F4E78';
  sh.getRange('A2').values = [[`Independent review — Reviewer ${letter}`]];
  sh.getRange('A2:Q2').format.font = { name: 'Arial', size: 14, bold: true, color: '#172B4D' };
  sh.getRange('A3').values = [['Read the separate reviewer guide. Work alone; return this first-pass file before discussing any post. Use only saved text. Yellow columns are for your answers.']];
  sh.getRange('A3:Q3').format.font = { name: 'Arial', size: 10, italic: true, color: '#475569' };
  sh.getRange('A5:Q5').values = [columns];
  sh.getRange('A5:Q5').format = {
    fill: '#1F4E78',
    font: { name: 'Arial', size: 10, bold: true, color: '#FFFFFF' },
    rowHeight: 28,
    verticalAlignment: 'center',
  };
  const matrix = rows.map(r => [r.review_id, r.title, r.post_body, r.discussion_context, ...Array(13).fill(null)]);
  sh.getRange('A6:Q205').values = matrix;
  sh.getRange('A6:Q205').format.font = { name: 'Arial', size: 10, color: '#1F2937' };
  sh.getRange('A6:Q205').format.rowHeight = 30;
  sh.getRange('A6:A205').format.columnWidth = 14;
  sh.getRange('B6:B205').format.columnWidth = 58;
  sh.getRange('C6:C205').format.columnWidth = 90;
  sh.getRange('D6:D205').format.columnWidth = 68;
  sh.getRange('E6:F205').format.columnWidth = 19;
  sh.getRange('G6:G205').format.columnWidth = 27;
  sh.getRange('H6:H205').format.columnWidth = 16;
  sh.getRange('I6:I205').format.columnWidth = 55;
  sh.getRange('J6:Q205').format.columnWidth = 21;
  sh.getRange('E6:Q205').format.fill = '#FFF4C2';
  sh.getRange('A5:Q205').format.verticalAlignment = 'center';
  sh.getRange('A5:Q5').format.horizontalAlignment = 'center';
  sh.freezePanes.freezeRows(5);
  sh.freezePanes.freezeColumns(2);
  sh.getRange('E6:F205').dataValidation = {rule:{type:'list',values:['yes','no','unclear']}};
  sh.getRange('G6:G205').dataValidation = {rule:{type:'list',values:['technical_troubleshooting','general_dissatisfaction','other','na']}};
  sh.getRange('H6:H205').dataValidation = {rule:{type:'list',values:['high','medium','low']}};
  sh.getRange('J6:Q205').dataValidation = {rule:{type:'list',values:['present','not_observed','unclear']}};
  wb.recalculate();
  const check = await wb.inspect({kind:'region',sheetId:sh.sheetId,range:'A5:J7',maxChars:1500});
  console.log(`Reviewer ${letter} inspect: ${check.ndjson.slice(0,1500)}`);
  const preview = await wb.render({sheetName:'Review',range:'A1:I8',scale:1,format:'png'});
  await fs.writeFile(path.join(here,`reviewer_${letter}_preview.png`),new Uint8Array(await preview.arrayBuffer()));
  const output = await SpreadsheetFile.exportXlsx(wb);
  const dest = path.join(here,`Reviewer_${letter}_Independent_200_Blank.xlsx`);
  await output.save(dest);
  console.log(dest);
}

await build('A');
await build('B');
