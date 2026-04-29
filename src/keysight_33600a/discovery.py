from typing import List

import pyvisa

# Module-level ResourceManager — created once and never explicitly closed.
# Closing a pyvisa ResourceManager on NI-VISA can invalidate sessions opened
# through other RMs in the same process, so we keep this one alive for the
# process lifetime.
_rm: pyvisa.ResourceManager = None


def _get_rm() -> pyvisa.ResourceManager:
    global _rm
    if _rm is None:
        _rm = pyvisa.ResourceManager()
    return _rm


def list_keysight_resources() -> List[str]:
    """Return VISA resource strings that likely belong to Keysight/Agilent instruments."""
    resources = _get_rm().list_resources()
    return [
        r
        for r in resources
        if "0X2A8D" in r.upper()    # Keysight modern USB VID
        or "0X0957" in r.upper()   # Agilent/Keysight legacy USB VID (33600A series)
        or "KEYSIGHT" in r.upper()
        or "AGILENT" in r.upper()
    ]
