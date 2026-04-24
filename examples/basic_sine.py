from keysight_33600a import Keysight33600A


def main() -> None:
    # Replace with your actual VISA resource name
    resource = "USB0::0x2A8D::0x0001::MYXXXXXXXX::INSTR"

    with Keysight33600A(resource) as gen:
        print(gen.identify())
        gen.clear_status()

        gen.set_function(1, "SIN")
        gen.set_frequency(1, 1000.0)
        gen.set_amplitude(1, 1.0)
        gen.set_offset(1, 0.0)
        gen.set_output(1, True)


if __name__ == "__main__":
    main()
