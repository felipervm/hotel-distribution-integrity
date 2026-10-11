# Hotel Distribution Integrity

### Every channel. One consistent promise.

**An independent hospitality operations study by Felipe Mattos**

[**Explore the interactive case study →**](https://felipervm.github.io/hotel-distribution-integrity/)

A guest sees a room, a price, and a set of booking conditions. Behind that simple experience, information travels across hotel websites, travel agencies, reservation systems, and distribution partners.

**What happens when those channels don't show the same information?**

That question inspired this project.

I wanted to explore a part of hospitality that guests rarely see: the work involved in keeping room rates, availability, and booking conditions understandable and consistent across different places where a reservation can begin.

This is an **independent learning and portfolio project**, not work commissioned by a hotel. All data and properties in the study are fictional. I did not use Four Seasons data or access OPERA, SynXis, GDS, or other live hotel systems.

---

## The question behind the project

Imagine a room listed at **CAD 650** in a hotel's central reference, but **CAD 625** on another booking channel.

At first glance, it looks like a mistake. But it might be a legitimate promotion, a different tax treatment, or another commercial arrangement.

The useful question isn't simply *“Are these numbers different?”* It's:

> **“Are we comparing the same offer — and what should we check before deciding something is wrong?”**

That distinction shaped the entire study.

## What I built

I created a small fictional hotel-distribution environment: **two room types, seven stay dates, four booking channels, and a central reference**.

Then I built a Python audit to compare each channel with that reference. It checks room rates, availability, cancellation windows, and whether a reservation is marked as bookable. Importantly, it checks that commercial conditions match *before* treating two prices as directly comparable.

The audit produces a review register. Rather than declaring that a channel is broken, each case explains **what was noticed, why it matters, who might investigate, and what evidence would be needed next**.

Finally, I built an interactive website that lets someone explore the study without needing to read Python code.

[**Open the study and explore the cases →**](https://felipervm.github.io/hotel-distribution-integrity/)

## What the exercise showed

| In this fictional dataset | Result |
| --- | ---: |
| Source records | **70** |
| Channel-to-reference comparisons | **56** |
| Comparisons aligned on the modeled fields | **51** |
| Cases requiring review | **5** |
| Cases routed as high priority | **2** |

These numbers describe a deliberately designed teaching scenario. They are **not measurements of a real hotel's distribution accuracy**, nor evidence of actual business impact.

The five cases helped me explore several different kinds of questions:

- **A different price:** Is the offer genuinely comparable, or are taxes, promotions, or conditions different?
- **Different availability:** Could allotments, restrictions, or the timing of updates explain the mismatch?
- **A different cancellation window:** Which published policy should be verified, and where?
- **A bookability difference:** Does an available room actually have a working path to reservation?

One of the most important lessons was that **a difference is a reason to investigate, not proof of an error**. A useful audit needs to preserve uncertainty rather than hide it.

## How I approached the work

I organized the process around four steps:

**1. Make the records comparable.** Check the dates, room types, rate plans, commercial conditions, and validity of each record.

**2. Look for differences.** Compare each channel with the fictional central reference, but only compare prices directly when the offers have equivalent terms.

**3. Ask what is still unknown.** Identify the additional information an actual distribution team would need — such as synchronized captures, mapping rules, restrictions, or policy wording.

**4. Make the next step clear.** Give each review case a suggested priority, team, and investigation action, without pretending it has already been resolved.

This approach connects data quality with practical operational judgment.

## Why I chose this topic

My background is in programming and data quality, and I am interested in how digital systems support real-world operations.

Hotel distribution stood out because even small details — a rate plan, a cancellation window, or a booking restriction — can matter to both the people running a hotel and the people trying to book a stay.

I built this project to learn more about those decisions and to show how I approach unfamiliar operational problems: **understand the context, check the data, recognize the limits, and communicate a useful next action**.

## Explore the work

- [**Interactive case study**](https://felipervm.github.io/hotel-distribution-integrity/) — the story, findings, and an example investigation.
- [**Full audit results (CSV)**](data/audit_results.csv) — all comparisons, including aligned rows.
- [**Synthetic source data (CSV)**](data/channel_snapshot.csv) — the fictional input records.
- [**Structured findings (JSON)**](data/report.json) — the report powering the website.
- [**Python audit**](src/audit.py) — the comparison and routing logic.
- [**Tests**](tests/) — checks for edge cases and consistency.

**Tools used:** Python for the audit; CSV and JSON to share results; HTML, CSS, and JavaScript for the interactive presentation; GitHub Pages to make the study accessible.

<details>
<summary><strong>For anyone who wants to reproduce the analysis</strong></summary>

Python 3.10+ is sufficient. From the repository root, run:

```bash
python src/audit.py
python -m unittest discover -s tests -v
```

The first command regenerates the structured report and CSV outputs from the synthetic snapshot. The second runs the regression tests.

To preview the website locally, serve the repository with a local HTTP server:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000/`. The page loads its data through HTTP rather than directly from a `file://` path.

</details>

## What this study cannot prove

This is one fictional property, with simplified one-night rates and a small number of pre-designed cases. It does not model every distribution rule, live synchronization, actual booking attempts, contractual arrangements, or the full complexity of hotel systems.

Even a well-structured finding cannot establish a real platform defect without operational evidence and confirmation by the relevant team.

The images on the site are original AI-created depictions of fictional architecture, not actual hotel properties. The site is independent and is **not affiliated with or endorsed by Four Seasons Hotels and Resorts or any hotel system provider**.

---

### About the author

**Felipe Mattos**

I study programming and data analysis and enjoy making complex information easier to understand and act on.

[Explore the website](https://felipervm.github.io/hotel-distribution-integrity/) · [GitHub](https://github.com/felipervm) · [LinkedIn](https://www.linkedin.com/in/felipervm)
