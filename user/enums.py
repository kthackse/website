import enum


class UserType(enum.IntEnum):
    PARTICIPANT = 0
    ORGANISER = 1
    VOLUNTEER = 2
    MENTOR = 3
    SPONSOR = 4
    RECRUITER = 5
    MEDIA = 6


class DepartmentType(enum.IntEnum):
    ADMIN = 0
    DIRECTOR = 1
    DESIGN = 2
    FINANCE = 3
    SPONSORSHIP = 4
    HACKERXPERIENCE = 5
    LOGISTICS = 6
    MARKETING = 7
    PHOTOGRAPHY = 8
    STAFF = 9
    WEBDEV = 10


class SexType(enum.IntEnum):
    NONE = 0
    FEMALE = 1
    MALE = 2


class DocumentType(enum.IntEnum):
    ID = 0
    PASSPORT = 1
