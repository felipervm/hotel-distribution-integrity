# Hotel Distribution Integrity

[Explore the live case study](https://felipervm.github.io/hotel-distribution-integrity/)

An independent proof of work by **Felipe Mattos**, exploring how structured data checks and operational judgment can support hotel distribution review. The static editorial site pairs an interactive exception register with a reproducible Python audit.

**All data are synthetic. No affiliation with Four Seasons, any hotel, or any hotel-system vendor. No internal data or system integrations were accessed.**

## The operational question

A channel difference is not automatically a defect. Which differences deserve investigation, what evidence is missing, and who should take the next step?

The study checks rate integrity, availability alignment, cancellation windows, and bookability. It deliberately distinguishes aligned comparisons, review cases, incomparable commercial terms, and high-priority routing cases. It does not claim financial impact, guest harm, parity violations, or confirmed platform defects.

## Dataset and evidence

`data/channel_snapshot.csv` contains 70 authored records: seven stay dates, two rooms, one BAR rate plan, a modeled central reference, and four fictional distribution channels. The fixture has 56 channel comparisons, 51 aligned rows, and five open review cases. One has an incomparable tax basis; two receive high-priority routing.

- `data/audit_results.csv`: every comparison, including aligned rows; working download and operational handoff.
- `data/findings.json`: the original compact review-case output, preserved for compatibility.
- `data/report.json`: data-derived metrics, review cases, matched references, comparable rate deltas, and required evidence. Drives the website.

Evidence checklists describe what would need to be collected; they are not evidence of a completed investigation.

## Method

1. **Normalize:** validate required fields, ISO dates, finite non-negative decimal rates, integer inventory and cancellation windows, positive occupancy, and Yes/No bookability. Reject duplicate stay/room/rate-plan/channel keys.
2. **Compare:** match stay date, room type, and rate plan. Compare rates only when currency, occupancy, meals, taxes, and promotion match. Use `Decimal`, not floating-point money. Independently review inventory, cancellation windows, and booking flags.
3. **Investigate:** preserve the reference and observation. Missing references are inconclusive. Different tax or promotion terms prevent direct rate comparison; no normalized tax amount is invented.
4. **Route:** choose the highest issue priority and its suggested owner/action. Inventory, bookability, and missing-reference cases are high; rates, policies, and commercial-basis reviews are medium. This is a stated heuristic, not measured impact. Cases remain open for human review.

## Reproduce and test

Python 3.10+; standard library only. Run from the repository root:

```sh
python src/audit.py
python -m unittest discover -s tests -v
```

The audit regenerates all three output files deterministically. Tests cover fixture findings, handoffs, precision, non-finite rates, invalid records, duplicate baselines, matching keys, every commercial-basis field, missing references, priority, and agreement between source, JSON, and CSV.

## Preview and GitHub Pages

No build step, dependencies, backend, or authentication.

```sh
python -m http.server 8000
```

Open `http://localhost:8000/`. Use an HTTP server: the interactive page fetches local JSON and is not intended to run from a `file://` URL.

For GitHub Pages, serve **main / root** in repository Settings → Pages. Relative CSS, JavaScript, SVG, JSON, and CSV paths support the project URL above. Existing Pages settings are not changed by the source implementation.

The interface offers native keyboard-accessible expandable cases, combined priority/category filters, loading/error/empty states, visible focus, responsive layouts, and reduced-motion support. All content remains available without scroll animation; CSV evidence remains accessible without JavaScript.

## Visual provenance

`site/architecture.svg` and `site/mark.svg` are original code-authored artwork created for this project. The architectural scene is fictional, not a photograph or depiction of a Four Seasons property. No proprietary photography or logo is used. Cormorant Garamond and Inter are self-hosted under the SIL Open Font License; license files are included in `site/fonts/`. System fallbacks keep the page usable while fonts load. No external font requests are made.

Design research: [Tengile MalaMala](https://tengilemalamala.com/), [Four Seasons](https://www.fourseasons.com/), [Toronto property](https://www.fourseasons.com/toronto/), [Magazine](https://www.fourseasons.com/magazine/), [Press Room](https://press.fourseasons.com/), and [public LinkedIn](https://www.linkedin.com/company/four-seasons-hotels-and-resorts/). Official Instagram could not be inspected because its public endpoint returned a rate-limit error. References informed editorial pacing and hospitality tone; their assets were not copied.

## Limitations and next validation

One fictional property; one-night rates; no timestamps, multi-night pricing, effective dates, conversion, contract logic, or real mapping catalog. Room and rate identifiers must already match. No whitespace/case or alias normalization is attempted because that needs validated mapping rules. Cancellation windows are numeric checks, not full policy interpretation. Availability differences may reflect valid allotments, restrictions, or capture timing. Bookability flags do not reproduce a booking path.

A production implementation would require property-aware and occupancy-aware matching, authorized access, synchronized captures, validated mappings, tax/promotion normalization, commercial agreements, policy-text review, and operational sign-off. Exact monetary differences are review signals, not automatic corrections. This static site is not a live distribution or case-management system.

## Author

[Felipe Mattos on LinkedIn](https://www.linkedin.com/in/felipervm) · [GitHub repository](https://github.com/felipervm/hotel-distribution-integrity)

Independent candidate portfolio study; not client consulting work, an official Four Seasons site, or evidence of hospitality-platform employment.
