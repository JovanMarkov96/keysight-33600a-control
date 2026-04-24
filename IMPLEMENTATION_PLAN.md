# Keysight 33600A Control Repository - Detailed Implementation Plan

## 1. Objective

Build a standalone, production-quality Python repository for remote control of Keysight 33600A series waveform generators, with:
- connection management
- robust SCPI read/write/query
- safety/error handling
- high-level API for common operations
- command coverage map and examples
- test scaffolding for future hardware-in-the-loop validation

This repository is designed to be integrated later into the Lab185 `main_Qt.py` GUI.

## 2. Scope and Non-Goals

## 2.1 In scope (Phase 1)
- VISA connection (USB/LAN/GPIB resource strings)
- instrument identity and health checks (`*IDN?`, `*CLS`, `*RST`, `SYST:ERR?`)
- channel-aware output control for CH1/CH2
- waveform setup: function shape, frequency, amplitude, offset, phase, output load
- burst and trigger basics
- sweep basics
- arbitrary waveform upload helpers (float and DAC text mode)
- readback methods for key settings
- command log and error-queue draining

## 2.2 Out of scope (Phase 1)
- full GUI
- full binary waveform upload pipeline
- every advanced modulation mode implementation in first pass
- full hardware CI automation

## 3. Source Material and Reliability Strategy

## 3.1 Sources used
- Existing lab repository patterns from:
  - Newport 8742 project
  - Thorlabs MDT project
  - Thorlabs Motion Control project
- PyMeasure Agilent 33500 driver source:
  - command patterns and property-level SCPI strings
- PyVISA SCPI and Keysight control guidance:
  - transport patterns
  - synchronization and error handling practices

## 3.2 Reliability strategy
- Keep command implementations conservative and explicit
- Expose low-level `write/query` for rapid extension
- Provide command coverage doc with status tags:
  - Implemented
  - Planned
  - Needs-manual-verification
- Add clear warnings where manual-level confirmation is still required

## 4. Repository Architecture

```
Keysight_33600A_Control/
├── README.md
├── IMPLEMENTATION_PLAN.md
├── pyproject.toml
├── requirements.txt
├── docs/
│   └── COMMAND_COVERAGE.md
├── examples/
│   ├── basic_connection.py
│   ├── sine_output.py
│   └── burst_example.py
├── src/
│   └── keysight_33600a/
│       ├── __init__.py
│       ├── errors.py
│       ├── models.py
│       ├── discovery.py
│       └── instrument.py
└── tests/
    └── test_api_surface.py
```

## 5. API Design

## 5.1 Core class
- `Keysight33600A`
- context-manager support (`with` usage)
- lazy connection handling

## 5.2 Low-level methods
- `connect()`, `disconnect()`
- `write(cmd)`, `query(cmd)`, `query_float(cmd)`
- `clear_status()`, `reset()`, `identify()`
- `get_error()`, `drain_errors()`

## 5.3 High-level methods
- Output control:
  - `set_output(channel, state)`
  - `get_output(channel)`
- Basic waveform:
  - `set_function(channel, shape)`
  - `set_frequency(channel, hz)`
  - `set_amplitude(channel, volts)`
  - `set_amplitude_unit(channel, unit)`
  - `set_offset(channel, volts)`
  - `set_phase(channel, degrees)`
  - `set_output_load(channel, load)`
- Burst/trigger:
  - `set_burst_state(channel, state)`
  - `set_burst_mode(channel, mode)`
  - `set_burst_ncycles(channel, ncycles)`
  - `set_burst_period(channel, seconds)`
  - `set_trigger_source(channel, source)`
  - `trigger()`
- Sweep basics:
  - `configure_frequency_sweep(channel, start_hz, stop_hz, sweep_time_s, enable=True)`
- Arbitrary:
  - `clear_volatile_arb(channel)`
  - `upload_arb_float(channel, name, values)`
  - `upload_arb_dac(channel, name, values)`
  - `select_arb(channel, name)`
  - `set_arb_sample_rate(channel, sa_per_s)`

## 5.4 Validation
- channel must be 1 or 2
- shape/unit/source/mode validated against discrete sets
- optional numeric range checks where stable across models

## 6. Error Handling and Safety

- dedicated exceptions:
  - `Keysight33600AError`
  - `ConnectionError33600A`
  - `SCPICommandError`
  - `ValidationError33600A`
- optional strict mode:
  - after write, poll `SYST:ERR?` and raise if non-zero
- helper to drain queue and return list for logging

## 7. Testing Strategy

## 7.1 Phase 1 tests
- import and API-surface tests (no hardware)
- channel/enum validation tests
- command string formatting tests with mock adapter stubs

## 7.2 Phase 2 tests (future)
- hardware-in-loop smoke tests:
  - connect/idn
  - set sine + output on/off
  - burst roundtrip readback

## 8. Documentation Plan

## 8.1 README.md
- installation
- quick start
- safety and transport notes
- examples

## 8.2 COMMAND_COVERAGE.md
- SCPI command table grouped by subsystem
- implementation status per command
- notes where manual confirmation needed

## 8.3 Example scripts
- minimal connect/identify
- sine output setup
- burst setup

## 9. Integration Path to Main GUI

Future integration in `main_Qt.py` should be done via:
1. service wrapper around `Keysight33600A`
2. dedicated Qt widget/tab for waveform generator
3. non-blocking polling timer for readback fields
4. explicit connect/disconnect and output-safe defaults

## 10. Milestone Execution

1. Scaffold package, metadata, docs skeleton
2. Implement low-level VISA and SCPI core
3. Implement high-level output/waveform methods
4. Add examples
5. Add command coverage doc and test scaffold
6. Run local syntax and import checks
7. Prepare for extraction as standalone GitHub repo

## 11. Definition of Done (Phase 1)

- package imports successfully
- connect and identify flow implemented
- core waveform/burst/sweep operations available through high-level API
- docs and examples included
- command coverage matrix included
- clear list of phase-2 enhancements maintained
