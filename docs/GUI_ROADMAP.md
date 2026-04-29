# GUI Roadmap

This document defines the standalone public desktop GUI for the Keysight 33600A. It is intentionally free of private lab wiring, private GUI frameworks, or local connection assumptions.

## Scope

1. Build a self-contained GUI that any user can run against an attached instrument.
2. Keep the GUI independent from any parent application or lab-specific runtime.
3. Drive the UI from the device manual and SCPI readback, not from private workflow assumptions.
4. Treat this repository as the public implementation source for the instrument panel behavior.

## Non-Goals

1. No references to private control servers, local ports, or lab-only startup scripts.
2. No dependency on any parent application.
3. No hard-coded device identity, IP address, or site-specific connection data.
4. No hidden state files for local lab integration.

## Manual-Backed Interaction Rules

These rules are derived from the local manual extraction file `docs/vendor_manuals/33500-33600-Manual.txt`.

1. The front panel has fixed function keys, softkeys, numeric entry, and a manual trigger key.
2. The display separates channel information from sweep, modulation, burst, and trigger state.
3. Modulation flow uses `[Modulate]`, then type selection, then enable.
4. Sweep flow uses `[Sweep]` and shows status on the selected channel.
5. Burst flow uses `[Burst]` and shows status on the selected channel.
6. Trigger key semantics are stateful:
  - solid when the trigger menu is selected
  - blinking when the channel is armed but the menu is not selected
  - illuminated when one or both channels are waiting for a trigger
7. Channel output key illumination indicates output enabled.
8. Channel menu focus is explicit; menu actions must target the focused channel.

## Behavior Model

### Channel State

Each channel must track:

1. output enabled state
2. waveform family and core waveform parameters
3. amplitude unit and load
4. modulation family state and source
5. sweep enabled state and sweep parameters
6. burst enabled state and burst parameters
7. trigger source and trigger timing state

### Illumination Rules

For selected channel `CHx`:

1. `Modulate` is lit if any modulation family is enabled.
2. `Sweep` is lit if sweep is enabled.
3. `Burst` is lit if burst is enabled.
4. `Trigger` is lit or blinking if trigger is armed or waiting.
5. Channel output is lit if the output is on.

### Readback Rules

1. Every settable parameter should have a readback path where the device supports it.
2. The GUI should refresh from instrument state after each successful action.
3. The status banner should summarize the selected channel in a short manual-like string.
4. Failures should be surfaced immediately and not silently ignored.

## Panel Map

### Fixed Mode Buttons

1. `Waveforms`
  - waveform family, frequency, amplitude, offset, phase
2. `Parameters`
  - load and device-specific waveform limits
3. `Units`
  - amplitude unit and any unit selection workflow
4. `Modulate`
  - AM, FM, PM, FSK, BPSK
5. `Sweep`
  - sweep start, stop, spacing, hold, return, trigger source
6. `Burst`
  - burst mode, cycle count, burst period
7. `Trigger`
  - trigger source, count, delay, slope, timer, manual trigger action
8. `Channel Setup`
  - channel focus, output enable, and channel-local settings
9. `System`
  - IDN, status, error queue, reset, clear status, state recall/save

### Channel Keys

1. Channel keys switch the focused channel for all mode panels.
2. The focused channel controls both readback and command targets.
3. Output buttons are channel-local and should remain obvious at all times.

## Implementation Plan

### Phase 1: Stable Standalone Shell

1. Connection strip with resource selection, auto-detect, connect, disconnect, and IDN.
2. Channel focus controls for CH1 and CH2.
3. Mode button column.
4. Mode panels for waveform, units, channel setup, and system actions.
5. Readback-driven status banner.

#### Milestone 1 checklist

- [ ] Launch the GUI as a standalone app from `examples/launch_gui.py`.
- [ ] Connect to a real instrument by VISA resource string.
- [ ] Auto-detect a candidate VISA resource.
- [ ] Read and display `*IDN?` after connect.
- [ ] Force both channel outputs off immediately after connect.
- [ ] Switch focus between CH1 and CH2 without changing the other channel state.
- [ ] Show a visible connection state in the header and status banner.

#### Milestone 1 tests

- [ ] Unit test the resource discovery helper or provide a mockable wrapper.
- [ ] Unit test connect/disconnect lifecycle behavior with a fake instrument.
- [ ] Unit test that output is forced off after connect.
- [ ] Smoke test the launcher imports and creates the root window.
- [ ] Manual hardware check: connect, identify, disconnect, reconnect.

### Phase 2: Full Command Coverage

1. Complete waveform controls.
2. Complete modulation controls.
3. Complete sweep controls.
4. Complete burst controls.
5. Complete trigger controls.
6. Error queue browsing and state save/recall.

#### Milestone 2 checklist

- [ ] Apply waveform family, frequency, amplitude, offset, and phase per channel.
- [ ] Apply load and amplitude unit settings per channel.
- [ ] Read back waveform and parameter values after each apply.
- [ ] Apply AM, FM, PM, FSK, and BPSK settings.
- [ ] Apply sweep start, stop, time, spacing, hold, return, and trigger source.
- [ ] Apply burst mode, cycle count, and period.
- [ ] Apply trigger source, count, delay, slope, and timer.
- [ ] Read and display the error queue from the instrument.

#### Milestone 2 tests

- [ ] Unit test command formatting for each subsystem method.
- [ ] Unit test validation for invalid channels and out-of-range numeric inputs.
- [ ] Unit test readback parsing for each query path.
- [ ] Manual hardware check: each mode panel changes the expected instrument state.
- [ ] Manual hardware check: error queue is visible when a command is intentionally invalid.

### Phase 3: Polish and Safety

1. Non-blocking instrument operations.
2. Optional blinking trigger indication.
3. Command history with timestamps.
4. Better validation and inline feedback for numeric inputs.
5. Optional simulator backend for development and CI.

#### Milestone 3 checklist

- [ ] Move instrument operations off the UI thread.
- [ ] Add a visible busy state while commands are in flight.
- [ ] Add optional blinking behavior for trigger-armed state.
- [ ] Add timestamped command log entries.
- [ ] Validate numeric inputs before dispatching commands.
- [ ] Add a simulator or fake backend for development and CI.

#### Milestone 3 tests

- [ ] UI responsiveness smoke test during repeated connect/apply/refresh actions.
- [ ] Unit test the trigger illumination state logic.
- [ ] Unit test the numeric validation helper paths.
- [ ] Automated smoke test against the simulator backend.
- [ ] Manual hardware check: trigger armed state and status lighting match the manual.

## Release Checklist

- [ ] README documents installation, launch, and basic usage.
- [ ] `COMMAND_COVERAGE.md` matches implemented API surface.
- [ ] `MANUAL_COMMAND_AUDIT.md` records the manual evidence used for the GUI.
- [ ] `GUI_ROADMAP.md` is in sync with the actual implemented panels.
- [ ] Tests pass locally before any release tag or submodule pointer update.

## Recommended Execution Order

1. Complete Milestone 1 before adding more subsystem controls.
2. Complete Milestone 2 before polishing UI behavior.
3. Complete Milestone 3 before considering the GUI ready for stable public release.
4. Only update the parent repository submodule pointer after the release checklist is green.

## Validation Checklist

1. Connect and IDN succeed on a real device.
2. Channel focus changes every read/write target.
3. Mode lighting matches queried instrument state.
4. Manual trigger behavior matches armed state semantics.
5. Output defaults to off after connect.
6. Error queue can be viewed and cleared.
7. GUI remains usable without any parent application.

## Safety Rules

1. Force outputs off after a successful connect.
2. Validate numeric fields before sending commands.
3. Keep apply actions separate from trigger actions.
4. Show errors clearly and do not hide failed commands.
