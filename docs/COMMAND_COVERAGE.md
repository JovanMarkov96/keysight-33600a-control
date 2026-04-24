# Command Coverage Map

This document tracks SCPI subsystem coverage and implementation status.

Status values:
- Implemented: available in current high-level API
- Planned: defined for upcoming API iterations
- Needs-manual-verification: command family identified but exact model behavior must be confirmed on hardware/manual revision

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

## Trigger Subsystem Expansion

| Domain | SCPI examples | Status | Planned API method(s) |
|---|---|---|---|
| Trigger timer | `TRIG{ch}:TIM` | Planned | `set_trigger_timer`, `get_trigger_timer` |
| Trigger delay | `TRIG{ch}:DEL` | Planned | `set_trigger_delay`, `get_trigger_delay` |
| Trigger slope | `TRIG{ch}:SLOP` | Planned | `set_trigger_slope`, `get_trigger_slope` |
| Trigger count | `TRIG{ch}:COUN` | Planned | `set_trigger_count`, `get_trigger_count` |

## Sweep Subsystem Expansion

| Domain | SCPI examples | Status | Planned API method(s) |
|---|---|---|---|
| Sweep spacing | `SOUR{ch}:SWE:SPAC` | Planned | `set_sweep_spacing`, `get_sweep_spacing` |
| Sweep shape | `SOUR{ch}:SWE:SHAP` | Planned | `set_sweep_shape`, `get_sweep_shape` |
| Sweep trigger source | `SOUR{ch}:SWE:TRIG:SOUR` | Planned | `set_sweep_trigger_source` |
| Sweep hold/return time | `SOUR{ch}:SWE:HTIM`, `SOUR{ch}:SWE:RTIM` | Planned | `set_sweep_hold_time`, `set_sweep_return_time` |
| Sweep marker | `SOUR{ch}:MARK:POIN`, `SOUR{ch}:MARK:STAT` | Needs-manual-verification | `set_sweep_marker_point`, `set_sweep_marker_enabled` |

## Modulation Subsystems

| Domain | SCPI examples | Status | Planned API method(s) |
|---|---|---|---|
| AM | `SOUR{ch}:AM:STAT`, `SOUR{ch}:AM:DEPT`, `SOUR{ch}:AM:SOUR` | Planned | `set_am_enabled`, `set_am_depth`, `set_am_source` |
| FM | `SOUR{ch}:FM:STAT`, `SOUR{ch}:FM:DEV`, `SOUR{ch}:FM:SOUR` | Planned | `set_fm_enabled`, `set_fm_deviation`, `set_fm_source` |
| PM | `SOUR{ch}:PM:STAT`, `SOUR{ch}:PM:DEV`, `SOUR{ch}:PM:SOUR` | Planned | `set_pm_enabled`, `set_pm_deviation`, `set_pm_source` |
| FSK | `SOUR{ch}:FSK:STAT`, `SOUR{ch}:FSK:FREQ`, `SOUR{ch}:FSK:SOUR` | Planned | `set_fsk_enabled`, `set_fsk_frequency`, `set_fsk_source` |
| BPSK | `SOUR{ch}:BPSK:STAT`, `SOUR{ch}:BPSK:PHAS`, `SOUR{ch}:BPSK:SOUR` | Planned | `set_bpsk_enabled`, `set_bpsk_phase`, `set_bpsk_source` |
| SUM | `SOUR{ch}:SUM:STAT`, `SOUR{ch}:SUM:AMPL` | Needs-manual-verification | `set_sum_enabled`, `set_sum_amplitude` |

## Arbitrary Waveform Data Transfer

| Domain | SCPI examples | Status | Planned API method(s) |
|---|---|---|---|
| Binary arb upload | `SOUR{ch}:DATA:ARB:DAC <name>,#<n><len><data>` | Planned | `upload_arb_waveform_binary` |
| Volatile memory clear | `SOUR{ch}:DATA:VOL:CLE` | Planned | `clear_volatile_arb` |
| Arb catalog/list | `SOUR{ch}:DATA:CAT?` | Planned | `list_arb_waveforms` |

## Sync, State, and Recall

| Domain | SCPI examples | Status | Planned API method(s) |
|---|---|---|---|
| Channel sync phase | `SOUR:PHAS:SYNC` | Planned | `sync_phases` |
| Instrument state save | `*SAV <n>` | Planned | `save_state` |
| Instrument state recall | `*RCL <n>` | Planned | `recall_state` |
| User preset / memory slots | model-specific state commands | Needs-manual-verification | `save_profile`, `load_profile` |

## Status and Event Registers

| Domain | SCPI examples | Status | Planned API method(s) |
|---|---|---|---|
| Status byte | `*STB?` | Planned | `get_status_byte` |
| ESR query | `*ESR?`, `*ESE`, `*ESE?` | Planned | `get_event_status`, `set_event_enable` |
| Service request enable | `*SRE`, `*SRE?` | Planned | `set_service_request_enable` |

## Verification Notes

- Command names and hierarchy should be cross-checked against the exact 33600A programming guide revision in use.
- For all entries marked Needs-manual-verification, implementation should include explicit hardware validation scripts before release.
