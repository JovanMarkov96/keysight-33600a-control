# GUI Roadmap

This roadmap defines the standalone desktop GUI for Keysight 33600A with behavior aligned to front-panel flow and manual terminology.

## Design Targets

1. Standalone app that can connect and control the generator without private infrastructure.
2. Channel-aware UI where CH1 and CH2 are independent, with explicit channel focus.
3. Front-panel-inspired operation model:
  - fixed function mode buttons
  - context-sensitive parameter panel
  - manual-trigger behavior and mode status
4. Mode indicators that follow instrument state per selected channel.

## Manual-Backed Interaction Rules

The following rules are derived from the local manual extraction file `docs/vendor_manuals/33500-33600-Manual.txt`.

1. Front-panel structure includes fixed function buttons, softkeys, numeric keypad, knob/cursor model, and manual trigger key.
  - evidence: lines around 1236-1250, 1292-1300
2. Display separates channel information and sweep/modulation/burst parameter area.
  - evidence: lines around 1275-1281
3. Modulation enable path uses `[Modulate]`, then type selection, then enable softkey.
  - evidence: lines around 1888-1889
4. Sweep enable path uses `[Sweep]` and Sweep softkey; sweep status appears in selected channel tab and button illuminates.
  - evidence: lines around 2032-2034
5. Burst enable path uses `[Burst] > Burst Off/On` and reports status in selected channel tab.
  - evidence: lines around 2093-2094
6. Trigger key semantics:
  - illuminated Trigger means waiting for manual/bus trigger
  - solid when trigger menu selected, blinking when armed but menu not selected
  - press behavior depends on solid/blinking state
  - evidence: lines around 2136-2142 and 4967-5013
7. Channel output key illumination indicates channel output enabled.
  - evidence: lines around 12722
8. Channel menu focus is explicit (menus apply to focused channel).
  - evidence: lines around 2386

## Button Functionality Map

### Fixed Mode Buttons

1. `Waveforms`
  - selects waveform family and core values (freq/amplitude/offset/phase)
2. `Parameters`
  - waveform-specific parameters and output load/limits
3. `Units`
  - unit conversion preferences (voltage, frequency/period, etc.)
4. `Modulate`
  - modulation type/source/values and enable state
  - illuminated when modulation state is ON for selected channel
5. `Sweep`
  - sweep mode and timing boundaries
  - illuminated when sweep is ON for selected channel
6. `Burst`
  - burst mode/count/period
  - illuminated when burst is ON for selected channel
7. `Trigger`
  - trigger source/count/delay/slope/timer and manual trigger action
  - illuminated or blinking when trigger is armed/waiting
8. `Channel Setup`
  - channel focus and output behavior (termination/polarity/limits)
9. `System`
  - clear/reset/status/error queue, state save/recall

### Channel Keys

1. Channel keys set menu focus target.
2. Each channel keeps independent states for waveform/mode/output.
3. Output indicator is channel-specific and lights when that channel output is ON.

### Softkey-Inspired UX

1. Mode panel content changes by selected fixed button.
2. Parameter rows are context-sensitive (example: modulation value label depends on modulation type).
3. Number entry supports direct value entry and unit selection workflow.

## Illumination/Status Model (GUI)

For selected channel `CHx`, compute:

1. `Modulate` lit if any of `AM/FM/PM/FSK/BPSK` state is ON on `CHx`.
2. `Sweep` lit if `SOURx:SWE:STAT` is ON.
3. `Burst` lit if `SOURx:BURS:STAT` is ON.
4. `Trigger` lit if trigger source is armed (`BUS/EXT/TIM`) and sweep or burst is active.
5. Channel output key lit if `OUTPx` is ON.

Status banner for `CHx` should mirror manual style strings, for example:
- `AM Modulated`
- `Linear Sweep`
- `N Cycle Burst`
- `Trigger Armed (BUS)`

## Implementation Plan

### Phase 1: Core Standalone Panel

1. Connection strip (resource, auto-detect, connect/disconnect, IDN).
2. Channel focus/output area for CH1/CH2.
3. Mode button column.
4. Core mode panels:
  - Waveforms
  - Units
  - Channel Setup
  - System (status/errors/reset)

### Phase 2: Mode Completeness

1. Full Modulate panel:
  - AM, FM, PM, FSK, BPSK
2. Full Sweep panel:
  - start/stop/time/spacing/hold/return/trigger source
3. Full Burst panel:
  - mode/cycles/period
4. Trigger panel:
  - source/count/delay/slope/timer/manual trigger

### Phase 3: Advanced UX

1. Command history with timestamps and result states.
2. Optional blinking behavior for Trigger key when armed but trigger menu not selected.
3. Softkey bar visualization and per-mode quick actions.
4. Optional waveform preview plot.

## Validation Checklist

1. Connect and IDN succeed.
2. Channel focus changes all mode reads/writes target channel.
3. Mode lights match instrument query state per channel.
4. Manual trigger behavior matches source/mode logic.
5. GUI actions update the instrument and then refresh readback state.
6. Error queue is visible and actionable.

## Safety Rules

1. Force outputs OFF right after successful connect.
2. Validate numeric fields before command send.
3. Keep explicit separation between apply actions and trigger actions.
4. If command fails, show the error and do not silently continue.
