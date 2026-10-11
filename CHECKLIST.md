# Before you hand off a cleaned CSV

Use this checklist to make a cleanup understandable and reversible.

## 1. Agree the rules

- Identify the source, owner, permitted use and recipient.
- Write down the target columns, required fields, encoding and delimiter.
- Treat IDs, postal codes and account numbers as text, even if they contain only digits.
- Specify date order, timezone if relevant, currency, decimal separator and rounding.
- Define exactly what makes two records duplicates. Sharing an identifier alone does not prove duplication.
- Decide which uncertain values require a human decision. Keep those records visible.

## 2. Preserve and trace

- Preserve an unchanged source copy; record its SHA-256 hash.
- Work in a new output folder.
- Give every retained or removed record a source reference. CSV record numbers can differ from physical lines when quoted fields contain newlines.
- Record changes as before/after values and explain every removal.
- Keep semantic values separate from spreadsheet export escapes.

## 3. Verify the result

- Reconcile input records = retained records + removed records.
- Check complete duplicates separately from conflicting records with the same ID.
- Inspect IDs with leading zeros, long identifiers, zero values and ambiguous dates.
- Check formula-like text without executing it. A prefix escape is a defense for this export, not a universal guarantee across spreadsheet applications.
- Import the output with explicit column types in the intended destination. Recheck identifiers after import and after any round trip.
- Review unresolved records before using the data for billing, inventory or decisions.

## 4. Deliver a readable handoff

Include the agreed rules, source hash, row reconciliation, change/removal counts, review queue and import instructions. Keep private source values and audit files within the agreed sharing boundary.

Suggested handoff note:

```text
Source: [file and SHA-256]
Rules applied: [agreed rule list]
Records: [input] = [retained] + [removed]
Changes: [count and summary]
Needs review: [count and reason groups]
Import: [column types and destination]
Unresolved: [questions requiring the owner's decision]
```

## Why explicit import matters

Microsoft documents leading-zero removal and conversion of long numbers when Excel treats them as numeric data. Use controlled text/CSV import and set identifier columns to Text. Available conversion settings depend on the Excel version; verify the actual destination rather than assuming settings are present.

Reference: [Microsoft: keeping leading zeros and large numbers](https://support.microsoft.com/en-us/excel/keeping-leading-zeros-and-large-numbers). Checked 2026-10-11.
