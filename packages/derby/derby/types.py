from enum import Enum


class WagerDecision(Enum):
    RAISE = "raise"
    CALL = "call"
    CHECK = "check"
    FOLD = "fold"
