from enum import Enum


class PricingModel(str, Enum):
    PERCENTAGE = "Percentage"
    HOURLY = "Hourly"
    FTE = "Dedicated FTE"