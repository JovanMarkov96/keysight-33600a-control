from __future__ import annotations

import argparse

from keysight_33600a.gui_app import Keysight33600AFrontPanel


def main() -> None:
    parser = argparse.ArgumentParser(description="Keysight 33600A GUI smoke test")
    parser.add_argument("--resource", default="", help="VISA resource string for live hardware")
    parser.add_argument("--simulate", action="store_true", help="Use the built-in simulator backend")
    args = parser.parse_args()

    app = Keysight33600AFrontPanel(simulate=args.simulate or not args.resource)
    try:
        if args.resource:
            app.resource_var.set(args.resource)
        else:
            app.resource_var.set("SIM::KEYSIGHT33600A")

        app._connect()
        print(app.idn_var.get())
        app._disconnect()
    finally:
        app.destroy()

    print("GUI_SMOKE_OK")


if __name__ == "__main__":
    main()