import enum


class GroupType(enum.IntEnum):
    PARTICIPANT = 0
    ORGANISER = 1
    SPONSOR = 2
    MEDIA = 3


class DepartmentType(enum.IntEnum):
    ADMIN = 0
    DIRECTOR = 1
    DESIGN = 2
    FINANCE = 3
    FUNDRAISING = 4
    HACKERXPERIENCE = 5
    LOGISTICS = 6
    MARKETING = 7
    PHOTOGRAPHY = 8
    STAFF = 9
    WEBDEV = 10
