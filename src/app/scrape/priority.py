import enum


class Priority(enum.Enum):
    """Enum for request priorities. Lower integer is higher priority."""

    ALL_COMBOS = 0  # For updating all comboboxes (except the model combobox)
    MODEL_COMBO = 1  # For updating the model combobox
    CASE_RAW_SAVE = 2  # For saving individual raw case data
    IMAGE = 3  # For requesting an individual image
    CASE_FOR_IMAGES = 4  # For requesting a case to extract all images
    CASE = 5  # For requesting a case during a scrape
    CASE_LIST = 6  # For requesting a list of cases during a scrape
