import enum


class Priority(enum.Enum):
    """Enum for request priorities. Lower integer is higher priority."""

    IMMEDIATE = 0  # For requests that need to be handled immediately
    IMAGE = 1  # For requesting an individual image
    CASE = 2  # For requesting a case during a scrape
    CASE_LIST = 3  # For requesting a list of cases during a scrape
