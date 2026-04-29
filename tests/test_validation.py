import pytest

from keysight_33600a import WaveformShape
from keysight_33600a.errors import ValidationError33600A
from keysight_33600a.validation import (
    normalize_load,
    validate_count,
    validate_frequency,
    validate_sweep_shape,
    validate_voltage_settings,
)


def test_normalize_load_accepts_finite_and_infinite_values() -> None:
    assert normalize_load(50) == 50.0
    assert normalize_load("INF") == "INF"


def test_validate_frequency_uses_manual_limits() -> None:
    validate_frequency(WaveformShape.SIN, 60_000_000)
    with pytest.raises(ValidationError33600A):
        validate_frequency(WaveformShape.SIN, 60_000_001)


def test_validate_voltage_settings_respects_termination_and_offset_relation() -> None:
    validate_voltage_settings(5.0, 0.0, 50)
    with pytest.raises(ValidationError33600A):
        validate_voltage_settings(10.5, 0.0, 50)
    with pytest.raises(ValidationError33600A):
        validate_voltage_settings(5.0, 4.0, 50)


def test_validate_sweep_shape_rejects_noise_and_dc() -> None:
    with pytest.raises(ValidationError33600A):
        validate_sweep_shape(WaveformShape.NOIS)
    with pytest.raises(ValidationError33600A):
        validate_sweep_shape(WaveformShape.DC)


def test_validate_count_accepts_positive_values() -> None:
    validate_count("Burst cycles", 1)
    with pytest.raises(ValidationError33600A):
        validate_count("Burst cycles", 0)