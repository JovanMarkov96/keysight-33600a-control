from keysight_33600a import Keysight33600A


def main() -> None:
    resource = "USB0::0x2A8D::0x0001::MYXXXXXXXX::INSTR"

    with Keysight33600A(resource) as gen:
        gen.clear_status()

        gen.set_function(1, "SQU")
        gen.set_frequency(1, 10000.0)
        gen.set_amplitude(1, 2.0)
        gen.set_burst_enabled(1, True)
        gen.set_burst_mode(1, "TRIG")
        gen.set_burst_ncycles(1, 5)
        gen.set_trigger_source(1, "BUS")
        gen.trigger()


if __name__ == "__main__":
    main()
