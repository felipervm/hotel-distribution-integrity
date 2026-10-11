import csv
import json
import unittest
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
from src.audit import audit, build_report, money, read_snapshot

class AuditRegressionTests(unittest.TestCase):
    def setUp(self):
        self.rows = read_snapshot()

    def test_nonfinite_and_negative_money_rejected(self):
        for value in ('NaN', 'Infinity', '-Infinity', '-0.01', 'invalid'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                money(value)

    def test_decimal_precision_is_preserved(self):
        rows = deepcopy(self.rows[:2])
        rows[0]['nightly_rate'] = '650.000000000000000001'
        rows[1]['nightly_rate'] = '650.000000000000000002'
        self.assertEqual(audit(rows)[0]['issues'], 'RATE_DIFFERENCE_REVIEW')
        self.assertEqual(money('650.00'), Decimal('650'))

    def test_duplicate_reference_cannot_silently_overwrite(self):
        with self.assertRaises(ValueError):
            audit(self.rows + [deepcopy(self.rows[0])])

    def test_invalid_fields_are_rejected(self):
        for key, value in [('availability', '-1'), ('availability', '1.5'),
                           ('cancel_window_hours', '-1'), ('occupancy', '0'),
                           ('bookable', 'Maybe'), ('stay_date', '2026-02-30'),
                           ('room_type', ''), ('nightly_rate', 'NaN')]:
            rows = deepcopy(self.rows)
            rows[0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                audit(rows)

    def test_room_and_rate_plan_keys_do_not_cross_match(self):
        rows = deepcopy(self.rows[:2])
        rows[1]['rate_plan'] = 'ADVANCE'
        self.assertEqual(audit(rows)[0]['issues'], 'MISSING_REFERENCE')
        rows[1]['rate_plan'] = 'BAR'
        rows[1]['room_type'] = 'Other room'
        self.assertEqual(audit(rows)[0]['issues'], 'MISSING_REFERENCE')

    def test_each_commercial_basis_difference_blocks_rate_delta(self):
        for key, value in [('currency', 'USD'), ('occupancy', '3'), ('meal_plan', 'Breakfast'),
                           ('tax_basis', 'After tax'), ('promotion_code', 'MEMBER')]:
            rows = deepcopy(self.rows[:2])
            rows[1][key] = value
            rows[1]['nightly_rate'] = '710'
            with self.subTest(key=key):
                result = audit(rows)
                self.assertEqual(result[0]['issues'], 'INCOMPARABLE_RATE_BASIS')
                self.assertIsNone(build_report(rows, result)['findings'][0]['rate_delta'])

    def test_highest_priority_wins_with_multiple_issues(self):
        rows = deepcopy(self.rows[:2])
        rows[1].update(tax_basis='After tax', availability='0', bookable='No')
        result = audit(rows)[0]
        self.assertEqual(result['priority'], 'HIGH')
        self.assertEqual(result['issue_count'], 3)
        self.assertIn('connectivity', result['assigned_team'])

    def test_report_missing_reference_stays_inconclusive(self):
        rows = [deepcopy(self.rows[1])]
        case = build_report(rows, audit(rows))['findings'][0]
        self.assertIsNone(case['reference'])
        self.assertIsNone(case['rate_delta'])
        self.assertEqual(case['review_status'], 'OPEN')

    def test_generated_files_agree_with_source(self):
        results = audit(self.rows)
        data = Path('data')
        self.assertEqual(json.loads((data / 'report.json').read_text()), build_report(self.rows, results))
        self.assertEqual(json.loads((data / 'findings.json').read_text()), [r for r in results if r['issue_count']])
        with (data / 'audit_results.csv').open(newline='') as file:
            csv_rows = list(csv.DictReader(file))
        self.assertEqual(csv_rows, [{k: str(v) for k, v in r.items()} for r in results])
        self.assertEqual(build_report(self.rows, results)['metrics'], {
            'source_records': 70, 'comparisons': 56, 'aligned': 51,
            'review_cases': 5, 'incomparable': 1, 'high_priority': 2})

if __name__ == '__main__':
    unittest.main()
