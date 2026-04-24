# Command Coverage Map

This table tracks implemented SCPI functionality in the first development iteration.

| Domain | SCPI examples | Status | API method(s) |
|---|---|---|---|
| Identity | `*IDN?` | Implemented | `identify` |
| Status clear/reset | `*CLS`, `*RST`, `*OPC?` | Implemented | `clear_status`, `reset`, `operation_complete` |
| Output enable | `OUTP{ch} ON/OFF`, `OUTP{ch}?` | Implemented | `set_output`, `get_output` |
| Output load | `OUTP{ch}:LOAD` | Implemented | `set_load`, `get_load` |
| Function/shape | `SOUR{ch}:FUNC` | Implemented | `set_function`, `get_function` |
| Frequency | `SOUR{ch}:FREQ` | Implemented | `set_frequency`, `get_frequency` |
| Amplitude | `SOUR{ch}:VOLT` | Implemented | `set_amplitude`, `get_amplitude` |
| Amplitude units | `SOUR{ch}:VOLT:UNIT` | Implemented | `set_amplitude_unit`, `get_amplitude_unit` |
| Offset | `SOUR{ch}:VOLT:OFFS` | Implemented | `set_offset`, `get_offset` |
| Phase | `SOUR{ch}:PHAS` | Implemented | `set_phase`, `get_phase` |
| Burst enable/mode | `SOUR{ch}:BURS:STAT`, `SOUR{ch}:BURS:MODE` | Implemented | `set_burst_enabled`, `set_burst_mode` |
| Burst cycles/period | `SOUR{ch}:BURS:NCYC`, `SOUR{ch}:BURS:INT:PER` | Implemented | `set_burst_ncycles`, `set_burst_period` |
| Trigger source | `TRIG{ch}:SOUR` | Implemented | `set_trigger_source`, `get_trigger_source` |
| Manual trigger | `*TRG` | Implemented | `trigger` |
| Sweep basics | `SOUR{ch}:SWE:STAT`, `FREQ:STAR`, `FREQ:STOP`, `SWE:TIME` | Implemented | `set_sweep_enabled`, `set_sweep_start`, `set_sweep_stop`, `set_sweep_time` |
| Arb upload/select | `SOUR{ch}:DATA:ARB`, `DATA:DAC`, `FUNC:ARB`, `FUNC ARB` | Implemented | `upload_arb_waveform_floats`, `upload_arb_waveform_dac`, `select_arb_waveform` |
| Arb sample rate | `SOUR{ch}:FUNC:ARB:SRAT` | Implemented | `set_arb_sample_rate` |
| Error queue | `SYST:ERR?` | Implemented | `get_system_errors`, `raise_for_instrument_errors`, `execute_checked` |

## Planned Next Coverage

- Trigger timer/delay/slope
- Sweep spacing/shape and marker controls
- Modulation families (AM/FM/PM/FSK/BPSK/SUM)
- Binary transfer mode for large arbitrary data blocks
- Sync/state-save/recall helpers
