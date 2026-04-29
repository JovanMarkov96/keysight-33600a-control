from __future__ import annotations

import argparse
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox
from typing import Dict, Optional

from .discovery import list_keysight_resources
from .errors import Keysight33600AError
from .instrument import Keysight33600A
from .models import (
    AmplitudeUnit,
    BurstMode,
    ModulationSource,
    SweepSpacing,
    TriggerSlope,
    TriggerSource,
    WaveformShape,
)
from .simulator import SimulatedKeysight33600A
from .validation import (
    normalize_load,
    validate_count,
    validate_frequency,
    validate_non_negative_value,
    validate_positive_value,
    validate_sweep_shape,
    validate_voltage_settings,
)


@dataclass
class ChannelVisualState:
    output_on: bool = False
    modulation_on: bool = False
    modulation_label: str = "None"
    sweep_on: bool = False
    burst_on: bool = False
    trigger_source: str = "IMM"
    trigger_waiting: bool = False


class Keysight33600AFrontPanel(tk.Tk):
    """Standalone front-panel-inspired GUI for Keysight 33600A control."""

    def __init__(self, simulate: bool = False) -> None:
        super().__init__()
        self.title("Keysight 33600A Control Panel")
        self.geometry("1420x860")
        self.minsize(1200, 760)
        self.configure(bg="#202327")

        self.simulate = simulate
        self.instrument: Optional[Keysight33600A] = None
        self.selected_channel = 1
        self.current_mode = "Waveforms"
        self.states: Dict[int, ChannelVisualState] = {
            1: ChannelVisualState(),
            2: ChannelVisualState(),
        }

        self.resource_var = tk.StringVar(value="")
        self.idn_var = tk.StringVar(value="Disconnected")
        self.status_var = tk.StringVar(value="Idle")

        self.waveform_var = tk.StringVar(value=WaveformShape.SIN.value)
        self.freq_var = tk.StringVar(value="1000")
        self.amp_var = tk.StringVar(value="1.0")
        self.offset_var = tk.StringVar(value="0.0")
        self.phase_var = tk.StringVar(value="0.0")
        self.load_var = tk.StringVar(value="50")
        self.unit_var = tk.StringVar(value=AmplitudeUnit.VPP.value)

        self.mod_enable_var = tk.BooleanVar(value=False)
        self.mod_type_var = tk.StringVar(value="AM")
        self.mod_source_var = tk.StringVar(value=ModulationSource.INT.value)
        self.mod_value_var = tk.StringVar(value="50")

        self.sweep_enable_var = tk.BooleanVar(value=False)
        self.sweep_spacing_var = tk.StringVar(value=SweepSpacing.LIN.value)
        self.sweep_start_var = tk.StringVar(value="50")
        self.sweep_stop_var = tk.StringVar(value="5000")
        self.sweep_time_var = tk.StringVar(value="1.0")
        self.sweep_hold_var = tk.StringVar(value="0")
        self.sweep_return_var = tk.StringVar(value="0")
        self.sweep_trigger_source_var = tk.StringVar(value=TriggerSource.IMM.value)

        self.burst_enable_var = tk.BooleanVar(value=False)
        self.burst_mode_var = tk.StringVar(value=BurstMode.TRIG.value)
        self.burst_cycles_var = tk.StringVar(value="3")
        self.burst_period_var = tk.StringVar(value="0.02")

        self.trigger_source_var = tk.StringVar(value=TriggerSource.IMM.value)
        self.trigger_count_var = tk.StringVar(value="1")
        self.trigger_delay_var = tk.StringVar(value="0")
        self.trigger_timer_var = tk.StringVar(value="0.5")
        self.trigger_slope_var = tk.StringVar(value=TriggerSlope.POS.value)

        self.state_slot_var = tk.StringVar(value="1")

        self.mode_buttons: Dict[str, tk.Button] = {}
        self.channel_focus_buttons: Dict[int, tk.Button] = {}
        self.channel_output_buttons: Dict[int, tk.Button] = {}

        self._build_layout()
        self._rebuild_mode_panel()
        self._refresh_all_indicators()

    def _build_layout(self) -> None:
        self._build_header()

        body = tk.Frame(self, bg="#202327")
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        self.display_frame = tk.Frame(body, bg="#101317", bd=2, relief=tk.GROOVE)
        self.display_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right = tk.Frame(body, bg="#202327")
        right.pack(side=tk.RIGHT, fill=tk.Y)

        self._build_display_panel()
        self._build_mode_column(right)

    def _build_header(self) -> None:
        header = tk.Frame(self, bg="#2a2f36", bd=0)
        header.pack(fill=tk.X, padx=12, pady=12)

        tk.Label(
            header,
            text="Keysight 33600A",
            fg="#f4f4f4",
            bg="#2a2f36",
            font=("Segoe UI", 16, "bold"),
        ).pack(side=tk.LEFT, padx=(8, 18))

        tk.Label(header, text="VISA Resource", fg="#d2d2d2", bg="#2a2f36").pack(
            side=tk.LEFT
        )
        tk.Entry(
            header,
            textvariable=self.resource_var,
            width=44,
            bg="#171a1f",
            fg="#f3f3f3",
            insertbackground="#f3f3f3",
            relief=tk.FLAT,
        ).pack(side=tk.LEFT, padx=6)

        tk.Button(
            header,
            text="Auto",
            command=self._auto_fill_resource,
            bg="#445062",
            fg="#ffffff",
            relief=tk.FLAT,
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            header,
            text="Connect",
            command=self._connect,
            bg="#3d7a45",
            fg="#ffffff",
            relief=tk.FLAT,
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            header,
            text="Disconnect",
            command=self._disconnect,
            bg="#9c3b3b",
            fg="#ffffff",
            relief=tk.FLAT,
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            header,
            text="Refresh",
            command=self._refresh_all_indicators,
            bg="#466a86",
            fg="#ffffff",
            relief=tk.FLAT,
        ).pack(side=tk.LEFT, padx=4)

        tk.Label(
            header,
            textvariable=self.idn_var,
            fg="#e9d872",
            bg="#2a2f36",
            anchor="e",
            font=("Consolas", 10),
        ).pack(side=tk.RIGHT, padx=(8, 10))

    def _build_display_panel(self) -> None:
        top = tk.Frame(self.display_frame, bg="#151a20")
        top.pack(fill=tk.X, padx=10, pady=10)

        for ch in (1, 2):
            row = tk.Frame(top, bg="#151a20")
            row.pack(side=tk.LEFT, padx=6)

            focus = tk.Button(
                row,
                text=f"CH{ch}",
                width=6,
                command=lambda c=ch: self._set_channel_focus(c),
                bg="#2d333b",
                fg="#f0f0f0",
                relief=tk.FLAT,
            )
            focus.pack(side=tk.TOP, pady=(0, 4))
            self.channel_focus_buttons[ch] = focus

            out_btn = tk.Button(
                row,
                text="OUT OFF",
                width=8,
                command=lambda c=ch: self._toggle_output(c),
                bg="#503434",
                fg="#f0f0f0",
                relief=tk.FLAT,
            )
            out_btn.pack(side=tk.TOP)
            self.channel_output_buttons[ch] = out_btn

        status_box = tk.Frame(top, bg="#151a20")
        status_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(14, 0))

        tk.Label(
            status_box,
            text="Channel Status",
            bg="#151a20",
            fg="#d8d8d8",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(fill=tk.X)

        self.status_message = tk.Label(
            status_box,
            textvariable=self.status_var,
            bg="#151a20",
            fg="#f2cd6b",
            font=("Consolas", 11),
            anchor="w",
            justify=tk.LEFT,
        )
        self.status_message.pack(fill=tk.X)

        self.mode_panel = tk.Frame(self.display_frame, bg="#101317")
        self.mode_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        log_frame = tk.Frame(self.display_frame, bg="#151a20")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        tk.Label(
            log_frame,
            text="Command Log",
            bg="#151a20",
            fg="#d8d8d8",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(fill=tk.X)

        self.log_text = tk.Text(
            log_frame,
            height=12,
            bg="#0d1014",
            fg="#dbe8ff",
            relief=tk.FLAT,
            wrap=tk.WORD,
            font=("Consolas", 10),
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.configure(state=tk.DISABLED)

    def _build_mode_column(self, parent: tk.Frame) -> None:
        mode_frame = tk.Frame(parent, bg="#1e2228", bd=2, relief=tk.GROOVE)
        mode_frame.pack(fill=tk.Y)

        for mode in [
            "Waveforms",
            "Parameters",
            "Units",
            "Modulate",
            "Sweep",
            "Burst",
            "Trigger",
            "Channel Setup",
            "System",
        ]:
            btn = tk.Button(
                mode_frame,
                text=mode,
                width=14,
                pady=8,
                command=lambda m=mode: self._select_mode(m),
                bg="#313740",
                fg="#f5f5f5",
                relief=tk.FLAT,
            )
            btn.pack(fill=tk.X, padx=8, pady=4)
            self.mode_buttons[mode] = btn

    def _log(self, text: str) -> None:
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _auto_fill_resource(self) -> None:
        if self.simulate:
            self.resource_var.set("SIM::KEYSIGHT33600A")
            self._log("Simulation mode selected")
            return

        try:
            resources = list_keysight_resources()
            if not resources:
                messagebox.showinfo("No resources", "No Keysight-like VISA resources found.")
                return
            self.resource_var.set(resources[0])
            self._log(f"Auto selected resource: {resources[0]}")
        except Exception as exc:
            messagebox.showerror("Auto detect failed", str(exc))

    def _connect(self) -> None:
        resource = self.resource_var.get().strip()
        if not resource:
            messagebox.showwarning("Missing resource", "Enter a VISA resource string first.")
            return

        try:
            if self.simulate or resource.upper().startswith("SIM::"):
                self.instrument = SimulatedKeysight33600A(resource)
            else:
                self.instrument = Keysight33600A(resource)
            self.instrument.connect()
            self.idn_var.set(self.instrument.identify())
            self.instrument.set_output(1, False)
            self.instrument.set_output(2, False)
            self._log(f"Connected: {self.idn_var.get()}")
            self._refresh_all_indicators()
        except Exception as exc:
            self.instrument = None
            messagebox.showerror("Connection failed", str(exc))

    def _disconnect(self) -> None:
        try:
            if self.instrument is not None:
                self.instrument.disconnect()
                self._log("Disconnected")
        except Exception as exc:
            messagebox.showwarning("Disconnect warning", str(exc))
        finally:
            self.instrument = None
            self.idn_var.set("Disconnected")
            self._refresh_all_indicators(clear_only=True)

    def _require_instrument(self) -> Keysight33600A:
        if self.instrument is None:
            raise RuntimeError("Connect to the instrument first.")
        return self.instrument

    def _execute(self, label: str, fn) -> None:
        try:
            fn()
            self._log(f"OK: {label}")
            self._refresh_all_indicators()
        except (RuntimeError, Keysight33600AError, ValueError) as exc:
            self._log(f"ERR: {label} -> {exc}")
            messagebox.showerror("Command failed", str(exc))

    def _set_channel_focus(self, channel: int) -> None:
        self.selected_channel = channel
        self._refresh_all_indicators()
        self._rebuild_mode_panel()

    def _toggle_output(self, channel: int) -> None:
        def action() -> None:
            inst = self._require_instrument()
            current = inst.get_output(channel)
            inst.set_output(channel, not current)

        self._execute(f"Toggle CH{channel} output", action)

    def _select_mode(self, mode: str) -> None:
        self.current_mode = mode
        self._rebuild_mode_panel()
        self._refresh_mode_buttons()

    def _rebuild_mode_panel(self) -> None:
        for child in self.mode_panel.winfo_children():
            child.destroy()

        builders = {
            "Waveforms": self._build_waveforms_panel,
            "Parameters": self._build_parameters_panel,
            "Units": self._build_units_panel,
            "Modulate": self._build_modulate_panel,
            "Sweep": self._build_sweep_panel,
            "Burst": self._build_burst_panel,
            "Trigger": self._build_trigger_panel,
            "Channel Setup": self._build_channel_setup_panel,
            "System": self._build_system_panel,
        }
        builders[self.current_mode]()

    def _row(self, label: str, var: tk.StringVar, width: int = 12) -> tk.Entry:
        row = tk.Frame(self.mode_panel, bg="#101317")
        row.pack(fill=tk.X, pady=4)
        tk.Label(row, text=label, bg="#101317", fg="#dcdcdc", width=20, anchor="w").pack(
            side=tk.LEFT
        )
        entry = tk.Entry(
            row,
            textvariable=var,
            width=width,
            bg="#171b21",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief=tk.FLAT,
        )
        entry.pack(side=tk.LEFT)
        return entry

    def _option_row(self, label: str, var: tk.StringVar, options: list[str]) -> None:
        row = tk.Frame(self.mode_panel, bg="#101317")
        row.pack(fill=tk.X, pady=4)
        tk.Label(row, text=label, bg="#101317", fg="#dcdcdc", width=20, anchor="w").pack(
            side=tk.LEFT
        )
        tk.OptionMenu(row, var, *options).pack(side=tk.LEFT)

    def _build_waveforms_panel(self) -> None:
        tk.Label(
            self.mode_panel,
            text=f"Waveforms (Channel {self.selected_channel})",
            bg="#101317",
            fg="#f0d16d",
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 8))

        self._option_row("Shape", self.waveform_var, [x.value for x in WaveformShape])
        self._row("Frequency (Hz)", self.freq_var)
        self._row("Amplitude", self.amp_var)
        self._row("Offset (V)", self.offset_var)
        self._row("Phase (deg)", self.phase_var)

        tk.Button(
            self.mode_panel,
            text="Apply Waveform",
            bg="#7a6a2d",
            fg="#ffffff",
            relief=tk.FLAT,
            command=self._apply_waveform,
        ).pack(anchor="w", pady=8)

    def _build_parameters_panel(self) -> None:
        tk.Label(
            self.mode_panel,
            text=f"Parameters (Channel {self.selected_channel})",
            bg="#101317",
            fg="#f0d16d",
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 8))

        self._row("Load (ohms or INF)", self.load_var)

        tk.Button(
            self.mode_panel,
            text="Apply Parameters",
            bg="#6c4f3a",
            fg="#ffffff",
            relief=tk.FLAT,
            command=self._apply_parameters,
        ).pack(anchor="w", pady=8)

    def _build_units_panel(self) -> None:
        tk.Label(
            self.mode_panel,
            text=f"Units (Channel {self.selected_channel})",
            bg="#101317",
            fg="#f0d16d",
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 8))

        self._option_row("Amplitude Unit", self.unit_var, [x.value for x in AmplitudeUnit])
        tk.Button(
            self.mode_panel,
            text="Apply Units",
            bg="#5d4a78",
            fg="#ffffff",
            relief=tk.FLAT,
            command=self._apply_units,
        ).pack(anchor="w", pady=8)

    def _build_modulate_panel(self) -> None:
        tk.Label(
            self.mode_panel,
            text=f"Modulate (Channel {self.selected_channel})",
            bg="#101317",
            fg="#f0d16d",
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 8))

        tk.Checkbutton(
            self.mode_panel,
            text="Modulation On",
            variable=self.mod_enable_var,
            bg="#101317",
            fg="#dcdcdc",
            selectcolor="#101317",
            activebackground="#101317",
            activeforeground="#dcdcdc",
        ).pack(anchor="w")

        self._option_row("Type", self.mod_type_var, ["AM", "FM", "PM", "FSK", "BPSK"])
        self._option_row("Source", self.mod_source_var, [x.value for x in ModulationSource])
        self._row("Value", self.mod_value_var)

        tk.Label(
            self.mode_panel,
            text="Value means: AM depth (%), FM dev (Hz), PM dev (deg), FSK hop freq (Hz), BPSK phase (deg)",
            bg="#101317",
            fg="#aab4c2",
            wraplength=720,
            justify=tk.LEFT,
        ).pack(fill=tk.X, pady=(4, 0))

        tk.Button(
            self.mode_panel,
            text="Apply Modulation",
            bg="#8a5a27",
            fg="#ffffff",
            relief=tk.FLAT,
            command=self._apply_modulation,
        ).pack(anchor="w", pady=8)

    def _build_sweep_panel(self) -> None:
        tk.Label(
            self.mode_panel,
            text=f"Sweep (Channel {self.selected_channel})",
            bg="#101317",
            fg="#f0d16d",
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 8))

        tk.Checkbutton(
            self.mode_panel,
            text="Sweep On",
            variable=self.sweep_enable_var,
            bg="#101317",
            fg="#dcdcdc",
            selectcolor="#101317",
            activebackground="#101317",
            activeforeground="#dcdcdc",
        ).pack(anchor="w")

        self._option_row("Spacing", self.sweep_spacing_var, [x.value for x in SweepSpacing])
        self._option_row(
            "Trigger Source",
            self.sweep_trigger_source_var,
            [x.value for x in TriggerSource],
        )
        self._row("Start Freq (Hz)", self.sweep_start_var)
        self._row("Stop Freq (Hz)", self.sweep_stop_var)
        self._row("Sweep Time (s)", self.sweep_time_var)
        self._row("Hold Time (s)", self.sweep_hold_var)
        self._row("Return Time (s)", self.sweep_return_var)

        tk.Button(
            self.mode_panel,
            text="Apply Sweep",
            bg="#6a7c31",
            fg="#ffffff",
            relief=tk.FLAT,
            command=self._apply_sweep,
        ).pack(anchor="w", pady=8)

    def _build_burst_panel(self) -> None:
        tk.Label(
            self.mode_panel,
            text=f"Burst (Channel {self.selected_channel})",
            bg="#101317",
            fg="#f0d16d",
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 8))

        tk.Checkbutton(
            self.mode_panel,
            text="Burst On",
            variable=self.burst_enable_var,
            bg="#101317",
            fg="#dcdcdc",
            selectcolor="#101317",
            activebackground="#101317",
            activeforeground="#dcdcdc",
        ).pack(anchor="w")

        self._option_row("Mode", self.burst_mode_var, [x.value for x in BurstMode])
        self._row("# Cycles", self.burst_cycles_var)
        self._row("Burst Period (s)", self.burst_period_var)

        tk.Button(
            self.mode_panel,
            text="Apply Burst",
            bg="#4d7a7a",
            fg="#ffffff",
            relief=tk.FLAT,
            command=self._apply_burst,
        ).pack(anchor="w", pady=8)

    def _build_trigger_panel(self) -> None:
        tk.Label(
            self.mode_panel,
            text=f"Trigger (Channel {self.selected_channel})",
            bg="#101317",
            fg="#f0d16d",
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 8))

        self._option_row("Trigger Source", self.trigger_source_var, [x.value for x in TriggerSource])
        self._row("Trigger Count", self.trigger_count_var)
        self._row("Trigger Delay (s)", self.trigger_delay_var)
        self._row("Trigger Timer (s)", self.trigger_timer_var)
        self._option_row("Trigger Slope", self.trigger_slope_var, [x.value for x in TriggerSlope])

        row = tk.Frame(self.mode_panel, bg="#101317")
        row.pack(fill=tk.X, pady=8)

        tk.Button(
            row,
            text="Apply Trigger Setup",
            bg="#7c5631",
            fg="#ffffff",
            relief=tk.FLAT,
            command=self._apply_trigger,
        ).pack(side=tk.LEFT)

        tk.Button(
            row,
            text="Manual Trigger",
            bg="#9a3d3d",
            fg="#ffffff",
            relief=tk.FLAT,
            command=self._send_manual_trigger,
        ).pack(side=tk.LEFT, padx=8)

    def _build_channel_setup_panel(self) -> None:
        tk.Label(
            self.mode_panel,
            text=f"Channel Setup (Channel {self.selected_channel})",
            bg="#101317",
            fg="#f0d16d",
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 8))

        tk.Label(
            self.mode_panel,
            text="Channel focus defines which channel menu actions target.",
            bg="#101317",
            fg="#aab4c2",
            anchor="w",
        ).pack(fill=tk.X)

        self._row("Load (ohms or INF)", self.load_var)

        tk.Button(
            self.mode_panel,
            text=f"Toggle CH{self.selected_channel} Output",
            bg="#61496f",
            fg="#ffffff",
            relief=tk.FLAT,
            command=lambda: self._toggle_output(self.selected_channel),
        ).pack(anchor="w", pady=(8, 2))

        tk.Button(
            self.mode_panel,
            text="Apply Channel Load",
            bg="#5f5a3a",
            fg="#ffffff",
            relief=tk.FLAT,
            command=self._apply_parameters,
        ).pack(anchor="w", pady=2)

    def _build_system_panel(self) -> None:
        tk.Label(
            self.mode_panel,
            text="System",
            bg="#101317",
            fg="#f0d16d",
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 8))

        row = tk.Frame(self.mode_panel, bg="#101317")
        row.pack(fill=tk.X, pady=4)

        tk.Button(row, text="*CLS", command=self._clear_status, bg="#49545f", fg="#fff", relief=tk.FLAT).pack(side=tk.LEFT)
        tk.Button(row, text="*RST", command=self._reset, bg="#5f4d49", fg="#fff", relief=tk.FLAT).pack(side=tk.LEFT, padx=6)
        tk.Button(row, text="Read Errors", command=self._read_errors, bg="#3c6360", fg="#fff", relief=tk.FLAT).pack(side=tk.LEFT)

        self._row("State Slot (0-4)", self.state_slot_var)

        row2 = tk.Frame(self.mode_panel, bg="#101317")
        row2.pack(fill=tk.X, pady=4)
        tk.Button(row2, text="Save State", command=self._save_state, bg="#6d5c2f", fg="#fff", relief=tk.FLAT).pack(side=tk.LEFT)
        tk.Button(row2, text="Recall State", command=self._recall_state, bg="#2f6d5d", fg="#fff", relief=tk.FLAT).pack(side=tk.LEFT, padx=6)

    def _apply_waveform(self) -> None:
        def action() -> None:
            inst = self._require_instrument()
            ch = self.selected_channel
            shape = WaveformShape(self.waveform_var.get())
            frequency = float(self.freq_var.get())
            amplitude = float(self.amp_var.get())
            offset = float(self.offset_var.get())
            load_value = normalize_load(self.load_var.get())

            validate_frequency(shape, frequency)
            validate_voltage_settings(amplitude, offset, load_value)

            inst.set_function(ch, shape)
            inst.set_frequency(ch, frequency)
            inst.set_amplitude(ch, amplitude)
            inst.set_offset(ch, offset)
            inst.set_phase(ch, float(self.phase_var.get()))

        self._execute(f"Apply waveform CH{self.selected_channel}", action)

    def _apply_parameters(self) -> None:
        def action() -> None:
            inst = self._require_instrument()
            raw = self.load_var.get().strip()
            ch = self.selected_channel
            normalized = normalize_load(raw)
            if self.unit_var.get().upper() == AmplitudeUnit.DBM.value and normalized == "INF":
                raise ValueError("dBm units require a finite output termination")
            try:
                inst.set_load(ch, normalized)
            except ValueError:
                inst.set_load(ch, normalized)

        self._execute(f"Apply parameters CH{self.selected_channel}", action)

    def _apply_units(self) -> None:
        def action() -> None:
            inst = self._require_instrument()
            inst.set_amplitude_unit(self.selected_channel, self.unit_var.get())

        self._execute(f"Apply units CH{self.selected_channel}", action)

    def _apply_modulation(self) -> None:
        def action() -> None:
            inst = self._require_instrument()
            ch = self.selected_channel
            typ = self.mod_type_var.get().upper()
            enabled = bool(self.mod_enable_var.get())
            source = self.mod_source_var.get().upper()
            value = float(self.mod_value_var.get())

            if typ == "AM":
                inst.set_am_source(ch, source)
                inst.set_am_depth(ch, value)
                inst.set_am_enabled(ch, enabled)
            elif typ == "FM":
                inst.set_fm_source(ch, source)
                inst.set_fm_deviation(ch, value)
                inst.set_fm_enabled(ch, enabled)
            elif typ == "PM":
                inst.set_pm_source(ch, source)
                inst.set_pm_deviation(ch, value)
                inst.set_pm_enabled(ch, enabled)
            elif typ == "FSK":
                inst.set_fsk_source(ch, source)
                inst.set_fsk_frequency(ch, value)
                inst.set_fsk_enabled(ch, enabled)
            elif typ == "BPSK":
                inst.set_bpsk_source(ch, source)
                inst.set_bpsk_phase(ch, value)
                inst.set_bpsk_enabled(ch, enabled)
            else:
                raise RuntimeError(f"Unsupported modulation type: {typ}")

        self._execute(f"Apply modulation CH{self.selected_channel}", action)

    def _apply_sweep(self) -> None:
        def action() -> None:
            inst = self._require_instrument()
            ch = self.selected_channel
            shape = WaveformShape(self.waveform_var.get())
            validate_sweep_shape(shape)
            start = float(self.sweep_start_var.get())
            stop = float(self.sweep_stop_var.get())
            validate_positive_value("Sweep start frequency", start)
            validate_positive_value("Sweep stop frequency", stop)
            if start >= stop:
                raise ValueError("Sweep start frequency must be lower than stop frequency")
            validate_positive_value("Sweep time", float(self.sweep_time_var.get()))
            validate_non_negative_value("Sweep hold time", float(self.sweep_hold_var.get()))
            validate_non_negative_value("Sweep return time", float(self.sweep_return_var.get()))
            inst.set_sweep_spacing(ch, self.sweep_spacing_var.get())
            inst.set_sweep_start(ch, start)
            inst.set_sweep_stop(ch, stop)
            inst.set_sweep_time(ch, float(self.sweep_time_var.get()))
            inst.set_sweep_hold_time(ch, float(self.sweep_hold_var.get()))
            inst.set_sweep_return_time(ch, float(self.sweep_return_var.get()))
            inst.set_sweep_trigger_source(ch, self.sweep_trigger_source_var.get())
            inst.set_sweep_enabled(ch, bool(self.sweep_enable_var.get()))

        self._execute(f"Apply sweep CH{self.selected_channel}", action)

    def _apply_burst(self) -> None:
        def action() -> None:
            inst = self._require_instrument()
            ch = self.selected_channel
            validate_count("Burst cycles", int(self.burst_cycles_var.get()))
            validate_positive_value("Burst period", float(self.burst_period_var.get()))
            inst.set_burst_mode(ch, self.burst_mode_var.get())
            inst.set_burst_ncycles(ch, int(self.burst_cycles_var.get()))
            inst.set_burst_period(ch, float(self.burst_period_var.get()))
            inst.set_burst_enabled(ch, bool(self.burst_enable_var.get()))

        self._execute(f"Apply burst CH{self.selected_channel}", action)

    def _apply_trigger(self) -> None:
        def action() -> None:
            inst = self._require_instrument()
            ch = self.selected_channel
            validate_count("Trigger count", int(self.trigger_count_var.get()))
            validate_non_negative_value("Trigger delay", float(self.trigger_delay_var.get()))
            validate_positive_value("Trigger timer", float(self.trigger_timer_var.get()))
            inst.set_trigger_source(ch, self.trigger_source_var.get())
            inst.set_trigger_count(ch, int(self.trigger_count_var.get()))
            inst.set_trigger_delay(ch, float(self.trigger_delay_var.get()))
            inst.set_trigger_timer(ch, float(self.trigger_timer_var.get()))
            inst.set_trigger_slope(ch, self.trigger_slope_var.get())

        self._execute(f"Apply trigger setup CH{self.selected_channel}", action)

    def _send_manual_trigger(self) -> None:
        self._execute("Manual trigger", lambda: self._require_instrument().trigger())

    def _clear_status(self) -> None:
        self._execute("*CLS", lambda: self._require_instrument().clear_status())

    def _reset(self) -> None:
        self._execute("*RST", lambda: self._require_instrument().reset())

    def _read_errors(self) -> None:
        def action() -> None:
            inst = self._require_instrument()
            errors = inst.get_system_errors(max_reads=30)
            if not errors:
                self._log("No instrument errors")
                return
            for entry in errors:
                self._log(f"SYST:ERR -> {entry.code}, {entry.message}")

        self._execute("Read errors", action)

    def _save_state(self) -> None:
        self._execute(
            f"Save state slot {self.state_slot_var.get()}",
            lambda: self._require_instrument().save_state(int(self.state_slot_var.get())),
        )

    def _recall_state(self) -> None:
        self._execute(
            f"Recall state slot {self.state_slot_var.get()}",
            lambda: self._require_instrument().recall_state(int(self.state_slot_var.get())),
        )

    def _refresh_all_indicators(self, clear_only: bool = False) -> None:
        if clear_only:
            self.states = {1: ChannelVisualState(), 2: ChannelVisualState()}
            self.status_var.set("Disconnected")
            self._refresh_channel_buttons()
            self._refresh_mode_buttons()
            return

        if self.instrument is not None:
            for ch in (1, 2):
                self.states[ch] = self._read_channel_state(ch)

            self._load_selected_channel_into_controls()
            self.status_var.set(self._compose_status_message(self.selected_channel))
        else:
            self.status_var.set("Idle")

        self._refresh_channel_buttons()
        self._refresh_mode_buttons()

    def _read_channel_state(self, channel: int) -> ChannelVisualState:
        inst = self._require_instrument()

        out = self._safe_bool(lambda: inst.get_output(channel), default=False)
        sweep = self._safe_bool(lambda: inst.get_sweep_enabled(channel), default=False)
        burst = self._safe_bool(lambda: inst.get_burst_enabled(channel), default=False)
        trig_source = self._safe_str(lambda: inst.get_trigger_source(channel), default="IMM")

        mod_checks = [
            ("AM", lambda: inst.get_am_enabled(channel)),
            ("FM", lambda: inst.get_fm_enabled(channel)),
            ("PM", lambda: inst.get_pm_enabled(channel)),
            ("FSK", lambda: inst.get_fsk_enabled(channel)),
            ("BPSK", lambda: inst.get_bpsk_enabled(channel)),
        ]
        mod_on = False
        mod_label = "None"
        for label, check in mod_checks:
            if self._safe_bool(check, default=False):
                mod_on = True
                mod_label = label
                break

        trigger_waiting = trig_source in {"EXT", "BUS", "TIM"} and (sweep or burst)

        return ChannelVisualState(
            output_on=out,
            modulation_on=mod_on,
            modulation_label=mod_label,
            sweep_on=sweep,
            burst_on=burst,
            trigger_source=trig_source,
            trigger_waiting=trigger_waiting,
        )

    @staticmethod
    def _safe_bool(fn, default: bool = False) -> bool:
        try:
            return bool(fn())
        except Exception:
            return default

    @staticmethod
    def _safe_str(fn, default: str = "") -> str:
        try:
            return str(fn()).strip().upper()
        except Exception:
            return default

    def _load_selected_channel_into_controls(self) -> None:
        if self.instrument is None:
            return

        ch = self.selected_channel
        inst = self.instrument

        self.waveform_var.set(self._safe_str(lambda: inst.get_function(ch), default=self.waveform_var.get()))
        self.freq_var.set(str(self._safe_number(lambda: inst.get_frequency(ch), self.freq_var.get())))
        self.amp_var.set(str(self._safe_number(lambda: inst.get_amplitude(ch), self.amp_var.get())))
        self.offset_var.set(str(self._safe_number(lambda: inst.get_offset(ch), self.offset_var.get())))
        self.phase_var.set(str(self._safe_number(lambda: inst.get_phase(ch), self.phase_var.get())))
        self.load_var.set(str(self._safe_number(lambda: inst.get_load(ch), self.load_var.get())))
        self.unit_var.set(self._safe_str(lambda: inst.get_amplitude_unit(ch), default=self.unit_var.get()))

        self.sweep_enable_var.set(self.states[ch].sweep_on)
        self.burst_enable_var.set(self.states[ch].burst_on)
        self.trigger_source_var.set(self.states[ch].trigger_source)

    @staticmethod
    def _safe_number(fn, fallback: str) -> float | str:
        try:
            return fn()
        except Exception:
            return fallback

    def _refresh_channel_buttons(self) -> None:
        for ch in (1, 2):
            focus = self.channel_focus_buttons[ch]
            out = self.channel_output_buttons[ch]
            is_focus = ch == self.selected_channel
            state = self.states[ch]

            focus.configure(
                bg="#a8772c" if is_focus else "#2d333b",
                fg="#111111" if is_focus else "#f0f0f0",
            )
            out.configure(
                text="OUT ON" if state.output_on else "OUT OFF",
                bg="#6ca93f" if state.output_on else "#503434",
            )

    def _refresh_mode_buttons(self) -> None:
        state = self.states[self.selected_channel]
        lit = {
            "Modulate": state.modulation_on,
            "Sweep": state.sweep_on,
            "Burst": state.burst_on,
            "Trigger": state.trigger_waiting,
        }

        for mode, btn in self.mode_buttons.items():
            mode_selected = mode == self.current_mode
            mode_lit = lit.get(mode, False)
            if mode_lit and mode_selected:
                btn.configure(bg="#f0c543", fg="#151515")
            elif mode_lit:
                btn.configure(bg="#a57d1c", fg="#ffffff")
            elif mode_selected:
                btn.configure(bg="#546e8a", fg="#ffffff")
            else:
                btn.configure(bg="#313740", fg="#f5f5f5")

    def _compose_status_message(self, channel: int) -> str:
        s = self.states[channel]
        parts = [f"CH{channel}"]

        if s.modulation_on:
            parts.append(f"{s.modulation_label} Modulated")
        if s.sweep_on:
            parts.append("Sweep On")
        if s.burst_on:
            parts.append("Burst On")
        if s.trigger_waiting:
            parts.append(f"Trigger Armed ({s.trigger_source})")
        if not (s.modulation_on or s.sweep_on or s.burst_on):
            parts.append("Base Waveform")

        return " | ".join(parts)


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Keysight 33600A control panel")
    parser.add_argument("--simulate", action="store_true", help="Run without hardware")
    args = parser.parse_args(argv)

    app = Keysight33600AFrontPanel(simulate=args.simulate)
    app.mainloop()


if __name__ == "__main__":
    main()
