import enum


class StatusType(enum.IntEnum):
    PENDING = 0
    CANCELLED = 1
    INVITED = 2
    CONFIRMED = 3
    REJECTED = 4
    REMINDED = 5
    EXPIRED = 6
    DUBIOUS = 7


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
