# Hotel Distribution Integrity

Independent proof of work by Felipe Mattos. **Entirely synthetic data; no affiliation with Four Seasons, OPERA, SynXis, GDS vendors, or any hotel.**

[View the interactive case study](https://felipervm.github.io/hotel-distribution-integrity/)

## The operational question

Can a distribution specialist identify rate, inventory, cancellation-policy and bookability inconsistencies across hotel booking channels without mistaking legitimate commercial differences for defects?

The fictional fixture covers a central reference and four distribution channels. The comparison intentionally includes five review cases. **A flagged difference is not proof of a platform defect.** Review rate basis, taxes, promotion, effective dates, mapping and capture time before escalation.

## Run the analysis

Python 3.10+; standard library only.

```bash
python -m unittest discover -s tests -v
python src/audit.py
```

The HTML report on GitHub Pages loads `data/findings.json`. The Python script can regenerate it from `data/channel_snapshot.csv`. The Excel handoff workbook is distributed separately until the binary asset is attached to this repository.

## Limitations

These are invented rates and bookings, not production data. No OPERA, SynXis or GDS API access is implied. Snapshots don't establish causality, overselling, contractual parity, guest harm or financial impact. The study demonstrates issue triage and operational communication, not knowledge of a hotel's private configuration.
