import enum


class MailTag(enum.Enum):
    SUBSCRIBE = "subscribe"
    VERIFY = "verify"
    INVOICE = "invoice"
