import unittest
from src.audit import read_snapshot,audit

class DistributionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=read_snapshot()
        cls.results=audit(cls.rows)
        cls.flags=[r for r in cls.results if r["issue_count"]]

    def test_snapshot_size(self):
        self.assertEqual(len(self.rows),70)
        self.assertEqual(len(self.results),56)

    def test_five_review_cases(self):
        self.assertEqual(len(self.flags),5)

    def test_all_findings_have_handoff(self):
        self.assertTrue(all(r["assigned_team"] and r["next_action"] for r in self.flags))

    def test_tax_incomparable_not_rate_violation(self):
        case=next(r for r in self.flags if r["issues"]=="INCOMPARABLE_RATE_BASIS")
        self.assertNotIn("RATE_DIFFERENCE_REVIEW",case["issues"])

    def test_high_priority_bookability(self):
        case=next(r for r in self.flags if r["issues"]=="BOOKABILITY_REVIEW")
        self.assertEqual(case["priority"],"HIGH")

    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            # duplicate validation is performed by read_snapshot; see source fixture
            import csv,tempfile,os
            with tempfile.NamedTemporaryFile(mode="w",suffix=".csv",delete=False,newline="") as f:
                path=f.name
                with open("data/channel_snapshot.csv",newline="") as source:
                    f.write(source.read())
                writer=csv.DictWriter(f,fieldnames=list(self.rows[0]))
                writer.writerow(self.rows[0])
            try: read_snapshot(path)
            finally: os.unlink(path)

    def test_missing_reference_review(self):
        rows=[r for r in self.rows if not (r["channel"]=="CENTRAL_REFERENCE" and r["stay_date"]=="2026-11-01")]
        self.assertTrue(any("MISSING_REFERENCE" in r["issues"] for r in audit(rows)))

if __name__=="__main__":unittest.main()
