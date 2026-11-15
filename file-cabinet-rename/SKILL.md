---
name: file-cabinet-rename
description: Rename existing files into the format `YYYY-MM-DD - FileSummary.ext` without changing file contents. Use when Codex needs to clean up a folder, standardize inconsistent filenames, rename only files that have not already been normalized, infer the most relevant document date, keep a short human-readable summary in the filename, or preserve the existing extension while lowercasing it.
---

# File Cabinet Rename

## Dependency preflight

Require an accessible scoped folder and host filesystem rename capability
or the OS `mv` command. Reading unclear document dates additionally needs a
working format reader/vision/OCR route. Verify required tools and target write
permissions before renaming. If they are missing, stop the affected rename
and report the dependency or date uncertainty; do not guess, overwrite, or
silently convert a file. No particular extractor or other skill is assumed.

## Overview

Rename files to a consistent cabinet-friendly format:

`YYYY-MM-DD - FileSummary.ext`

Operate on filenames only. Do not edit, convert, rewrite, resave, or otherwise change file contents.

Only operate on files that do not already fit the complete format. A filename starting with the current year is not enough to qualify.

## Format Check

Skip a file only when its name has all of the following:

1. A valid date prefix in exactly `YYYY-MM-DD - ` form, including the space, hyphen, and space after the date.
2. A nonempty, descriptive `FileSummary` following that prefix.
3. Its existing extension in lowercase, preserving the file type.

Apply this check regardless of the year. Incorrect separators, missing summaries, and uppercase or mixed-case extensions still require renaming.

Examples:

- `2000-01-15_scan.pdf` needs renaming: it lacks the exact ` - ` separator and a descriptive summary.
- `2000-01-15 - Bank Statement.PDF` needs renaming to `2000-01-15 - Bank Statement.pdf`.
- `1999-01-15 - Bank Statement.pdf` already fits, even though its date is not in the current year.

## Workflow

1. List candidate files in the requested scope.
2. Check the complete filename against Format Check; skip only files that satisfy it and do not need improvement.
3. For each remaining file, determine the most relevant date.
4. Write a short summary that identifies the document at a glance.
5. Rename with `mv` only after confirming the target name will not overwrite another file.

## Date Selection

Choose the date that is most relevant to the document itself, not the filesystem timestamp unless no better signal exists.

Prefer dates in this order:

1. Statement date, invoice date, service date, visit date, issue date, signed date, or letter date shown inside the document.
2. A reliable date already present in the filename.
3. Embedded metadata that clearly reflects the document date.
4. File modified or created date only as a last resort.

If a file contains multiple dates, choose the date a human would most likely use to file it later. Examples:

1. Use the statement closing date for bank statements.
2. Use the date of service for medical paperwork when that is the main anchor.
3. Use the invoice or receipt date for billing documents.
4. Use the letter date for notices and correspondence.

## Summary Rules

Write `FileSummary` as a concise 2- to 5-word description.

Prefer summaries that tell the user what the file is without reopening it:

1. Keep recognizable issuer or subject names when useful: `Capital One Savor Statement`, `Dental Arts Visit Letter`.
2. Remove filler like `statement dated`, `document`, `scan`, or random IDs unless they are the only distinguishing detail.
3. Preserve meaningful differentiators such as person names, account types, or duplicate numbers.
4. Replace forbidden path characters such as `/` or `:` with safe spaces.
5. Avoid adding commentary not supported by the file.

Use title-style capitalization when it improves readability. Preserve established acronyms like `IRS`, `PDF`, `UHC`, or `DICOM`.

## Extension Rules

Keep the existing file type and lowercase the extension:

1. `PDF` becomes `.pdf`
2. `HEIC` becomes `.heic`
3. `mov` stays `.mov`

Do not change the actual file format.

## Safety Rules

1. Never overwrite an existing file.
2. If the preferred filename collides, choose a clearer summary or add a minimal differentiator such as `2` only when necessary.
3. Rename files only. Do not modify contents, metadata, timestamps, or directory structure unless the user explicitly asks.
4. Prefer a dry listing first when many files are involved or when date inference is uncertain.
5. If the correct date cannot be determined confidently, surface the uncertainty instead of guessing silently.

## Execution Notes

Use fast shell discovery tools such as `rg --files` or `find` to identify files. Inspect filenames first, then read document text or metadata only for the files whose dates or summaries are unclear.

Use non-destructive rename commands:

```bash
mv -- "old name.ext" "YYYY-MM-DD - FileSummary.ext"
```

If working through a large folder, present the proposed rename map clearly before executing when that reduces risk.

## Example Triggers

1. Rename the PDFs in this folder that are still using random filenames.
2. Standardize these statements to `YYYY-MM-DD - Summary.ext` and leave the ones already renamed alone.
3. Clean up this downloads folder by renaming documents based on the most relevant date in each file.
4. Rename these scans only. Do not edit the files themselves.

## Dependencies and portability

All naming/date-selection rules are local; no other skill is required.
Renaming needs host filesystem operations or the OS `mv` command. Reading
document contents may need built-in document/vision support or an optional
format-specific extractor/OCR tool. With unreadable dates, report uncertainty.
A bundled Python standard-library rename/preflight helper could replace `mv`,
but Python alone does not parse every document format.
