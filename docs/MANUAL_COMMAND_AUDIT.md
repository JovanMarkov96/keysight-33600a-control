# Manual Command Audit (33500/33600)

## Objective

Cross-check implemented API commands against the Keysight 33500/33600 manual and identify missing command families.

## Source Manual

- Local reference file: `docs/vendor_manuals/33500-33600-Manual.pdf`
- Local extracted text: `docs/vendor_manuals/33500-33600-Manual.txt`

## Extraction Approach (Low Token)

1. Convert PDF to text locally with `pdftotext -layout`.
2. Extract SCPI-like command tokens via regex.
3. Compare command families against `src/keysight_33600a/instrument.py` command usage.
4. Apply code updates for high-confidence command families.

## Manual-Verified Commands Used in This Update

- Trigger extensions
  - `TRIG:COUN` / `TRIG:COUN?`
  - `TRIG:DEL` / `TRIG:DEL?`
  - `TRIG:SLOP` / `TRIG:SLOP?`
  - `TRIG:TIM` / `TRIG:TIM?`
- Sweep extensions
  - `SWE:HTIM` / `SWE:HTIM?`
  - `SWE:RTIM` / `SWE:RTIM?`
  - `SWE:SPAC` / `SWE:SPAC?`
- Modulation families
  - `AM:STAT`, `AM:DEPT`, `AM:SOUR`
  - `FM:STAT`, `FM:DEV`, `FM:SOUR`
  - `PM:STAT`, `PM:DEV`, `PM:SOUR`
  - `FSK:STAT`, `FSK:FREQ`, `FSK:SOUR`
  - `BPSK:STAT`, `BPSK:PHAS`, `BPSK:SOUR`
- Volatile arbitrary memory
  - `DATA:VOL:CAT?`
  - `DATA:VOL:CLE`
  - `DATA:VOL:FREE?`
- IEEE/SCPI core status-state
  - `*STB?`, `*ESR?`, `*ESE`, `*ESE?`, `*SRE`, `*SRE?`, `*SAV`, `*RCL`

## Selected Manual Line Evidence (from extracted text)

- `AM:STATe` / `FM:STATe` entries around lines 3546 and 3548.
- `PM:STATe` and `PM:DEViation` around lines 3810 and 3939.
- `TRIG:COUN` examples around lines 6994 and 6998.
- `DATA:VOLatile:CATalog?`, `CLEar`, `FREE?` around lines 9097, 9114, 9126.
- `*ESR?`, `*RCL`, `*SAV`, `*STB?` around lines 11140, 11146, 11148, 11155.
- `SWE:HTIM`, `SWE:RTIM`, `SWE:SPAC` around lines 14565, 14578, 14592.

## Outcome

The API now includes high-confidence implementations for the command groups above.
Remaining command families are tracked in `docs/COMMAND_COVERAGE.md` with status tags for planned/manual-verification work.
