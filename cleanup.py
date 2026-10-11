"""Conservative CSV demonstration. No network access or third-party dependencies."""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from decimal import Decimal
from pathlib import Path

COLUMNS = ['sku', 'item_name', 'order_date', 'quantity', 'unit_price', 'status', 'region', 'notes']
STATUS = {'pending': 'Pending', 'shipped': 'Shipped', 'cancelled': 'Cancelled'}


def clean(rows):
    """Rules apply only to this agreed demo schema. Preserve uncertain values."""
    retained, events, removed, seen = [], [], [], {}
    for source_row, original in enumerate(rows, 2):
        if set(original) != set(COLUMNS) or any(v is None for v in original.values()):
            raise ValueError(f'Malformed CSV record at source row {source_row}')
        if not any(v.strip() for v in original.values()):
            removed.append({'source_row': source_row, 'reason': 'empty row'})
            continue
        record = {k: v.strip() for k, v in original.items()}
        flags = []
        for col in COLUMNS:
            value = record[col]
            if col == 'order_date' and value:
                parsed = None
                for fmt in ('%Y-%m-%d', '%d %b %Y'):
                    try:
                        parsed = datetime.strptime(value, fmt).date().isoformat()
                        break
                    except ValueError:
                        pass
                if parsed is None:
                    flags.append('order_date: invalid or unapproved date format')
                else:
                    record[col] = parsed
            if col in ('quantity', 'unit_price') and value:
                pattern = r'[0-9]+' if col == 'quantity' else r'[0-9]+(?:\.[0-9]+)?'
                if not re.fullmatch(pattern, value):
                    flags.append(f'{col}: requires nonnegative {"integer" if col == "quantity" else "decimal with dot"}')
                else:
                    record[col] = str(int(value)) if col == 'quantity' else format(Decimal(value), 'f')
            if col == 'status' and value:
                if value.lower() in STATUS:
                    record[col] = STATUS[value.lower()]
                else:
                    flags.append('status: unmapped value')
            if record[col] != original[col]:
                events.append({'source_row': source_row, 'column': col,
                               'before': original[col], 'after': record[col]})
        for col in ('sku', 'item_name', 'order_date', 'quantity', 'unit_price', 'status', 'region'):
            if not record[col]:
                flags.append(f'{col}: missing required value')
        key = tuple(record[col] for col in COLUMNS)
        if key in seen:
            removed.append({'source_row': source_row, 'reason': 'duplicate after agreed normalization',
                            'kept_source_row': seen[key]})
            continue
        seen[key] = source_row
        retained.append({'source_row': source_row, 'data': record, 'flags': flags})
    counts = Counter(r['data']['sku'] for r in retained if r['data']['sku'])
    for row in retained:
        if counts[row['data']['sku']] > 1:
            row['flags'].append('sku: conflicting records retained for review')
    return {'rows': retained, 'changes': events, 'removed': removed,
            'summary': {'input_rows': len(rows), 'output_rows': len(retained),
                        'removed_rows': len(removed),
                        'review_rows': sum(bool(r['flags']) for r in retained),
                        'changed_cells': len(events)}}


def spreadsheet_text(value):
    # CSV is an interchange format. Escape formula triggers for spreadsheet use.
    return "'" + value if value.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')) else value


def run(source, target):
    source, target = Path(source), Path(target)
    raw = source.read_bytes()
    with source.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle, strict=True)
        if reader.fieldnames != COLUMNS:
            raise ValueError('Header must match the eight demo columns in the agreed order')
        rows = list(reader)
    result = clean(rows)
    result['source_rows'] = rows
    result['source_sha256'] = hashlib.sha256(raw).hexdigest()
    # A new directory is mandatory to prevent source or previous-output overwrite.
    target.mkdir(parents=True, exist_ok=False)
    export_events = []
    with (target / 'cleaned.csv').open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=['source_row'] + COLUMNS + ['review'])
        writer.writeheader()
        for row in result['rows']:
            values = {key: spreadsheet_text(value) for key, value in row['data'].items()}
            for key in COLUMNS:
                if values[key] != row['data'][key]:
                    export_events.append({'source_row': row['source_row'], 'column': key,
                                          'reason': 'formula trigger escaped for spreadsheet export'})
            writer.writerow({'source_row': row['source_row'], **values, 'review': '; '.join(row['flags'])})
    result['export_events'] = export_events
    (target / 'audit.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    # Raw source is copied byte for byte, without decoding or formula evaluation.
    (target / 'original.csv').write_bytes(raw)
    assert result['summary']['input_rows'] == result['summary']['output_rows'] + result['summary']['removed_rows']
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('new_output_directory')
    args = parser.parse_args()
    result = run(args.source, args.new_output_directory)
    print(json.dumps(result['summary']))
