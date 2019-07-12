import enum


class OfferStatus(enum.IntEnum):
    DRAFT = 0
    PENDING_DRAFT = 1
    PUBLISHED = 2
    ARCHIVED = 3
    REMOVED = 4


class ApplicationStatus(enum.IntEnum):
    PENDING = 0
    PENDING_ANSWER = 1
    ACCEPTED = 2
    REJECTED = 3
