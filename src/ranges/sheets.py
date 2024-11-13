import math
import re

from decimal import Decimal, InvalidOperation
from typing import Union

from ranges.units import DistanceUnit, WeightUnit

class SheetParser:
    expected_columns = [
    {
        "column_name": "mvz_num",
        "valid_names": ["MVZ #", "MVZ#", "catalognumberint", "mvz"],
        "type": "whole",
        "optional": False
    },
    {
        "column_name": "collector",
        "valid_names": ["collector", "collectors", "COLLECTORS"],
        "type": "text",
        "optional": True
    },
    {
        "column_name": "scientific_name",
        "valid_names": ["scientific_name", "subspecies"],
        "type": "text",
        "optional": False
    },
    {
        "column_name": "date",
        "valid_names": ["date"],
        "type": "text",
        "optional": True
    },
    {
        "column_name": "total_length",
        "valid_names": ["total", "total_length", "total length"],
        "type": "decimal",
        "optional": False
    },
    {
        "column_name": "tail_length",
        "valid_names": ["tail", "tail_length", "tail length"],
        "type": "decimal",
        "optional": False
    },
    {
        "column_name": "hind_foot_with_claw",
        "valid_names": ["hf", "hind_foot_with_claw", "hind foot with claw"],
        "type": "decimal",
        "optional": False
    },
    {
        "column_name": "ear",
        "valid_names": ["ear"],
        "type": "decimal",
        "optional": True
    },
    {
        "column_name": "ear_from_notch",
        "valid_names": ["Notch"],
        "type": "decimal",
        "optional": True
    },
    {
        "column_name": "ear_from_crown",
        "valid_names": ["Crown"],
        "type": "decimal",
        "optional": True
    },
    {
        "column_name": "distance_unit",
        "valid_names": ["unit"],
        "type": "distance_unit",
        "optional": False
    },
    {
        "column_name": "weight",
        "valid_names": ["wt", "weight"],
        "type": "decimal",
        "optional": False
    },
    {
        "column_name": "weight_unit",
        "valid_names": ["units"],
        "type": "mass_unit",
        "optional": False
    },
    {
        "column_name": "repro_comments",
        "valid_names": ["repro comments", "reproductive data"],
        "type": "text",
        "optional": False
    },
    {
        "column_name": "testes_length",
        "valid_names": ["testes L", "testis L"],
        "type": "decimal",
        "optional": True
    },
    {
        "column_name": "testes_width",
        "valid_names": ["testes W", "testes R", "testis W", "testis R"],
        "type": "decimal",
        "optional": True
    },
    {
        "column_name": "embryo_count",
        "valid_names": ["emb count"],
        "type": "whole",
        "optional": True
    },
    {
        "column_name": "embryo_count_left",
        "valid_names": ["embs L"],
        "type": "whole",
        "optional": True
    },
    {
        "column_name": "embryo_count_right",
        "valid_names": ["embs R"],
        "type": "whole",
        "optional": True
    },
    {
        "column_name": "crown_rump_length",
        "valid_names": ["emb CR"],
        "type": "decimal",
        "optional": True
    },
    {
        "column_name": "scars",
        "valid_names": ["scars"],
        "type": "text",
        "optional": True
    },
    {
        "column_name": "unformatted_measurements",
        "valid_names": ["unformatted measurements"],
        "type": "text",
        "optional": True
    },
    {
        "column_name": "review_needed",
        "valid_names": ["REVIEW NEEDED"],
        "type": "text",
        "optional": True
    }]

    

    def is_recorded(raw_value):
        if raw_value is None:
            return False

        if isinstance(raw_value, float) and math.isnan(raw_value):
            return False

        if isinstance(raw_value, str):
            value_cleaned = raw_value.strip().lower()

            if value_cleaned in ["", "not recorded", "?", "no recorded", "already in arctos",
                                "no measurements", "not recoded", "no data"]:
                return False
        
        return True
    
    def parse_mvz_guid(value: str) -> str:
        if value is None:
            raise ValueError("Cannot parse guid from None value")

        matched = re.match(r"^(?:MVZ)?:?(?:Mamm)?:?([0-9]+)$", value)

        if matched is None:
            raise ValueError("Couldn't parse guid from value", f"'{value}'")

        return f"MVZ:Mamm:{int(matched.group(1))}"

    def verify_columns_exist(columns):
        missing_columns = []

        for expected_column in SheetParser.expected_columns:
            found = False
            for valid_name in expected_column["valid_names"]:
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
            for valid_name in expected_column["valid_names"]:
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
                    raise ValueError("Could not find field", expected_column["column_name"], raw_record)
            else:
                found_columns.add(expected_column["column_name"])
        
        if record["ear_from_notch"] is None:
            record["ear_from_notch"] = record["ear"]

        if record["ear"] is not None and record["ear_from_notch"] != record["ear"]:
            raise ValueError("Ear and Notch column mismatched", record["ear"], record["ear_from_notch"], raw_record)
        
        if "ear" not in found_columns and "ear_from_notch" not in found_columns and "ear_from_crown" not in found_columns:
            raise ValueError("Could not find any column for ear measurements", raw_record)
            
        return record

    
    def parse_numerical_attribute(raw_value: str,
                                  unit: Union[DistanceUnit, WeightUnit],
                                  default: Union[DistanceUnit, WeightUnit]) -> \
                                    tuple[Decimal, Union[DistanceUnit, WeightUnit], str]:
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
                value = Decimal(matched.group(1) or 0) + \
                    (Decimal(matched.group(2)) / Decimal(matched.group(3))).quantize(Decimal('0.01'), rounding="ROUND_HALF_EVEN")
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