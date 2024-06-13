import enum


class Priority(enum.Enum):
    """Enum for request priorities. Lower integer is higher priority."""

    ALL_COMBOS = 0
    MODEL_COMBO = 1
    IMAGE = 2
    CASE_FOR_IMAGE = 3
    CASE = 4
    CASE_LIST = 5
