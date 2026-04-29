from keysight_33600a import SimulatedKeysight33600A, WaveformShape


def test_simulator_connect_identify_and_output_toggle() -> None:
    inst = SimulatedKeysight33600A()
    inst.connect()

    assert inst.is_connected is True
    assert "SIMULATED" in inst.identify()

    inst.set_output(1, True)
    assert inst.get_output(1) is True

    inst.disconnect()
    assert inst.is_connected is False


def test_simulator_applies_waveform_and_parameters() -> None:
    inst = SimulatedKeysight33600A()
    inst.connect()

    inst.set_load(1, 50)
    inst.set_function(1, WaveformShape.SIN)
    inst.set_frequency(1, 1_000)
    inst.set_amplitude(1, 1.0)
    inst.set_offset(1, 0.0)

    assert inst.get_load(1) == 50
    assert inst.get_function(1) == "SIN"
    assert inst.get_frequency(1) == 1_000
    assert inst.get_amplitude(1) == 1.0
    assert inst.get_offset(1) == 0.0


def test_simulator_tracks_modulation_sweep_burst_and_trigger_state() -> None:
    inst = SimulatedKeysight33600A()
    inst.connect()

    inst.set_am_enabled(1, True)
    inst.set_sweep_enabled(1, True)
    inst.set_burst_enabled(1, True)
    inst.set_trigger_source(1, "BUS")
    inst.set_trigger_count(1, 5)
    inst.set_trigger_delay(1, 0.1)
    inst.set_trigger_timer(1, 0.5)

    assert inst.get_am_enabled(1) is True
    assert inst.get_sweep_enabled(1) is True
    assert inst.get_burst_enabled(1) is True
    assert inst.get_trigger_source(1) == "BUS"
    assert inst.get_trigger_count(1) == 5
    assert inst.get_trigger_delay(1) == 0.1
    assert inst.get_trigger_timer(1) == 0.5