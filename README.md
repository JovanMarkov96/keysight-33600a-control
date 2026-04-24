# Keysight 33600A Control

Professional Python library for remote control of Keysight 33600A series waveform generators via SCPI/PyVISA.

This project is vendor-neutral and intended for anyone building measurement and automation software.

## Features (Phase 1)

- VISA connection management (USB/LAN/GPIB)
- Robust SCPI read/write/query wrapper
- IEEE status/event helpers (`*STB?`, `*ESR?`, `*ESE`, `*SRE`)
- State save/recall helpers (`*SAV`, `*RCL`)
- Channel-aware output and waveform control (CH1/CH2)
- Trigger controls (source/count/delay/slope/timer)
- Sweep controls (start/stop/time/spacing/hold/return)
- Modulation controls (AM/FM/PM/FSK/BPSK)
- Arbitrary waveform helpers (text float, DAC text, binary block)
- Volatile arbitrary memory controls (catalog/clear/free)
- Error queue handling (`SYST:ERR?`)

## Roadmap

- Complete advanced SCPI subsystem coverage
- Add hardware-in-the-loop validation scripts
- Build a standalone GUI application for interactive testing and configuration

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
- manual cross-check audit: `docs/MANUAL_COMMAND_AUDIT.md`
- GUI roadmap: `docs/GUI_ROADMAP.md`
- vendor manual handling policy: `docs/vendor_manuals/README.md`
- usage examples: `examples/`

## Legal and Trademark Notice

- This project is not affiliated with, endorsed by, or sponsored by Keysight Technologies.
- Keysight and 33600A are trademarks of their respective owners.
- This repository provides open-source integration tooling only and does not claim ownership of vendor protocols, manuals, or product IP.

## Notes

- Commands are implemented using documented SCPI conventions and verified command families.
- Always validate model-specific limits and behavior against your exact instrument firmware and documentation.
