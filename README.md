# Keysight 33600A Control

Professional Python library for remote control of Keysight 33600A series waveform generators via SCPI/PyVISA.

This package is designed for lab automation and future integration into Lab185 GUI tooling.

## Features (Phase 1)

- VISA connection management (USB/LAN/GPIB)
- Robust SCPI read/write/query wrapper
- Error queue handling (`SYST:ERR?`)
- Channel-aware output and waveform control (CH1/CH2)
- Burst and trigger basics
- Frequency sweep basics
- Arbitrary waveform upload helpers (text float/DAC)

## Install

```bash
pip install -e .
```

## Quick Start

```python
from keysight_33600a import Keysight33600A

resource = "USB0::0x2A8D::0x0001::MYXXXXXXXX::INSTR"

with Keysight33600A(resource) as gen:
    print(gen.identify())
    gen.clear_status()

    gen.set_function(1, "SIN")
    gen.set_frequency(1, 1_000.0)
    gen.set_amplitude(1, 2.0)
    gen.set_offset(1, 0.0)
    gen.set_output(1, True)
```

## Repository Layout

- API implementation: `src/keysight_33600a/`
- command coverage map: `docs/COMMAND_COVERAGE.md`
- usage examples: `examples/`
- implementation roadmap: `IMPLEMENTATION_PLAN.md`

## Notes

- Commands are based on SCPI practices and 33500-family command patterns.
- For model-specific limits and edge cases, validate against your exact 33600A firmware/manual revision.
