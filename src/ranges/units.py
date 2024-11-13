import enum
import re

class WeightUnit(enum.Enum):
    GRAMS = "g"
    OUNCES = "oz"

    def from_string(value: str):
        if value in ["g", "grams"]:
            return WeightUnit.GRAMS
        elif value in ["oz", "ounces"]:
            return WeightUnit.OUNCES
        elif value is None:
            return None
        else:
            raise ValueError("Could not parse weight unit from value", value)
        
    @staticmethod
    def split_value(value: str):
        if value is None:
            raise ValueError("Cannot split None value")

        matched = re.match(r"^(.+?[0-9|\s])\s*(g|grams|oz|ounces)$", value.strip())

        if matched is None:
            return value.strip(), None
        
        value_cleaned = matched.group(1).strip()
        extracted_unit = matched.group(2).strip()

        return value_cleaned, WeightUnit.from_string(extracted_unit) if extracted_unit is not None else None

class DistanceUnit(enum.Enum):
    INCHES = "in"
    MILLIMETERS = "mm"
    CENTIMETERS = "cm"

    @staticmethod
    def from_string(value: str):
        if value == "in" or value == "in." or value == "inches" or value == "inch":
            return DistanceUnit.INCHES
        elif value == "mm":
            return DistanceUnit.MILLIMETERS
        elif value == "cm":
            return DistanceUnit.CENTIMETERS
        elif value is None:
            return None
        else:
            raise ValueError("Could not parse distance unit from value", value)
        
    @staticmethod
    def split_value(value: str):
        if value is None:
            raise ValueError("Cannot split None value")
        
        matched = re.match(r"^(.+?[0-9|\s])\s*(mm|in|in\.|inches)$", value.strip())

        if matched is None:
            return value.strip(), None
        
        value_cleaned = matched.group(1).strip()
        extracted_unit = matched.group(2).strip()

        return value_cleaned, DistanceUnit.from_string(extracted_unit) if extracted_unit is not None else None