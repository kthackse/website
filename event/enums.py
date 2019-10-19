import enum


class EventType(enum.IntEnum):
    HACKATHON = 0
    OTHER = 1


class EventApplicationStatus(enum.IntEnum):
    PENDING = 0
    OPEN = 1
    CLOSED = 2


class ApplicationStatus(enum.IntEnum):
    DRAFT = 0
    PENDING = 1
    CANCELLED = 2
    INVITED = 3
    CONFIRMED = 4
    REJECTED = 5
    REMINDED = 6
    EXPIRED = 7
    DUBIOUS = 8
    ATTENDED = 9


class DietType(enum.IntEnum):
    REGULAR = 0
    VEGETARIAN = 1
    VEGAN = 2
    PORK_FREE = 3
    GLUTEN_FREE = 4
    LACTOSE_FREE = 5
    SEAFOOD_FREE = 6
    OTHER = 7


class TshirtSize(enum.IntEnum):
    XXS = 10
    XS = 20
    S = 30
    M = 40
    L = 50
    XL = 60
    XXL = 70
    XXXL = 80


class ReimbursementType(enum.IntEnum):
    PAYPAL = 0
    BANK_TRANSFER = 1
    SWISH = 2


class ReimbursementStatus(enum.IntEnum):
    DRAFT = 0
    PENDING_DRAFT = 1
    PENDING_TICKET = 2
    PENDING_APPROVAL = 3
    APPROVED = 4
    DENIED = 5
    EXPIRED = 6
    WAILISTED = 7


class SubscriberStatus(enum.IntEnum):
    PENDING = 0
    SUBSCRIBED = 1
    UNSUBSCRIBED = 2


class CompanyTier(enum.IntEnum):
    TERA = 10
    GIGA = 20
    MEGA = 30
    KILO = 40
    MILI = 50
    PARTNER = 60
    SUPPORT = 70
    ORGANISER = 80


class InvoiceStatus(enum.IntEnum):
    DRAFT = 0
    SENT = 1


class MessageType(enum.IntEnum):
    GENERIC = 10
    SUBSCRIBED = 20
    ACCEPTED = 30
    LETTER = 40
    INVOICE = 50
    BILL = 60
    VOLUNTEERS = 70
    MENTORS = 80
    SPONSORS = 90


class LetterType(enum.IntEnum):
    VISA = 0
    UNDERAGE = 1


class LetterStatus(enum.IntEnum):
    DRAFT = 0
    SIGNED = 1
    SENT = 2
    CANCELLED = 3
