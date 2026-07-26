import enum
import re

import typing


class WeightUnit(enum.StrEnum):
    GRAMS = "g"
    KILOGRAMS = "kg"
    OUNCES = "oz"
    POUNDS = "lb"

    GRAMS_ALIAS = enum.nonmember(["g", "gm", "gms", "grams"])
    KILOGRAMS_ALIAS = enum.nonmember(["kg", "kgs", "kilograms"])
    OUNCES_ALIAS = enum.nonmember(["oz", "ounces"])
    POUNDS_ALIAS = enum.nonmember(["lb", "lbs", "pounds"])

    REGEX_ALIAS_MATCH = enum.nonmember(
        re.compile(
            f"^(.+?[0-9|\s])\s*({"|".join(GRAMS_ALIAS + KILOGRAMS_ALIAS + OUNCES_ALIAS + POUNDS_ALIAS)})$"
        )
    )

    @classmethod
    def from_string(cls, value: str) -> typing.Self:
        if value in cls.GRAMS_ALIAS:
            return cls.GRAMS
        elif value in cls.KILOGRAMS_ALIAS:
            return cls.KILOGRAMS
        elif value in cls.OUNCES_ALIAS:
            return cls.OUNCES
        elif value in cls.POUNDS_ALIAS:
            return cls.POUNDS
        elif value is None:
            return None
        else:
            raise ValueError("Could not parse weight unit from value", value)

    @classmethod
    def split_value(cls, value: str) -> tuple[str, typing.Self]:
        if value is None:
            raise ValueError("Cannot split None value")

        matched = re.match(
            cls.REGEX_ALIAS_MATCH,
            value.strip(),
        )

        if matched is None:
            return value.strip(), None

        value_cleaned = matched.group(1).strip()
        extracted_unit = matched.group(2).strip()

        return value_cleaned, (
            cls.from_string(extracted_unit) if extracted_unit is not None else None
        )


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

        return value_cleaned, (
            DistanceUnit.from_string(extracted_unit)
            if extracted_unit is not None
            else None
        )
