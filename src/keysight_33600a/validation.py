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


@dataclass(frozen=True)
class FrequencyProfile:
    sine: tuple[tuple[float, float], ...]
    square: tuple[tuple[float, float], ...]
    noise: tuple[tuple[float, float], ...]
    prbs: tuple[tuple[float, float], ...]
    ramp: float
    arb: float


_DEFAULT_PROFILE = FrequencyProfile(
    sine=((4.0, 120_000_000.0), (8.0, 80_000_000.0), (10.0, 60_000_000.0)),
    square=((4.0, 100_000_000.0), (10.0, 50_000_000.0)),
    noise=((4.0, 120_000_000.0), (8.0, 80_000_000.0), (10.0, 60_000_000.0)),
    prbs=((4.0, 200_000_000.0), (10.0, 100_000_000.0)),
    ramp=800_000.0,
    arb=1_000_000_000.0,
)


def _select_max_frequency(profile: tuple[tuple[float, float], ...], amplitude_vpp: float | None) -> float:
    if amplitude_vpp is None:
        return profile[-1][1]

    for amplitude_limit, max_hz in profile:
        if amplitude_vpp <= amplitude_limit:
            return max_hz
    return profile[-1][1]


def _waveform_profile(shape: WaveformShape) -> FrequencyProfile:
    if shape is WaveformShape.DC:
        return _DEFAULT_PROFILE
    return _DEFAULT_PROFILE


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


def validate_frequency(
    shape: WaveformShape | str,
    frequency_hz: float,
    amplitude_vpp: float | None = None,
) -> None:
    waveform = WaveformShape(shape) if not isinstance(shape, WaveformShape) else shape
    if frequency_hz <= 0:
        raise ValidationError33600A("Frequency must be > 0")

    profile = _waveform_profile(waveform)
    if waveform is WaveformShape.SIN:
        max_hz = _select_max_frequency(profile.sine, amplitude_vpp)
        note = "33622A sine frequency limit"
    elif waveform in {WaveformShape.SQU, WaveformShape.PULS}:
        max_hz = _select_max_frequency(profile.square, amplitude_vpp)
        note = "33622A square/pulse frequency limit"
    elif waveform in {WaveformShape.TRI, WaveformShape.RAMP}:
        max_hz = profile.ramp
        note = "33622A ramp/triangle frequency limit"
    elif waveform is WaveformShape.NOIS:
        max_hz = _select_max_frequency(profile.noise, amplitude_vpp)
        note = "33622A noise frequency limit"
    elif waveform is WaveformShape.PRBS:
        max_hz = _select_max_frequency(profile.prbs, amplitude_vpp)
        note = "33622A PRBS frequency limit"
    elif waveform is WaveformShape.ARB:
        max_hz = profile.arb
        note = "33622A arbitrary sample rate limit"
    else:
        return

    if max_hz > 0 and frequency_hz > max_hz:
        raise ValidationError33600A(
            f"Frequency for {waveform.value} must be <= {max_hz:g} Hz ({note})"
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