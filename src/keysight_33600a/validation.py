from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from .errors import ValidationError33600A
from .models import WaveformShape

LoadLike = Union[float, str]


@dataclass(frozen=True)
class WaveformFrequencyLimit:
    shape: WaveformShape
    max_hz: float
    note: str


# Conservative 33600-series limits taken from the manual. These stay within the
# documented ranges across the model table and are safe for offline validation.
WAVEFORM_FREQUENCY_LIMITS: dict[WaveformShape, WaveformFrequencyLimit] = {
    WaveformShape.SIN: WaveformFrequencyLimit(WaveformShape.SIN, 60_000_000.0, "33600-series sine limit"),
    WaveformShape.SQU: WaveformFrequencyLimit(WaveformShape.SQU, 50_000_000.0, "33600-series square/pulse limit"),
    WaveformShape.TRI: WaveformFrequencyLimit(WaveformShape.TRI, 800_000.0, "33600-series ramp/triangle limit"),
    WaveformShape.RAMP: WaveformFrequencyLimit(WaveformShape.RAMP, 800_000.0, "33600-series ramp/triangle limit"),
    WaveformShape.PULS: WaveformFrequencyLimit(WaveformShape.PULS, 50_000_000.0, "33600-series square/pulse limit"),
    WaveformShape.NOIS: WaveformFrequencyLimit(WaveformShape.NOIS, 60_000_000.0, "33600-series noise limit"),
    WaveformShape.ARB: WaveformFrequencyLimit(WaveformShape.ARB, 660_000_000.0, "33600-series arbitrary sample rate limit"),
    WaveformShape.PRBS: WaveformFrequencyLimit(WaveformShape.PRBS, 100_000_000.0, "33600-series PRBS limit"),
    WaveformShape.DC: WaveformFrequencyLimit(WaveformShape.DC, 0.0, "DC function does not use frequency"),
}


def normalize_load(load: LoadLike) -> float | str:
    if isinstance(load, str):
        normalized = load.strip().upper()
        if normalized in {"INF", "INFINITY"}:
            return "INF"
        if normalized in {"MIN", "MAX"}:
            return normalized
        try:
            value = float(normalized)
        except ValueError as exc:
            raise ValidationError33600A(
                "Load must be numeric, INF, INFINITY, MIN, or MAX"
            ) from exc
        if value <= 0:
            raise ValidationError33600A("Load must be positive")
        return value

    if load <= 0:
        raise ValidationError33600A("Load must be positive")
    return float(load)


def is_high_impedance_load(load: LoadLike) -> bool:
    normalized = normalize_load(load)
    return isinstance(normalized, str) and normalized == "INF"


def validate_frequency(shape: WaveformShape | str, frequency_hz: float) -> None:
    waveform = WaveformShape(shape) if not isinstance(shape, WaveformShape) else shape
    if frequency_hz <= 0:
        raise ValidationError33600A("Frequency must be > 0")

    limit = WAVEFORM_FREQUENCY_LIMITS[waveform]
    if limit.max_hz > 0 and frequency_hz > limit.max_hz:
        raise ValidationError33600A(
            f"Frequency for {waveform.value} must be <= {limit.max_hz:g} Hz ({limit.note})"
        )


def validate_voltage_settings(amplitude_vpp: float, offset_v: float, load: LoadLike) -> None:
    if amplitude_vpp < 0:
        raise ValidationError33600A("Amplitude must be >= 0")

    normalized_load = normalize_load(load)
    peak_voltage = 10.0 if isinstance(normalized_load, str) and normalized_load == "INF" else 5.0

    if amplitude_vpp > 2 * peak_voltage:
        raise ValidationError33600A(
            f"Amplitude must be <= {2 * peak_voltage:g} Vpp for the selected output termination"
        )

    max_offset = peak_voltage - amplitude_vpp / 2.0
    if abs(offset_v) > max_offset + 1e-12:
        raise ValidationError33600A(
            f"Offset must satisfy |offset| <= {max_offset:g} V for the selected amplitude and termination"
        )


def validate_sweep_shape(shape: WaveformShape | str) -> None:
    waveform = WaveformShape(shape) if not isinstance(shape, WaveformShape) else shape
    if waveform in {WaveformShape.NOIS, WaveformShape.DC}:
        raise ValidationError33600A("Sweep is not supported for noise or DC waveforms")


def validate_positive_value(name: str, value: float) -> None:
    if value <= 0:
        raise ValidationError33600A(f"{name} must be > 0")


def validate_non_negative_value(name: str, value: float) -> None:
    if value < 0:
        raise ValidationError33600A(f"{name} must be >= 0")


def validate_count(name: str, value: int) -> None:
    if value <= 0:
        raise ValidationError33600A(f"{name} must be >= 1")