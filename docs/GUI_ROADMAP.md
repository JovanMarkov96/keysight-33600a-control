# GUI Roadmap

This document defines the standalone GUI direction for interactive control and testing of Keysight 33600A instruments.

## Goals

- Connect/disconnect from VISA resources directly in the GUI
- Provide full channel control for CH1 and CH2
- Support command-level verification against live hardware
- Offer safe defaults for output state during connect and startup

## Phase 1 GUI Scope

- Resource selection and connection panel
- Identity/status panel (`*IDN?`, basic status indicators)
- Output enable/disable controls per channel
- Basic waveform controls:
  - function shape
  - frequency
  - amplitude and unit
  - DC offset
  - phase
- Error queue viewer (`SYST:ERR?` drain)

## Phase 2 GUI Scope

- Burst and trigger controls
- Frequency sweep configuration panel
- Arbitrary waveform manager:
  - import sample data
  - upload/select/delete waveforms
- Preset/state save and recall controls

## Phase 3 GUI Scope

- Advanced modulation tabs (AM/FM/PM/FSK/BPSK)
- Live plotting of configured waveform and modulation envelope
- Command history panel and replay
- Session profile save/load

## Suggested Technical Stack

- UI toolkit: PyQt5 or PySide6
- Device backend: `keysight_33600a.Keysight33600A`
- Non-blocking command execution using worker threads
- Structured logging for command-response traceability

## Safety Defaults

- Keep outputs OFF immediately after connection
- Confirm before enabling high amplitude outputs
- Validate channel and numeric input before command send
- Surface instrument errors prominently and block risky follow-up actions
