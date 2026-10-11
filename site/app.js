'use strict';
const labels = {
  RATE_DIFFERENCE_REVIEW: 'Comparable rate difference',
  AVAILABILITY_DIFFERENCE_REVIEW: 'Availability difference',
  CANCELLATION_POLICY_REVIEW: 'Cancellation policy review',
  BOOKABILITY_REVIEW: 'Bookability review',
  INCOMPARABLE_RATE_BASIS: 'Incomparable commercial basis',
  MISSING_REFERENCE: 'Missing reference'
};
const channels = {OFFICIAL_WEB: 'Hotel website', GDS: 'GDS', OTA_A: 'OTA A', OTA_B: 'OTA B'};
const fields = {nightly_rate: 'Nightly rate', availability: 'Available rooms', cancel_window_hours: 'Cancellation window', bookable: 'Bookable', currency: 'Currency', occupancy: 'Occupancy', meal_plan: 'Meal plan', tax_basis: 'Tax basis', promotion_code: 'Promotion'};
const priority = document.querySelector('#priority');
const category = document.querySelector('#category');
const register = document.querySelector('#exceptions');
let findings = [];
function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}
function dateLabel(date) {
  return new Intl.DateTimeFormat('en', {day: '2-digit', month: 'short', timeZone: 'UTC'}).format(new Date(date + 'T00:00:00Z'));
}
function value(row, field) {
  if (!row) return 'Unavailable';
  if (field === 'nightly_rate') return `${row.currency} ${Number(row[field]).toLocaleString('en', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
  if (field === 'cancel_window_hours') return `${row[field]} hours`;
  return row[field];
}
function issueTitle(row) { return row.issues.split(' | ').map(issue => labels[issue] || issue).join(' / '); }
function comparison(row) {
  const table = el('table', undefined, 'comparison');
  const caption = el('caption', 'Synthetic central reference and channel observation');
  caption.className = 'visually-hidden';
  table.append(caption);
  const head = el('thead'), hr = el('tr');
  ['Field', 'Central reference', 'Channel observation'].forEach(text => hr.append(el('th', text)));
  head.append(hr); table.append(head);
  const body = el('tbody');
  Object.entries(fields).forEach(([field, label]) => {
    const tr = el('tr');
    const th = el('th', label); th.scope = 'row';
    tr.append(th, el('td', value(row.reference, field)), el('td', value(row, field)));
    body.append(tr);
  });
  table.append(body); return table;
}
function caseNode(row) {
  const details = el('details', undefined, 'case');
  const summary = el('summary');
  const time = el('time', dateLabel(row.stay_date), 'case-date'); time.dateTime = row.stay_date;
  const title = el('span', issueTitle(row), 'case-title');
  title.append(el('span', `${row.room_type} · ${row.rate_plan}`, 'case-room'));
  const arrow = el('span', '+', 'case-arrow'); arrow.setAttribute('aria-hidden', 'true');
  summary.append(time, title, el('span', channels[row.channel] || row.channel, 'case-channel'), el('span', row.priority, `priority ${row.priority.toLowerCase()}`), arrow);
  details.append(summary);
  const body = el('div', undefined, 'case-body');
  body.append(el('p', `${row.stay_date} · ${row.room_type} · Rate code ${row.rate_plan} · Status: ${row.review_status}`, 'case-meta'), comparison(row));
  const basis = !row.reference ? 'No central reference: comparison is inconclusive.' : row.basis_differences.length ? `Rate basis differs: ${row.basis_differences.map(key => fields[key]).join(', ')}. No comparable rate delta is calculated. Normalize terms before interpretation.` : `The modeled currency, occupancy, meals, tax, and promotion basis match.${row.rate_delta !== null && row.rate_delta !== '0' ? ` Channel minus reference: ${row.currency} ${row.rate_delta}.` : ''} Matching fixture terms still require operational verification.`;
  body.append(el('p', basis, 'case-notice'));
  const grid = el('div', undefined, 'handoff-grid');
  const owner = el('div'); owner.append(el('h4', 'Suggested operational owner'), el('p', row.assigned_team), el('h4', 'Recommended next action'), el('p', row.next_action));
  const evidence = el('div'); evidence.append(el('h4', 'Evidence required — not supplied by this fixture'));
  const list = el('ul'); row.evidence_required.forEach(text => list.append(el('li', text))); evidence.append(list);
  grid.append(owner, evidence); body.append(grid); details.append(body); return details;
}
function render() {
  const visible = findings.filter(row => (priority.value === 'ALL' || row.priority === priority.value) && (category.value === 'ALL' || row.issues.split(' | ').includes(category.value)));
  register.replaceChildren(...visible.map(caseNode));
  if (!visible.length) register.append(el('p', 'No review cases match these filters.', 'error'));
  document.querySelector('#shown-count').textContent = `${visible.length} of ${findings.length} review cases`;
}
function scenario(row) {
  const container = document.querySelector('#scenario-content'); container.replaceChildren();
  if (!row) {container.append(el('p', 'No incomparable-rate-basis case is present in the current dataset.')); return;}
  const values = el('div', undefined, 'scenario-values');
  [row.reference, row].forEach((record, index) => {
    const block = el('div'); block.append(el('small', index ? `${channels[row.channel]} · OBSERVATION` : 'CENTRAL · REFERENCE'), el('strong', value(record, 'nightly_rate')), el('p', `${record.tax_basis} · ${row.room_type} · ${row.stay_date}`)); values.append(block);
  }); container.append(values);
  const narrative = el('div', undefined, 'scenario-narrative');
  const notes = [
    ['01 / Establish the basis', `Both rows share the stay date, room, ${row.rate_plan} rate plan, currency, occupancy, meal plan, and promotion. Tax basis differs. The rates are not directly comparable.`],
    ['02 / Preserve the uncertainty', 'Classification: incomparable commercial basis. No like-for-like rate delta is calculated. Obtain tax breakdowns, all-in prices, capture times, and mapping evidence before deciding whether a defect exists.'],
    ['03 / Route the next review', `${row.priority} priority · ${row.assigned_team}. ${row.next_action} Status remains ${row.review_status}; no operational resolution is established.`]
  ]; notes.forEach(([title, text]) => {const block = el('article'); block.append(el('h3', title), el('p', text)); narrative.append(block);}); container.append(narrative);
}
priority.addEventListener('change', render); category.addEventListener('change', render);
async function load() {
  try {
    const response = await fetch('data/report.json');
    if (!response.ok) throw new Error('Report unavailable');
    const report = await response.json();
    if (report.synthetic !== true || !Array.isArray(report.findings) || !report.metrics) throw new Error('Invalid report');
    findings = report.findings;
    document.querySelectorAll('[data-metric]').forEach(node => {node.textContent = report.metrics[node.dataset.metric];});
    const categories = [...new Set(findings.flatMap(row => row.issues.split(' | ')))];
    categories.forEach(key => {const option = el('option', labels[key] || key); option.value = key; category.append(option);});
    render(); scenario(findings.find(row => row.issues.includes('INCOMPARABLE_RATE_BASIS')));
  } catch (error) {
    register.replaceChildren(el('p', 'The synthetic report could not be loaded. Please reload or use the CSV below.', 'error'));
    const link = el('a', 'Open the complete audit CSV'); link.href = 'data/audit_results.csv'; register.append(link);
    document.querySelector('#shown-count').textContent = 'Report unavailable';
    document.querySelector('#scenario-content').textContent = 'The scenario is unavailable until the report loads.';
    priority.disabled = true; category.disabled = true;
  } finally { register.setAttribute('aria-busy', 'false'); }
}
load();
if (!matchMedia('(prefers-reduced-motion: reduce)').matches && 'IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {entries.forEach(entry => {if (entry.isIntersecting) {entry.target.classList.add('reveal'); observer.unobserve(entry.target);}});}, {threshold: .08});
  document.querySelectorAll('.editorial, .stats, .steps').forEach(node => observer.observe(node));
}
