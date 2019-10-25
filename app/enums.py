import enum


class MailTag(enum.Enum):
    SUBSCRIBE = "subscribe"
    VERIFY = "verify"
    INVOICE = "invoice"
    LETTER = "letter"


class FileType(enum.IntEnum):
    INVOICE = 0
    LETTER = 1


class FileStatus(enum.IntEnum):
    VALID = 0
    DEPRECATED = 1
    INVALID = 2


class FileSubmissionStatus(enum.IntEnum):
    VALID = 0
    SUSPECTED = 1
    INVALID = 2


class FileVerificationStatus(enum.IntEnum):
    SUCCESS = 0
    FAILED = 1
