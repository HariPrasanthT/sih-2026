"""
Common schema types and Enums.
"""
from enum import Enum


class VesselClassEnum(str, Enum):
    HANDYSIZE = "Handysize"
    SUPRAMAX = "Supramax"
    PANAMAX = "Panamax"
    CAPESIZE = "Capesize"


class CharterDecisionEnum(str, Enum):
    CHARTER = "CHARTER"
    WAIT = "WAIT"
    AVOID = "AVOID"


class MarketRegimeEnum(str, Enum):
    LOW_VOLATILITY = "LOW_VOLATILITY"
    NORMAL = "NORMAL"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
