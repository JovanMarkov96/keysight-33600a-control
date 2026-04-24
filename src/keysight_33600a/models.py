from enum import Enum


class WaveformShape(str, Enum):
    SIN = "SIN"
    SQU = "SQU"
    TRI = "TRI"
    RAMP = "RAMP"
    PULS = "PULS"
    NOIS = "NOIS"
    ARB = "ARB"
    DC = "DC"
    PRBS = "PRBS"


class AmplitudeUnit(str, Enum):
    VPP = "VPP"
    VRMS = "VRMS"
    DBM = "DBM"


class BurstMode(str, Enum):
    TRIG = "TRIG"
    GAT = "GAT"


class TriggerSource(str, Enum):
    IMM = "IMM"
    EXT = "EXT"
    BUS = "BUS"
