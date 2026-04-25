from keysight_33600a import (
    AmplitudeUnit,
    BurstMode,
    Keysight33600A,
    ModulationSource,
    SweepSpacing,
    TriggerSlope,
    TriggerSource,
    WaveformShape,
)


def test_enums_expose_expected_values() -> None:
    assert WaveformShape.SIN.value == "SIN"
    assert AmplitudeUnit.VPP.value == "VPP"
    assert BurstMode.TRIG.value == "TRIG"
    assert TriggerSource.BUS.value == "BUS"
    assert TriggerSource.TIM.value == "TIM"
    assert TriggerSlope.POS.value == "POS"
    assert SweepSpacing.LOG.value == "LOG"
    assert ModulationSource.INT.value == "INT"


def test_validate_channel_accepts_1_and_2() -> None:
    assert Keysight33600A._validate_channel(1) == 1
    assert Keysight33600A._validate_channel(2) == 2


def test_parse_error_entry_no_error() -> None:
    entry = Keysight33600A._parse_error_entry('0,"No error"')
    assert entry.code == 0
    assert "No error" in entry.message


def test_validate_state_slot_accepts_0_to_4() -> None:
    for slot in (0, 1, 2, 3, 4):
        Keysight33600A._validate_state_slot(slot)


def test_validate_register_mask_accepts_8bit_range() -> None:
    Keysight33600A._validate_register_mask(0)
    Keysight33600A._validate_register_mask(255)
