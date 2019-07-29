import enum


class PageContentType(enum.IntEnum):
    PLAIN = 0
    HTML = 1
    MARKDOWN = 2


class PageSourceType(enum.IntEnum):
    INTERNAL = 0
    URL = 1
