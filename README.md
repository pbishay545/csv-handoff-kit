# CSV Handoff Kit — 0.1

A worked example for developers who need to explain a CSV cleanup, preserve identifiers, and give the recipient a reviewable change record.

The download contains a short handoff checklist, fictional input, a standard-library Python cleaner, and seven regression tests. Run it locally: no account, upload, API key or package install required. Python 3.9+ is required; the included preview has been tested on Python 3.12.

## Try it in five minutes

Unzip the download. Open a terminal in its folder, then run:

```text
python -m unittest -v test_cleanup.py
python cleanup.py sample.csv first-run
```

On Windows, `py` may replace `python` if that is how Python is installed. Use a new output folder for each run.

The sample contains 12 fictional input rows. Expected result: 10 retained, 2 removed, 7 requiring review, 15 changed cells. `first-run/` contains:

| File | What to check |
| --- | --- |
| original.csv | Exact source-byte copy; compare with sample.csv |
| cleaned.csv | Source row references, normalized values and review flags |
| audit.json | Source hash, cell changes, removals, retained records and export escapes |

Open `cleaned.csv` using your spreadsheet's controlled text/CSV import. Set identifier columns such as `sku` to Text. A CSV cannot carry spreadsheet cell types, so double-clicking the file may convert `0001` to `1`. See the linked Microsoft guidance in CHECKLIST.md.

## What the example actually supports

The exact header is:

```text
sku,item_name,order_date,quantity,unit_price,status,region,notes
```

It trims surrounding whitespace, normalizes ISO dates and dates like `02 Oct 2026`, accepts nonnegative integer quantities and dot-decimal prices, and maps pending/shipped/cancelled statuses. It removes fully blank rows and complete duplicates after those rules. Different rows sharing a SKU remain flagged for review. Zero quantities and prices are valid.

Uncertain dates, unsupported numbers and missing values stay visible. Spreadsheet formula triggers are prefixed with an apostrophe in the cleaned export and recorded separately. The original byte copy is unchanged; import it as text rather than evaluating cells. No workbook, CRM, Shopify or arbitrary-schema integration is included.

The checklist applies more broadly; the code is a narrow educational sample. Agree real transformation rules before adapting it. The audit contains source values, so keep real-data outputs local and share only with their authorized recipient.

## Feedback that would help

If this becomes publicly released, please report whether you could run the sample, whether the row counts reconciled, and which handoff step remained unclear. Use fictional or redacted examples. The next version will be chosen from actual requests rather than guessed integrations.

## License and provenance

MIT licensed; see LICENSE. Created with AI assistance and tested against fictional data. This example demonstrates its stated rules; it does not claim customer use, certification or universal CSV support.
