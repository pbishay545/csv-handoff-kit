import csv
import tempfile
import unittest
from pathlib import Path
from cleanup import COLUMNS, clean, run, spreadsheet_text


def row(**changes):
    result = dict(zip(COLUMNS, ['0001', 'Demo', '2026-10-01', '0', '0.00', 'pending', 'North', '']))
    result.update(changes)
    return result


class CleanupTests(unittest.TestCase):
    def test_conservation_and_demo_expectations(self):
        with Path('sample.csv').open(newline='', encoding='utf-8') as f:
            result = clean(list(csv.DictReader(f)))
        self.assertEqual(result['summary']['input_rows'], 12)
        self.assertEqual(result['summary']['output_rows'], 10)
        self.assertEqual(result['summary']['removed_rows'], 2)
        self.assertEqual(result['summary']['review_rows'], 7)
        self.assertEqual({r['source_row'] for r in result['rows']} | {r['source_row'] for r in result['removed']}, set(range(2, 14)))

    def test_identifiers_zero_and_uncertainty(self):
        result = clean([row(), row(sku='0002', order_date='03/04/2026', unit_price='1,234')])
        self.assertEqual(result['rows'][0]['data']['sku'], '0001')
        self.assertEqual(result['rows'][0]['data']['quantity'], '0')
        self.assertEqual(result['rows'][0]['flags'], [])
        self.assertEqual(result['rows'][1]['data']['order_date'], '03/04/2026')
        self.assertEqual(result['rows'][1]['data']['unit_price'], '1,234')
        self.assertEqual(len(result['rows'][1]['flags']), 2)

    def test_conflicts_are_never_collapsed_by_identifier(self):
        result = clean([row(), row(quantity='2'), row(quantity='2')])
        self.assertEqual(len(result['rows']), 2)
        self.assertTrue(all('conflicting' in r['flags'][0] for r in result['rows']))
        self.assertEqual(result['removed'][0]['kept_source_row'], 3)

    def test_malformed_rows_rejected(self):
        with self.assertRaises(ValueError):
            clean([row(notes=None)])
        with self.assertRaises(ValueError):
            clean([{**row(), None: ['extra']}])

    def test_source_preservation_and_no_overwrite(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent.resolve(), prefix='test-run-') as tmp:
            source = Path(tmp) / 'source.csv'
            with source.open('w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=COLUMNS)
                writer.writeheader()
                writer.writerow(row(notes='=1+1'))
            before = source.read_bytes()
            target = Path(tmp) / 'result'
            result = run(source, target)
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual((target / 'original.csv').read_bytes(), before)
            self.assertEqual(result['rows'][0]['data']['notes'], '=1+1')
            self.assertEqual(len(result['export_events']), 1)
            with (target / 'cleaned.csv').open(encoding='utf-8-sig', newline='') as f:
                self.assertEqual(next(csv.DictReader(f))['notes'], "'=1+1")
            with self.assertRaises(FileExistsError):
                run(source, target)

    def test_formula_trigger_export(self):
        for value in ('=1+1', '+CMD', '-CMD', '@SUM(A1)', ' \t=1'):
            self.assertTrue(spreadsheet_text(value).startswith("'"))
        self.assertEqual(spreadsheet_text('0001'), '0001')

    def test_target_job_scale(self):
        result = clean([row(sku=f'{i:08d}') for i in range(1321)])
        self.assertEqual(result['summary']['output_rows'], 1321)
        self.assertEqual(result['summary']['removed_rows'], 0)
        self.assertEqual(result['summary']['review_rows'], 0)


if __name__ == '__main__':
    unittest.main()
