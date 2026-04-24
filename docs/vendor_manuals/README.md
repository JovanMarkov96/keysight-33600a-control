# Vendor Manuals

This folder is for local vendor reference manuals used during development and validation.

## Current Manual

- Keysight Trueform Series Operating and Service Guide
- Expected local filename:
  - `33500-33600-Manual.pdf`

## Tracking Policy

Vendor manuals are typically copyrighted and should not be redistributed in this repository.

- Keep PDF/TXT manual artifacts local only.
- Use the command coverage and audit docs for shareable implementation details.

## Recommended Workflow

1. Place manual PDF in this folder locally.
2. Generate local text extraction only when needed.
3. Use `docs/MANUAL_COMMAND_AUDIT.md` and `docs/COMMAND_COVERAGE.md` as the tracked outputs.
