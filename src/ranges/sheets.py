import math
import re

from decimal import Decimal, InvalidOperation
from typing import Union

from src.ranges.units import DistanceUnit, WeightUnit


class CellParser:
    def __init__(self):
        raise NotImplementedError

    def parse(self, raw_value: str) -> any:
        raise NotImplementedError

    def validate(self, raw_value: str) -> bool:
        raise NotImplementedError


class SheetParser:
    expected_columns = [
        {
            "column_name": "guid",
            "valid_names": ["MVZ #", "MVZ#", "catalognumberint", "mvz", "mvz_num"],
            "optional": False,
        },
        {
            "column_name": "collector",
            "valid_names": ["collector", "collectors", "COLLECTORS"],
            "optional": True,
        },
        {
            "column_name": "scientific_name",
            "valid_names": ["scientific_name", "subspecies"],
            "optional": False,
        },
        {
            "column_name": "date",
            "valid_names": ["date"],
            "optional": True,
        },
        {
            "column_name": "total_length",
            "valid_names": ["total", "total_length", "total length"],
            "optional": False,
        },
        {
            "column_name": "tail_length",
            "valid_names": ["tail", "tail_length", "tail length"],
            "optional": False,
        },
        {
            "column_name": "hind_foot_with_claw",
            "valid_names": ["hf", "hind_foot_with_claw", "hind foot with claw"],
            "optional": False,
        },
        {
            "column_name": "ear",
            "valid_names": ["ear"],
            "optional": True,
        },
        {
            "column_name": "ear_from_notch",
            "valid_names": ["Notch", "ear_from_notch"],
            "optional": True,
        },
        {
            "column_name": "ear_from_crown",
            "valid_names": ["Crown", "ear_from_crown"],
            "optional": True,
        },
        {
            "column_name": "distance_unit",
            "valid_names": ["unit", "distance_units", "length_units"],
            "optional": False,
        },
        {
            "column_name": "weight",
            "valid_names": ["wt", "weight"],
            "optional": False,
        },
        {
            "column_name": "weight_unit",
            "valid_names": ["units", "weight_unit", "weight_units"],
            "optional": False,
        },
        {
            "column_name": "reproductive_data",
            "valid_names": ["repro comments", "reproductive data", "reproductive_data"],
            "optional": False,
        },
        {
            "column_name": "testes_length",
            "valid_names": ["testes L", "testis L"],
            "optional": True,
        },
        {
            "column_name": "testes_width",
            "valid_names": ["testes W", "testes R", "testis W", "testis R"],
            "optional": True,
        },
        {
            "column_name": "embryo_count",
            "valid_names": ["emb count"],
            "optional": True,
        },
        {
            "column_name": "embryo_count_left",
            "valid_names": ["embs L"],
            "optional": True,
        },
        {
            "column_name": "embryo_count_right",
            "valid_names": ["embs R"],
            "optional": True,
        },
        {
            "column_name": "crown_rump_length",
            "valid_names": ["emb CR"],
            "optional": True,
        },
        {
            "column_name": "scars",
            "valid_names": ["scars"],
            "optional": True,
        },
        {
            "column_name": "unformatted_measurements",
            "valid_names": ["unformatted measurements"],
            "optional": True,
        },
        {
            "column_name": "review_needed",
            "valid_names": ["REVIEW NEEDED"],
            "optional": True,
        },
    ]

    def is_recorded(raw_value):
        if raw_value is None:
            return False

        if isinstance(raw_value, float) and math.isnan(raw_value):
            return False

        if isinstance(raw_value, str):
            value_cleaned = raw_value.strip().lower()

            if value_cleaned in [
                "",
                "not recorded",
                "?",
                "no recorded",
                "already in arctos",
                "no measurements",
                "not recoded",
                "no data",
            ]:
                return False

        return True

    def verify_columns_exist(columns):
        missing_columns = []

        for expected_column in SheetParser.expected_columns:
            found = False
            for valid_name in expected_column["valid_names"] + [
                expected_column["column_name"]
            ]:
                if valid_name in columns:
                    found = True

            if not found and not expected_column["optional"]:
                missing_columns.append(expected_column["column_name"])

        return missing_columns

    def extract_record(raw_record):
        record = {}

        found_columns = set()
        for expected_column in SheetParser.expected_columns:
            found = False
            for valid_name in expected_column["valid_names"] + [
                expected_column["column_name"]
            ]:
                if valid_name in raw_record:
                    column = raw_record[valid_name]
                    if isinstance(column, str):
                        column = column.strip()

                    if SheetParser.is_recorded(column):
                        record[expected_column["column_name"]] = str(column)
                    else:
                        record[expected_column["column_name"]] = None

                    found = True
                    break

            if not found:
                if expected_column["optional"]:
                    record[expected_column["column_name"]] = None
                else:
                    raise ValueError(
                        "Could not find field",
                        expected_column["column_name"],
                        raw_record,
                    )
            else:
                found_columns.add(expected_column["column_name"])

        if record["ear_from_notch"] is None:
            record["ear_from_notch"] = record["ear"]

        if record["ear"] is not None and record["ear_from_notch"] != record["ear"]:
            raise ValueError(
                "Ear and Notch column mismatched",
                record["ear"],
                record["ear_from_notch"],
                raw_record,
            )

        if (
            "ear" not in found_columns
            and "ear_from_notch" not in found_columns
            and "ear_from_crown" not in found_columns
        ):
            raise ValueError(
                "Could not find any column for ear measurements", raw_record
            )

        return record

    def parse_guid(guid: str) -> str:
        matched = re.match(r"^(?=.{3,20}:[^:]+$)([A-Za-z]+:[A-Za-z]+):([^:]+)$", guid)

        if not matched:
            raise ValueError("Guid does not match valid Arctos format", guid)

        return matched.group(1), matched.group(2)

    def parse_numerical_attribute(
        raw_value: str,
        unit: Union[DistanceUnit, WeightUnit],
        default: Union[DistanceUnit, WeightUnit],
    ) -> tuple[Decimal, Union[DistanceUnit, WeightUnit], str]:
        if raw_value is None:
            return None, None, None

        if isinstance(default, DistanceUnit):
            value_cleaned, extracted_unit = DistanceUnit.split_value(raw_value)
        elif isinstance(default, WeightUnit):
            value_cleaned, extracted_unit = WeightUnit.split_value(raw_value)
        else:
            raise ValueError("Invalid default value type")

        matched = re.match("(?:([0-9]+) )?([0-9]+)/([1-9][0-9]*)", value_cleaned)

        value = None
        remarks = None
        try:
            if matched:
                remarks = value_cleaned
                value = Decimal(matched.group(1) or 0) + (
                    Decimal(matched.group(2)) / Decimal(matched.group(3))
                ).quantize(Decimal("0.01"), rounding="ROUND_HALF_EVEN")
            else:
                value = Decimal(value_cleaned)
        except InvalidOperation:
            remarks = raw_value

        if extracted_unit is not None and unit is not None and extracted_unit != unit:
            print("Unit Mismatched")

        if extracted_unit is None:
            extracted_unit = unit or default

        return value, extracted_unit, remarks

    def parse_integer_attribute(raw_value: str) -> tuple[int, str]:
        if raw_value is None:
            return None, None

        value = None
        remarks = None
        try:
            value = int(raw_value.strip())
        except ValueError:
            remarks = raw_value

        return value, remarks
