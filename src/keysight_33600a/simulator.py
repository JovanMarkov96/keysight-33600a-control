from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .models import AmplitudeUnit, BurstMode, ModulationSource, SweepSpacing, TriggerSlope, TriggerSource, WaveformShape
from .validation import (
    validate_count,
    validate_frequency,
    validate_non_negative_value,
    validate_positive_value,
    validate_sweep_shape,
    validate_voltage_settings,
)


@dataclass
class _ChannelState:
    output: bool = False
    load: float | str = 50.0
    function: str = WaveformShape.SIN.value
    frequency_hz: float = 1_000.0
    amplitude: float = 0.1
    amplitude_unit: str = AmplitudeUnit.VPP.value
    offset_v: float = 0.0
    phase_deg: float = 0.0
    burst_enabled: bool = False
    burst_mode: str = BurstMode.TRIG.value
    burst_cycles: int = 1
    burst_period_s: float = 0.02
    trigger_source: str = TriggerSource.IMM.value
    trigger_count: int = 1
    trigger_delay_s: float = 0.0
    trigger_timer_s: float = 0.5
    trigger_slope: str = TriggerSlope.POS.value
    sweep_enabled: bool = False
    sweep_start_hz: float = 50.0
    sweep_stop_hz: float = 5_000.0
    sweep_time_s: float = 1.0
    sweep_spacing: str = SweepSpacing.LIN.value
    sweep_hold_s: float = 0.0
    sweep_return_s: float = 0.0
    sweep_trigger_source: str = TriggerSource.IMM.value
    am_enabled: bool = False
    am_depth: float = 50.0
    am_source: str = ModulationSource.INT.value
    fm_enabled: bool = False
    fm_deviation: float = 1_000.0
    fm_source: str = ModulationSource.INT.value
    pm_enabled: bool = False
    pm_deviation: float = 10.0
    pm_source: str = ModulationSource.INT.value
    fsk_enabled: bool = False
    fsk_frequency: float = 1_000.0
    fsk_source: str = ModulationSource.INT.value
    bpsk_enabled: bool = False
    bpsk_phase: float = 180.0
    bpsk_source: str = ModulationSource.INT.value


@dataclass
class SimulatedKeysight33600A:
    resource_name: str = "SIM::KEYSIGHT33600A"
    _connected: bool = False
    _errors: List[str] = field(default_factory=list)
    _channels: Dict[int, _ChannelState] = field(default_factory=lambda: {1: _ChannelState(), 2: _ChannelState()})

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    def identify(self) -> str:
        return "Agilent Technologies,33622A,SIMULATED,0.1"

    def reset(self) -> None:
        self._channels = {1: _ChannelState(), 2: _ChannelState()}

    def clear_status(self) -> None:
        self._errors.clear()

    def get_system_errors(self, max_reads: int = 20):
        from .instrument import ErrorEntry

        errors: List[ErrorEntry] = []
        for item in self._errors[:max_reads]:
            errors.append(ErrorEntry(code=-1, message=item))
        self._errors.clear()
        return errors

    def save_state(self, slot: int) -> None:
        validate_count("State slot", slot if slot > 0 else 1)

    def recall_state(self, slot: int) -> None:
        validate_count("State slot", slot if slot > 0 else 1)

    def trigger(self) -> None:
        return None

    def set_output(self, channel: int, state: bool) -> None:
        self._channel(channel).output = bool(state)

    def get_output(self, channel: int) -> bool:
        return self._channel(channel).output

    def set_load(self, channel: int, load_ohm):
        self._channel(channel).load = load_ohm

    def get_load(self, channel: int):
        return self._channel(channel).load

    def set_function(self, channel: int, shape):
        self._channel(channel).function = self._normalize(shape)

    def get_function(self, channel: int) -> str:
        return self._channel(channel).function

    def set_frequency(self, channel: int, frequency_hz: float) -> None:
        state = self._channel(channel)
        validate_frequency(state.function, frequency_hz)
        state.frequency_hz = frequency_hz

    def get_frequency(self, channel: int) -> float:
        return self._channel(channel).frequency_hz

    def set_amplitude(self, channel: int, value: float) -> None:
        state = self._channel(channel)
        validate_voltage_settings(value, state.offset_v, state.load)
        state.amplitude = value

    def get_amplitude(self, channel: int) -> float:
        return self._channel(channel).amplitude

    def set_amplitude_unit(self, channel: int, unit) -> None:
        self._channel(channel).amplitude_unit = self._normalize(unit)

    def get_amplitude_unit(self, channel: int) -> str:
        return self._channel(channel).amplitude_unit

    def set_offset(self, channel: int, offset_v: float) -> None:
        state = self._channel(channel)
        validate_voltage_settings(state.amplitude, offset_v, state.load)
        state.offset_v = offset_v

    def get_offset(self, channel: int) -> float:
        return self._channel(channel).offset_v

    def set_phase(self, channel: int, phase_deg: float) -> None:
        self._channel(channel).phase_deg = phase_deg

    def get_phase(self, channel: int) -> float:
        return self._channel(channel).phase_deg

    def set_burst_enabled(self, channel: int, enabled: bool) -> None:
        self._channel(channel).burst_enabled = bool(enabled)

    def get_burst_enabled(self, channel: int) -> bool:
        return self._channel(channel).burst_enabled

    def set_burst_mode(self, channel: int, mode) -> None:
        self._channel(channel).burst_mode = self._normalize(mode)

    def get_burst_mode(self, channel: int) -> str:
        return self._channel(channel).burst_mode

    def set_burst_ncycles(self, channel: int, ncycles: int) -> None:
        validate_count("Burst cycles", ncycles)
        self._channel(channel).burst_cycles = ncycles

    def get_burst_ncycles(self, channel: int) -> int:
        return self._channel(channel).burst_cycles

    def set_burst_period(self, channel: int, period_s: float) -> None:
        validate_positive_value("Burst period", period_s)
        self._channel(channel).burst_period_s = period_s

    def get_burst_period(self, channel: int) -> float:
        return self._channel(channel).burst_period_s

    def set_trigger_source(self, channel: int, source) -> None:
        self._channel(channel).trigger_source = self._normalize(source)

    def get_trigger_source(self, channel: int) -> str:
        return self._channel(channel).trigger_source

    def set_trigger_count(self, channel: int, count: int) -> None:
        validate_count("Trigger count", count)
        self._channel(channel).trigger_count = count

    def get_trigger_count(self, channel: int) -> int:
        return self._channel(channel).trigger_count

    def set_trigger_delay(self, channel: int, delay_s: float) -> None:
        validate_non_negative_value("Trigger delay", delay_s)
        self._channel(channel).trigger_delay_s = delay_s

    def get_trigger_delay(self, channel: int) -> float:
        return self._channel(channel).trigger_delay_s

    def set_trigger_timer(self, channel: int, period_s: float) -> None:
        validate_positive_value("Trigger timer", period_s)
        self._channel(channel).trigger_timer_s = period_s

    def get_trigger_timer(self, channel: int) -> float:
        return self._channel(channel).trigger_timer_s

    def set_trigger_slope(self, channel: int, slope) -> None:
        self._channel(channel).trigger_slope = self._normalize(slope)

    def get_trigger_slope(self, channel: int) -> str:
        return self._channel(channel).trigger_slope

    def set_sweep_enabled(self, channel: int, enabled: bool) -> None:
        self._channel(channel).sweep_enabled = bool(enabled)

    def get_sweep_enabled(self, channel: int) -> bool:
        return self._channel(channel).sweep_enabled

    def set_sweep_start(self, channel: int, frequency_hz: float) -> None:
        validate_positive_value("Sweep start frequency", frequency_hz)
        self._channel(channel).sweep_start_hz = frequency_hz

    def get_sweep_start(self, channel: int) -> float:
        return self._channel(channel).sweep_start_hz

    def set_sweep_stop(self, channel: int, frequency_hz: float) -> None:
        validate_positive_value("Sweep stop frequency", frequency_hz)
        self._channel(channel).sweep_stop_hz = frequency_hz

    def get_sweep_stop(self, channel: int) -> float:
        return self._channel(channel).sweep_stop_hz

    def set_sweep_time(self, channel: int, sweep_time_s: float) -> None:
        validate_positive_value("Sweep time", sweep_time_s)
        self._channel(channel).sweep_time_s = sweep_time_s

    def get_sweep_time(self, channel: int) -> float:
        return self._channel(channel).sweep_time_s

    def set_sweep_spacing(self, channel: int, spacing) -> None:
        self._channel(channel).sweep_spacing = self._normalize(spacing)

    def get_sweep_spacing(self, channel: int) -> str:
        return self._channel(channel).sweep_spacing

    def set_sweep_hold_time(self, channel: int, hold_time_s: float) -> None:
        validate_non_negative_value("Sweep hold time", hold_time_s)
        self._channel(channel).sweep_hold_s = hold_time_s

    def get_sweep_hold_time(self, channel: int) -> float:
        return self._channel(channel).sweep_hold_s

    def set_sweep_return_time(self, channel: int, return_time_s: float) -> None:
        validate_non_negative_value("Sweep return time", return_time_s)
        self._channel(channel).sweep_return_s = return_time_s

    def get_sweep_return_time(self, channel: int) -> float:
        return self._channel(channel).sweep_return_s

    def set_sweep_trigger_source(self, channel: int, source) -> None:
        self._channel(channel).sweep_trigger_source = self._normalize(source)

    def get_sweep_trigger_source(self, channel: int) -> str:
        return self._channel(channel).sweep_trigger_source

    def set_am_enabled(self, channel: int, enabled: bool) -> None:
        self._channel(channel).am_enabled = bool(enabled)

    def get_am_enabled(self, channel: int) -> bool:
        return self._channel(channel).am_enabled

    def set_am_depth(self, channel: int, depth_percent: float) -> None:
        validate_non_negative_value("AM depth", depth_percent)
        self._channel(channel).am_depth = depth_percent

    def get_am_depth(self, channel: int) -> float:
        return self._channel(channel).am_depth

    def set_am_source(self, channel: int, source) -> None:
        self._channel(channel).am_source = self._normalize(source)

    def get_am_source(self, channel: int) -> str:
        return self._channel(channel).am_source

    def set_fm_enabled(self, channel: int, enabled: bool) -> None:
        self._channel(channel).fm_enabled = bool(enabled)

    def get_fm_enabled(self, channel: int) -> bool:
        return self._channel(channel).fm_enabled

    def set_fm_deviation(self, channel: int, deviation_hz: float) -> None:
        validate_non_negative_value("FM deviation", deviation_hz)
        self._channel(channel).fm_deviation = deviation_hz

    def get_fm_deviation(self, channel: int) -> float:
        return self._channel(channel).fm_deviation

    def set_fm_source(self, channel: int, source) -> None:
        self._channel(channel).fm_source = self._normalize(source)

    def get_fm_source(self, channel: int) -> str:
        return self._channel(channel).fm_source

    def set_pm_enabled(self, channel: int, enabled: bool) -> None:
        self._channel(channel).pm_enabled = bool(enabled)

    def get_pm_enabled(self, channel: int) -> bool:
        return self._channel(channel).pm_enabled

    def set_pm_deviation(self, channel: int, deviation_deg: float) -> None:
        validate_non_negative_value("PM deviation", deviation_deg)
        self._channel(channel).pm_deviation = deviation_deg

    def get_pm_deviation(self, channel: int) -> float:
        return self._channel(channel).pm_deviation

    def set_pm_source(self, channel: int, source) -> None:
        self._channel(channel).pm_source = self._normalize(source)

    def get_pm_source(self, channel: int) -> str:
        return self._channel(channel).pm_source

    def set_fsk_enabled(self, channel: int, enabled: bool) -> None:
        self._channel(channel).fsk_enabled = bool(enabled)

    def get_fsk_enabled(self, channel: int) -> bool:
        return self._channel(channel).fsk_enabled

    def set_fsk_frequency(self, channel: int, frequency_hz: float) -> None:
        validate_positive_value("FSK frequency", frequency_hz)
        self._channel(channel).fsk_frequency = frequency_hz

    def get_fsk_frequency(self, channel: int) -> float:
        return self._channel(channel).fsk_frequency

    def set_fsk_source(self, channel: int, source) -> None:
        self._channel(channel).fsk_source = self._normalize(source)

    def get_fsk_source(self, channel: int) -> str:
        return self._channel(channel).fsk_source

    def set_bpsk_enabled(self, channel: int, enabled: bool) -> None:
        self._channel(channel).bpsk_enabled = bool(enabled)

    def get_bpsk_enabled(self, channel: int) -> bool:
        return self._channel(channel).bpsk_enabled

    def set_bpsk_phase(self, channel: int, phase_deg: float) -> None:
        self._channel(channel).bpsk_phase = phase_deg

    def get_bpsk_phase(self, channel: int) -> float:
        return self._channel(channel).bpsk_phase

    def set_bpsk_source(self, channel: int, source) -> None:
        self._channel(channel).bpsk_source = self._normalize(source)

    def get_bpsk_source(self, channel: int) -> str:
        return self._channel(channel).bpsk_source

    def _channel(self, channel: int) -> _ChannelState:
        if channel not in (1, 2):
            raise ValueError("Channel must be 1 or 2")
        return self._channels[channel]

    @staticmethod
    def _normalize(value) -> str:
        return value.value if hasattr(value, "value") else str(value).strip().upper()