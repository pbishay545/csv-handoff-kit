import csv
import tempfile
import unittest
from pathlib import Path
from cleanup import COLUMNS, run


class FullWidthExportTests(unittest.TestCase):
    def test_fullwidth_values_are_preserved_and_export_escaped(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            source = Path(folder) / 'synthetic.csv'
            values = ['＝1+2', '＋1+2', '－1+2', '＠SUM(1,2)']
            with source.open('w', encoding='utf-8', newline='') as handle:
                writer = csv.DictWriter(handle, fieldnames=COLUMNS)
                writer.writeheader()
                for index, value in enumerate(values):
                    writer.writerow(dict(zip(COLUMNS, [str(index), 'Demo', '2026-10-11',
                                                       '1', '0', 'pending', 'North', value])))
            before = source.read_bytes()
            target = Path(folder) / 'result'
            result = run(source, target)
            self.assertEqual((target / 'original.csv').read_bytes(), before)
            self.assertEqual([row['data']['notes'] for row in result['rows']], values)
            self.assertEqual(len(result['export_events']), 4)
            with (target / 'cleaned.csv').open(encoding='utf-8-sig', newline='') as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual([row['notes'] for row in rows], ["'" + value for value in values])


if __name__ == '__main__':
    unittest.main()
