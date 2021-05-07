from enum import Enum

class SignalStatuses(Enum):
    DUMPED = -2
    DONE = +1
    FAILED = -1
    PENDING = 0

