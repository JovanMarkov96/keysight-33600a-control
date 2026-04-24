from typing import List

import pyvisa


def list_keysight_resources() -> List[str]:
    """Return VISA resource strings that likely belong to Keysight/Agilent instruments."""
    rm = pyvisa.ResourceManager()
    try:
        resources = rm.list_resources()
    finally:
        rm.close()

    return [
        r
        for r in resources
        if "0x2A8D" in r.upper() or "KEYSIGHT" in r.upper() or "AGILENT" in r.upper()
    ]
