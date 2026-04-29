from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Union

import pyvisa

from .errors import (
    ConnectionError33600A,
    Keysight33600AError,
    SCPICommandError,
    ValidationError33600A,
)
from .models import (
    AmplitudeUnit,
    BurstMode,
    ModulationSource,
    SweepSpacing,
    TriggerSlope,
    TriggerSource,
    WaveformShape,
)

ShapeLike = Union[WaveformShape, str]
UnitLike = Union[AmplitudeUnit, str]
BurstModeLike = Union[BurstMode, str]
TriggerSourceLike = Union[TriggerSource, str]
TriggerSlopeLike = Union[TriggerSlope, str]
SweepSpacingLike = Union[SweepSpacing, str]
ModulationSourceLike = Union[ModulationSource, str]


@dataclass
class ErrorEntry:
    code: int
    message: str


class Keysight33600A:
    """Minimal, robust SCPI control wrapper for Keysight 33600A series generators."""

    def __init__(
        self,
        resource_name: str,
        timeout_ms: int = 5000,
        write_termination: str = "\n",
        read_termination: str = "\n",
    ) -> None:
        self.resource_name = resource_name
        self.timeout_ms = timeout_ms
        self.write_termination = write_termination
        self.read_termination = read_termination

        self._rm: Optional[pyvisa.ResourceManager] = None
        self._inst = None

    def __enter__(self) -> "Keysight33600A":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.disconnect()

    @property
    def is_connected(self) -> bool:
        return self._inst is not None

    def connect(self) -> None:
        if self._inst is not None:
            return

        try:
            self._rm = pyvisa.ResourceManager()
            self._inst = self._rm.open_resource(self.resource_name)
            self._inst.timeout = self.timeout_ms
            self._inst.write_termination = self.write_termination
            self._inst.read_termination = self.read_termination
        except Exception as exc:
            self._inst = None
            # Do NOT close self._rm here — closing a ResourceManager on NI-VISA can
            # invalidate VISA sessions opened through other RMs in the same process.
            raise ConnectionError33600A(
                f"Failed to connect to {self.resource_name}: {exc}"
            ) from exc

    def disconnect(self) -> None:
        errors: List[Exception] = []

        if self._inst is not None:
            try:
                self._inst.close()
            except Exception as exc:
                errors.append(exc)
            finally:
                self._inst = None

        # Keep self._rm alive — closing it can invalidate other VISA sessions in the process.
        # The RM will be cleaned up when this object is garbage-collected or the process exits.

        if errors:
            raise ConnectionError33600A(f"Disconnect encountered errors: {errors[0]}")

    def write(self, command: str) -> None:
        self._require_connection()
        self._inst.write(command)

    def query(self, command: str) -> str:
        self._require_connection()
        return str(self._inst.query(command)).strip()

    def ask_float(self, command: str) -> float:
        return float(self.query(command))

    def ask_int(self, command: str) -> int:
        return int(float(self.query(command)))

    def identify(self) -> str:
        return self.query("*IDN?")

    def reset(self) -> None:
        self.write("*RST")

    def clear_status(self) -> None:
        self.write("*CLS")

    def get_status_byte(self) -> int:
        return self.ask_int("*STB?")

    def get_event_status(self) -> int:
        return self.ask_int("*ESR?")

    def set_event_enable(self, mask: int) -> None:
        self._validate_register_mask(mask)
        self.write(f"*ESE {int(mask)}")

    def get_event_enable(self) -> int:
        return self.ask_int("*ESE?")

    def set_service_request_enable(self, mask: int) -> None:
        self._validate_register_mask(mask)
        self.write(f"*SRE {int(mask)}")

    def get_service_request_enable(self) -> int:
        return self.ask_int("*SRE?")

    def save_state(self, slot: int) -> None:
        self._validate_state_slot(slot)
        self.write(f"*SAV {int(slot)}")

    def recall_state(self, slot: int) -> None:
        self._validate_state_slot(slot)
        self.write(f"*RCL {int(slot)}")

    def operation_complete(self) -> bool:
        return self.ask_int("*OPC?") == 1

    def trigger(self) -> None:
        self.write("*TRG")

    def set_output(self, channel: int, state: bool) -> None:
        ch = self._validate_channel(channel)
        self.write(f"OUTP{ch} {'ON' if state else 'OFF'}")

    def get_output(self, channel: int) -> bool:
        ch = self._validate_channel(channel)
        return self.ask_int(f"OUTP{ch}?") == 1

    def set_load(self, channel: int, load_ohm: Union[float, str]) -> None:
        ch = self._validate_channel(channel)
        if isinstance(load_ohm, str):
            normalized = load_ohm.strip().upper()
            if normalized not in {"INF", "INFINITY", "MIN", "MAX"}:
                raise ValidationError33600A(
                    "String load must be one of INF/INFINITY/MIN/MAX"
                )
            cmd = "INF" if normalized in {"INF", "INFINITY"} else normalized
            self.write(f"OUTP{ch}:LOAD {cmd}")
            return

        if load_ohm <= 0:
            raise ValidationError33600A("Load must be positive")
        self.write(f"OUTP{ch}:LOAD {float(load_ohm)}")

    def get_load(self, channel: int) -> float:
        ch = self._validate_channel(channel)
        return self.ask_float(f"OUTP{ch}:LOAD?")

    def set_function(self, channel: int, shape: ShapeLike) -> None:
        ch = self._validate_channel(channel)
        value = self._normalize_enum_or_string(shape, WaveformShape, "shape")
        self.write(f"SOUR{ch}:FUNC {value}")

    def get_function(self, channel: int) -> str:
        ch = self._validate_channel(channel)
        return self.query(f"SOUR{ch}:FUNC?")

    def set_frequency(self, channel: int, frequency_hz: float) -> None:
        ch = self._validate_channel(channel)
        if frequency_hz <= 0:
            raise ValidationError33600A("Frequency must be > 0")
        self.write(f"SOUR{ch}:FREQ {float(frequency_hz)}")

    def get_frequency(self, channel: int) -> float:
        ch = self._validate_channel(channel)
        return self.ask_float(f"SOUR{ch}:FREQ?")

    def set_amplitude(self, channel: int, value: float) -> None:
        ch = self._validate_channel(channel)
        if value < 0:
            raise ValidationError33600A("Amplitude must be >= 0")
        self.write(f"SOUR{ch}:VOLT {float(value)}")

    def get_amplitude(self, channel: int) -> float:
        ch = self._validate_channel(channel)
        return self.ask_float(f"SOUR{ch}:VOLT?")

    def set_amplitude_unit(self, channel: int, unit: UnitLike) -> None:
        ch = self._validate_channel(channel)
        value = self._normalize_enum_or_string(unit, AmplitudeUnit, "unit")
        self.write(f"SOUR{ch}:VOLT:UNIT {value}")

    def get_amplitude_unit(self, channel: int) -> str:
        ch = self._validate_channel(channel)
        return self.query(f"SOUR{ch}:VOLT:UNIT?")

    def set_offset(self, channel: int, offset_v: float) -> None:
        ch = self._validate_channel(channel)
        self.write(f"SOUR{ch}:VOLT:OFFS {float(offset_v)}")

    def get_offset(self, channel: int) -> float:
        ch = self._validate_channel(channel)
        return self.ask_float(f"SOUR{ch}:VOLT:OFFS?")

    def set_phase(self, channel: int, phase_deg: float) -> None:
        ch = self._validate_channel(channel)
        self.write(f"SOUR{ch}:PHAS {float(phase_deg)}")

    def get_phase(self, channel: int) -> float:
        ch = self._validate_channel(channel)
        return self.ask_float(f"SOUR{ch}:PHAS?")

    def set_burst_enabled(self, channel: int, enabled: bool) -> None:
        ch = self._validate_channel(channel)
        self.write(f"SOUR{ch}:BURS:STAT {'ON' if enabled else 'OFF'}")

    def get_burst_enabled(self, channel: int) -> bool:
        ch = self._validate_channel(channel)
        return self.ask_int(f"SOUR{ch}:BURS:STAT?") == 1

    def set_burst_mode(self, channel: int, mode: BurstModeLike) -> None:
        ch = self._validate_channel(channel)
        value = self._normalize_enum_or_string(mode, BurstMode, "burst mode")
        self.write(f"SOUR{ch}:BURS:MODE {value}")

    def get_burst_mode(self, channel: int) -> str:
        ch = self._validate_channel(channel)
        return self.query(f"SOUR{ch}:BURS:MODE?")

    def set_burst_ncycles(self, channel: int, ncycles: int) -> None:
        ch = self._validate_channel(channel)
        if ncycles <= 0:
            raise ValidationError33600A("Burst cycles must be >= 1")
        self.write(f"SOUR{ch}:BURS:NCYC {int(ncycles)}")

    def get_burst_ncycles(self, channel: int) -> int:
        ch = self._validate_channel(channel)
        return self.ask_int(f"SOUR{ch}:BURS:NCYC?")

    def set_burst_period(self, channel: int, period_s: float) -> None:
        ch = self._validate_channel(channel)
        if period_s <= 0:
            raise ValidationError33600A("Burst period must be > 0")
        self.write(f"SOUR{ch}:BURS:INT:PER {float(period_s)}")

    def get_burst_period(self, channel: int) -> float:
        ch = self._validate_channel(channel)
        return self.ask_float(f"SOUR{ch}:BURS:INT:PER?")

    def set_trigger_source(self, channel: int, source: TriggerSourceLike) -> None:
        ch = self._validate_channel(channel)
        value = self._normalize_enum_or_string(source, TriggerSource, "trigger source")
        self.write(f"TRIG{ch}:SOUR {value}")

    def get_trigger_source(self, channel: int) -> str:
        ch = self._validate_channel(channel)
        return self.query(f"TRIG{ch}:SOUR?")

    def set_trigger_count(self, channel: int, count: int) -> None:
        ch = self._validate_channel(channel)
        if count <= 0:
            raise ValidationError33600A("Trigger count must be >= 1")
        self.write(f"TRIG{ch}:COUN {int(count)}")

    def get_trigger_count(self, channel: int) -> int:
        ch = self._validate_channel(channel)
        return self.ask_int(f"TRIG{ch}:COUN?")

    def set_trigger_delay(self, channel: int, delay_s: float) -> None:
        ch = self._validate_channel(channel)
        if delay_s < 0:
            raise ValidationError33600A("Trigger delay must be >= 0")
        self.write(f"TRIG{ch}:DEL {float(delay_s)}")

    def get_trigger_delay(self, channel: int) -> float:
        ch = self._validate_channel(channel)
        return self.ask_float(f"TRIG{ch}:DEL?")

    def set_trigger_timer(self, channel: int, period_s: float) -> None:
        ch = self._validate_channel(channel)
        if period_s <= 0:
            raise ValidationError33600A("Trigger timer period must be > 0")
        self.write(f"TRIG{ch}:TIM {float(period_s)}")

    def get_trigger_timer(self, channel: int) -> float:
        ch = self._validate_channel(channel)
        return self.ask_float(f"TRIG{ch}:TIM?")

    def set_trigger_slope(self, channel: int, slope: TriggerSlopeLike) -> None:
        ch = self._validate_channel(channel)
        value = self._normalize_enum_or_string(slope, TriggerSlope, "trigger slope")
        self.write(f"TRIG{ch}:SLOP {value}")

    def get_trigger_slope(self, channel: int) -> str:
        ch = self._validate_channel(channel)
        return self.query(f"TRIG{ch}:SLOP?")

    def set_sweep_enabled(self, channel: int, enabled: bool) -> None:
        ch = self._validate_channel(channel)
        self.write(f"SOUR{ch}:SWE:STAT {'ON' if enabled else 'OFF'}")

    def get_sweep_enabled(self, channel: int) -> bool:
        ch = self._validate_channel(channel)
        return self.ask_int(f"SOUR{ch}:SWE:STAT?") == 1

    def set_sweep_start(self, channel: int, frequency_hz: float) -> None:
        ch = self._validate_channel(channel)
        if frequency_hz <= 0:
            raise ValidationError33600A("Sweep start frequency must be > 0")
        self.write(f"SOUR{ch}:FREQ:STAR {float(frequency_hz)}")

    def get_sweep_start(self, channel: int) -> float:
        ch = self._validate_channel(channel)
        return self.ask_float(f"SOUR{ch}:FREQ:STAR?")

    def set_sweep_stop(self, channel: int, frequency_hz: float) -> None:
        ch = self._validate_channel(channel)
        if frequency_hz <= 0:
            raise ValidationError33600A("Sweep stop frequency must be > 0")
        self.write(f"SOUR{ch}:FREQ:STOP {float(frequency_hz)}")

    def get_sweep_stop(self, channel: int) -> float:
        ch = self._validate_channel(channel)
        return self.ask_float(f"SOUR{ch}:FREQ:STOP?")

    def set_sweep_time(self, channel: int, sweep_time_s: float) -> None:
        ch = self._validate_channel(channel)
        if sweep_time_s <= 0:
            raise ValidationError33600A("Sweep time must be > 0")
        self.write(f"SOUR{ch}:SWE:TIME {float(sweep_time_s)}")

    def get_sweep_time(self, channel: int) -> float:
        ch = self._validate_channel(channel)
        return self.ask_float(f"SOUR{ch}:SWE:TIME?")

    def set_sweep_spacing(self, channel: int, spacing: SweepSpacingLike) -> None:
        ch = self._validate_channel(channel)
        value = self._normalize_enum_or_string(spacing, SweepSpacing, "sweep spacing")
        self.write(f"SOUR{ch}:SWE:SPAC {value}")

    def get_sweep_spacing(self, channel: int) -> str:
        ch = self._validate_channel(channel)
        return self.query(f"SOUR{ch}:SWE:SPAC?")

    def set_sweep_hold_time(self, channel: int, hold_time_s: float) -> None:
        ch = self._validate_channel(channel)
        if hold_time_s < 0:
            raise ValidationError33600A("Sweep hold time must be >= 0")
        self.write(f"SOUR{ch}:SWE:HTIM {float(hold_time_s)}")

    def get_sweep_hold_time(self, channel: int) -> float:
        ch = self._validate_channel(channel)
        return self.ask_float(f"SOUR{ch}:SWE:HTIM?")

    def set_sweep_return_time(self, channel: int, return_time_s: float) -> None:
        ch = self._validate_channel(channel)
        if return_time_s < 0:
            raise ValidationError33600A("Sweep return time must be >= 0")
        self.write(f"SOUR{ch}:SWE:RTIM {float(return_time_s)}")

    def get_sweep_return_time(self, channel: int) -> float:
        ch = self._validate_channel(channel)
        return self.ask_float(f"SOUR{ch}:SWE:RTIM?")

    def set_sweep_trigger_source(
        self, channel: int, source: TriggerSourceLike
    ) -> None:
        ch = self._validate_channel(channel)
        value = self._normalize_enum_or_string(source, TriggerSource, "sweep trigger source")
        self.write(f"SOUR{ch}:SWE:TRIG:SOUR {value}")

    def get_sweep_trigger_source(self, channel: int) -> str:
        ch = self._validate_channel(channel)
        return self.query(f"SOUR{ch}:SWE:TRIG:SOUR?")

    def set_am_enabled(self, channel: int, enabled: bool) -> None:
        ch = self._validate_channel(channel)
        self.write(f"SOUR{ch}:AM:STAT {'ON' if enabled else 'OFF'}")

    def get_am_enabled(self, channel: int) -> bool:
        ch = self._validate_channel(channel)
        return self.ask_int(f"SOUR{ch}:AM:STAT?") == 1

    def set_am_depth(self, channel: int, depth_percent: float) -> None:
        ch = self._validate_channel(channel)
        if depth_percent < 0:
            raise ValidationError33600A("AM depth must be >= 0")
        self.write(f"SOUR{ch}:AM:DEPT {float(depth_percent)}")

    def get_am_depth(self, channel: int) -> float:
        ch = self._validate_channel(channel)
        return self.ask_float(f"SOUR{ch}:AM:DEPT?")

    def set_am_source(self, channel: int, source: ModulationSourceLike) -> None:
        ch = self._validate_channel(channel)
        value = self._normalize_enum_or_string(source, ModulationSource, "AM source")
        self.write(f"SOUR{ch}:AM:SOUR {value}")

    def get_am_source(self, channel: int) -> str:
        ch = self._validate_channel(channel)
        return self.query(f"SOUR{ch}:AM:SOUR?")

    def set_fm_enabled(self, channel: int, enabled: bool) -> None:
        ch = self._validate_channel(channel)
        self.write(f"SOUR{ch}:FM:STAT {'ON' if enabled else 'OFF'}")

    def get_fm_enabled(self, channel: int) -> bool:
        ch = self._validate_channel(channel)
        return self.ask_int(f"SOUR{ch}:FM:STAT?") == 1

    def set_fm_deviation(self, channel: int, deviation_hz: float) -> None:
        ch = self._validate_channel(channel)
        if deviation_hz < 0:
            raise ValidationError33600A("FM deviation must be >= 0")
        self.write(f"SOUR{ch}:FM:DEV {float(deviation_hz)}")

    def get_fm_deviation(self, channel: int) -> float:
        ch = self._validate_channel(channel)
        return self.ask_float(f"SOUR{ch}:FM:DEV?")

    def set_fm_source(self, channel: int, source: ModulationSourceLike) -> None:
        ch = self._validate_channel(channel)
        value = self._normalize_enum_or_string(source, ModulationSource, "FM source")
        self.write(f"SOUR{ch}:FM:SOUR {value}")

    def get_fm_source(self, channel: int) -> str:
        ch = self._validate_channel(channel)
        return self.query(f"SOUR{ch}:FM:SOUR?")

    def set_pm_enabled(self, channel: int, enabled: bool) -> None:
        ch = self._validate_channel(channel)
        self.write(f"SOUR{ch}:PM:STAT {'ON' if enabled else 'OFF'}")

    def get_pm_enabled(self, channel: int) -> bool:
        ch = self._validate_channel(channel)
        return self.ask_int(f"SOUR{ch}:PM:STAT?") == 1

    def set_pm_deviation(self, channel: int, deviation_deg: float) -> None:
        ch = self._validate_channel(channel)
        if deviation_deg < 0:
            raise ValidationError33600A("PM deviation must be >= 0")
        self.write(f"SOUR{ch}:PM:DEV {float(deviation_deg)}")

    def get_pm_deviation(self, channel: int) -> float:
        ch = self._validate_channel(channel)
        return self.ask_float(f"SOUR{ch}:PM:DEV?")

    def set_pm_source(self, channel: int, source: ModulationSourceLike) -> None:
        ch = self._validate_channel(channel)
        value = self._normalize_enum_or_string(source, ModulationSource, "PM source")
        self.write(f"SOUR{ch}:PM:SOUR {value}")

    def get_pm_source(self, channel: int) -> str:
        ch = self._validate_channel(channel)
        return self.query(f"SOUR{ch}:PM:SOUR?")

    def set_fsk_enabled(self, channel: int, enabled: bool) -> None:
        ch = self._validate_channel(channel)
        self.write(f"SOUR{ch}:FSK:STAT {'ON' if enabled else 'OFF'}")

    def get_fsk_enabled(self, channel: int) -> bool:
        ch = self._validate_channel(channel)
        return self.ask_int(f"SOUR{ch}:FSK:STAT?") == 1

    def set_fsk_frequency(self, channel: int, frequency_hz: float) -> None:
        ch = self._validate_channel(channel)
        if frequency_hz <= 0:
            raise ValidationError33600A("FSK frequency must be > 0")
        self.write(f"SOUR{ch}:FSK:FREQ {float(frequency_hz)}")

    def get_fsk_frequency(self, channel: int) -> float:
        ch = self._validate_channel(channel)
        return self.ask_float(f"SOUR{ch}:FSK:FREQ?")

    def set_fsk_source(self, channel: int, source: ModulationSourceLike) -> None:
        ch = self._validate_channel(channel)
        value = self._normalize_enum_or_string(source, ModulationSource, "FSK source")
        self.write(f"SOUR{ch}:FSK:SOUR {value}")

    def get_fsk_source(self, channel: int) -> str:
        ch = self._validate_channel(channel)
        return self.query(f"SOUR{ch}:FSK:SOUR?")

    def set_bpsk_enabled(self, channel: int, enabled: bool) -> None:
        ch = self._validate_channel(channel)
        self.write(f"SOUR{ch}:BPSK:STAT {'ON' if enabled else 'OFF'}")

    def get_bpsk_enabled(self, channel: int) -> bool:
        ch = self._validate_channel(channel)
        return self.ask_int(f"SOUR{ch}:BPSK:STAT?") == 1

    def set_bpsk_phase(self, channel: int, phase_deg: float) -> None:
        ch = self._validate_channel(channel)
        self.write(f"SOUR{ch}:BPSK:PHAS {float(phase_deg)}")

    def get_bpsk_phase(self, channel: int) -> float:
        ch = self._validate_channel(channel)
        return self.ask_float(f"SOUR{ch}:BPSK:PHAS?")

    def set_bpsk_source(self, channel: int, source: ModulationSourceLike) -> None:
        ch = self._validate_channel(channel)
        value = self._normalize_enum_or_string(source, ModulationSource, "BPSK source")
        self.write(f"SOUR{ch}:BPSK:SOUR {value}")

    def get_bpsk_source(self, channel: int) -> str:
        ch = self._validate_channel(channel)
        return self.query(f"SOUR{ch}:BPSK:SOUR?")

    def upload_arb_waveform_floats(
        self,
        channel: int,
        name: str,
        samples: Sequence[float],
    ) -> None:
        """Upload an arbitrary waveform from float samples expected in [-1, 1]."""
        ch = self._validate_channel(channel)
        self._validate_waveform_name(name)
        if not samples:
            raise ValidationError33600A("Arbitrary waveform samples cannot be empty")

        for idx, val in enumerate(samples):
            if val < -1.0 or val > 1.0:
                raise ValidationError33600A(
                    f"Sample {idx}={val} outside normalized range [-1, 1]"
                )

        csv = ",".join(f"{float(v):.6g}" for v in samples)
        self.write(f'SOUR{ch}:DATA:ARB {name},{csv}')

    def upload_arb_waveform_dac(
        self,
        channel: int,
        name: str,
        samples: Sequence[int],
    ) -> None:
        """Upload an arbitrary waveform from integer DAC values."""
        ch = self._validate_channel(channel)
        self._validate_waveform_name(name)
        if not samples:
            raise ValidationError33600A("Arbitrary waveform samples cannot be empty")

        csv = ",".join(str(int(v)) for v in samples)
        self.write(f'SOUR{ch}:DATA:DAC {name},{csv}')

    def select_arb_waveform(self, channel: int, name: str) -> None:
        ch = self._validate_channel(channel)
        self._validate_waveform_name(name)
        self.write(f'SOUR{ch}:FUNC:ARB "{name}"')
        self.write(f"SOUR{ch}:FUNC ARB")

    def set_arb_sample_rate(self, channel: int, sample_rate_hz: float) -> None:
        ch = self._validate_channel(channel)
        if sample_rate_hz <= 0:
            raise ValidationError33600A("Arbitrary sample rate must be > 0")
        self.write(f"SOUR{ch}:FUNC:ARB:SRAT {float(sample_rate_hz)}")

    def clear_volatile_arb(self, channel: int) -> None:
        ch = self._validate_channel(channel)
        self.write(f"SOUR{ch}:DATA:VOL:CLE")

    def get_volatile_arb_catalog(self, channel: int) -> str:
        ch = self._validate_channel(channel)
        return self.query(f"SOUR{ch}:DATA:VOL:CAT?")

    def get_volatile_arb_free(self, channel: int) -> int:
        ch = self._validate_channel(channel)
        return self.ask_int(f"SOUR{ch}:DATA:VOL:FREE?")

    def upload_arb_waveform_binary(self, channel: int, name: str, data: bytes) -> None:
        """Upload arbitrary waveform payload using SCPI definite-length binary block."""
        ch = self._validate_channel(channel)
        self._validate_waveform_name(name)
        if not data:
            raise ValidationError33600A("Binary waveform payload cannot be empty")

        self._require_connection()
        size_text = str(len(data))
        header = f"#{len(size_text)}{size_text}".encode("ascii")
        prefix = f"SOUR{ch}:DATA:ARB:DAC {name},".encode("ascii")
        self._inst.write_raw(prefix + header + data)

    def get_system_errors(self, max_reads: int = 20) -> List[ErrorEntry]:
        if max_reads <= 0:
            raise ValidationError33600A("max_reads must be > 0")

        errors: List[ErrorEntry] = []
        for _ in range(max_reads):
            response = self.query("SYST:ERR?")
            entry = self._parse_error_entry(response)
            if entry.code == 0:
                break
            errors.append(entry)
        return errors

    def raise_for_instrument_errors(self, max_reads: int = 20) -> None:
        errors = self.get_system_errors(max_reads=max_reads)
        if not errors:
            return
        joined = "; ".join(f"{e.code}:{e.message}" for e in errors)
        raise SCPICommandError(f"Instrument error queue not empty: {joined}")

    def execute_checked(self, command: str, max_reads: int = 20) -> None:
        self.write(command)
        self.raise_for_instrument_errors(max_reads=max_reads)

    def _require_connection(self) -> None:
        if self._inst is None:
            raise ConnectionError33600A("Instrument not connected")

    @staticmethod
    def _validate_register_mask(mask: int) -> None:
        if mask < 0 or mask > 255:
            raise ValidationError33600A("Register mask must be in [0, 255]")

    @staticmethod
    def _validate_state_slot(slot: int) -> None:
        if slot not in (0, 1, 2, 3, 4):
            raise ValidationError33600A("State slot must be one of 0,1,2,3,4")

    @staticmethod
    def _validate_channel(channel: int) -> int:
        if channel not in (1, 2):
            raise ValidationError33600A("Channel must be 1 or 2")
        return channel

    @staticmethod
    def _validate_waveform_name(name: str) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValidationError33600A("Waveform name must be a non-empty string")

    @staticmethod
    def _normalize_enum_or_string(value, enum_cls, field_name: str) -> str:
        if isinstance(value, enum_cls):
            return value.value
        if isinstance(value, str):
            normalized = value.strip().upper()
            if normalized in {item.value for item in enum_cls}:
                return normalized
        valid = ", ".join(item.value for item in enum_cls)
        raise ValidationError33600A(f"Invalid {field_name}. Expected one of: {valid}")

    @staticmethod
    def _parse_error_entry(response: str) -> ErrorEntry:
        text = response.strip()
        if not text:
            return ErrorEntry(code=0, message="No error")

        parts = text.split(",", 1)
        if len(parts) == 1:
            try:
                return ErrorEntry(code=int(parts[0]), message="")
            except ValueError:
                return ErrorEntry(code=-1, message=text)

        code_text, message = parts
        try:
            code = int(code_text)
        except ValueError:
            code = -1

        cleaned_message = message.strip().strip('"')
        return ErrorEntry(code=code, message=cleaned_message)
