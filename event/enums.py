import enum


class EventType(enum.IntEnum):
    HACKATHON = 0


class EventApplicationStatus(enum.IntEnum):
    PENDING = 0
    OPEN = 1
    CLOSED = 2
