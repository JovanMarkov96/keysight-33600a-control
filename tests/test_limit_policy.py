from pathlib import Path


def test_code_does_not_write_limit_setting_scpi_commands() -> None:
    instrument_source = Path(__file__).resolve().parents[1] / "src" / "keysight_33600a" / "instrument.py"
    text = instrument_source.read_text(encoding="utf-8")

    assert "VOLT:LIM" not in text
    assert "FREQ:LIM" not in text
    assert "SWE:LIM" not in text
    assert "BURS:LIM" not in text


def test_validation_module_is_validation_only() -> None:
    validation_source = Path(__file__).resolve().parents[1] / "src" / "keysight_33600a" / "validation.py"
    text = validation_source.read_text(encoding="utf-8")

    assert "write(" not in text
