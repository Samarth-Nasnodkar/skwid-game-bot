from enum import Enum


class JoinOptions(Enum):
    NO_ERROR = 0
    ENDED_BY_HOST = 1
    UNKNOWN_EXCEPTION = 3
