import dataclasses
from decimal import Decimal

from src.ranges.units import DistanceUnit, WeightUnit
from src.ranges import sheets


class ReviewNeededException(Exception):
    pass


@dataclasses.dataclass
class Specimen:
    guid: str
    scientific_name: str
    collectors: str
    collected_date: str

    total_length: tuple[Decimal, DistanceUnit, str]
    tail_length: tuple[Decimal, DistanceUnit, str]
    hind_foot_with_claw: tuple[Decimal, DistanceUnit, str]
    ear_from_notch: tuple[Decimal, DistanceUnit, str]
    ear_from_crown: tuple[Decimal, DistanceUnit, str]
    tragus_length: tuple[Decimal, DistanceUnit, str]
    forearm_length: tuple[Decimal, DistanceUnit, str]
    weight: tuple[Decimal, WeightUnit, str]
    unformatted_measurements: str | None

    life_stage: tuple[sheets.LifeStage, str]
    testes_length: tuple[Decimal, DistanceUnit, str]
    testes_width: tuple[Decimal, DistanceUnit, str]
    embryo_count: tuple[int, str]
    embryo_count_left: tuple[int, str]
    embryo_count_right: tuple[int, str]
    crown_rump_length: tuple[Decimal, DistanceUnit, str]
    scars: str
    repro_comments: str | None

    distance_unit: DistanceUnit
    weight_unit: WeightUnit
    initials: str | None

    def from_raw_record(raw_record):
        record = sheets.extract_record(raw_record)

        if not record["guid"] and not record["mvz_num"]:
            raise ValueError(f"Could not find guid or mvz_num field in {raw_record}")

        guid = (
            ":".join(sheets.parse_guid(record["guid"]))
            if record["guid"]
            else f"MVZ:Mamm:{int(record["mvz_num"])}"
        )
        distance_unit = DistanceUnit.from_string(record["distance_unit"])
        weight_unit = WeightUnit.from_string(record["weight_unit"])

        if record["review_needed"] is not None:
            raise ReviewNeededException(
                "Record has been marked with Review Needed:", record["review_needed"]
            )

        return Specimen(
            guid=guid,
            scientific_name=record["scientific_name"],
            collectors=record["collector"],
            collected_date=record["date"],
            total_length=sheets.parse_numerical_attribute(
                record["total_length"], distance_unit, DistanceUnit.MILLIMETERS
            ),
            tail_length=sheets.parse_numerical_attribute(
                record["tail_length"], distance_unit, DistanceUnit.MILLIMETERS
            ),
            hind_foot_with_claw=sheets.parse_numerical_attribute(
                record["hind_foot_with_claw"],
                distance_unit,
                DistanceUnit.MILLIMETERS,
            ),
            ear_from_notch=sheets.parse_numerical_attribute(
                record["ear_from_notch"], distance_unit, DistanceUnit.MILLIMETERS
            ),
            ear_from_crown=sheets.parse_numerical_attribute(
                record["ear_from_crown"], distance_unit, DistanceUnit.MILLIMETERS
            ),
            tragus_length=sheets.parse_numerical_attribute(
                record["tragus_length"], distance_unit, DistanceUnit.MILLIMETERS
            ),
            forearm_length=sheets.parse_numerical_attribute(
                record["forearm_length"], distance_unit, DistanceUnit.MILLIMETERS
            ),
            weight=sheets.parse_numerical_attribute(
                record["weight"], weight_unit, WeightUnit.GRAMS
            ),
            unformatted_measurements=record["unformatted_measurements"],
            life_stage=sheets.parse_life_stage(record["life_stage"]),
            testes_length=sheets.parse_numerical_attribute(
                record["testes_length"], distance_unit, DistanceUnit.MILLIMETERS
            ),
            testes_width=sheets.parse_numerical_attribute(
                record["testes_width"], distance_unit, DistanceUnit.MILLIMETERS
            ),
            embryo_count=sheets.parse_integer_attribute(record["embryo_count"]),
            embryo_count_left=sheets.parse_integer_attribute(
                record["embryo_count_left"]
            ),
            embryo_count_right=sheets.parse_integer_attribute(
                record["embryo_count_right"]
            ),
            crown_rump_length=sheets.parse_numerical_attribute(
                record["crown_rump_length"], distance_unit, DistanceUnit.MILLIMETERS
            ),
            scars=record["scars"],
            repro_comments=record["reproductive_data"],
            distance_unit=distance_unit,
            weight_unit=weight_unit,
            initials=record["initials"],
        )

    def to_dict(self):
        return {
            "guid": self.guid,
            "scientific_name": self.scientific_name,
            "collectors": self.collectors,
            "collected_date": self.collected_date,
            "total_length": self.total_length[0],
            "tail_length": self.tail_length[0],
            "hind_foot_with_claw": self.hind_foot_with_claw[0],
            "ear_from_notch": self.ear_from_notch[0],
            "ear_from_crown": self.ear_from_crown[0],
            "tragus_length": self.tragus_length[0],
            "forearm_length": self.forearm_length[0],
            "weight": self.weight[0],
            "unformatted_measurements": self.unformatted_measurements,
            "life_stage": self.life_stage[0],
            "testes_length": self.testes_length[0],
            "testes_width": self.testes_width[0],
            "embryo_count": self.embryo_count[0],
            "embryo_count_left": self.embryo_count_left[0],
            "embryo_count_right": self.embryo_count_right[0],
            "crown_rump_length": self.crown_rump_length[0],
            "scars": self.scars,
            "repro_comments": self.repro_comments,
            "distance_unit": (self.distance_unit or DistanceUnit.MILLIMETERS).value,
            "weight_unit": (self.weight_unit or WeightUnit.GRAMS).value,
        }

    def export_attributes(self) -> list:
        attributes = []
        unitless_attributes = []
        unparsed_values = []

        for value, attribute_type in [
            (self.total_length, "total length"),
            (self.tail_length, "tail length"),
            (self.hind_foot_with_claw, "hind foot with claw"),
            (self.ear_from_notch, "ear from notch"),
            (self.ear_from_crown, "ear from crown"),
            (self.tragus_length, "tragus length"),
            (self.forearm_length, "forearm length"),
            (self.weight, "weight"),
            (self.crown_rump_length, "crown-rump length"),
        ]:
            if value[0] is not None:
                attributes.append(
                    {
                        "guid": self.guid,
                        "attribute_type": attribute_type,
                        "attribute_value": str(value[0]),
                        "attribute_units": value[1].value,
                        "attribute_remark": value[2],
                    }
                )

            elif value[2] is not None:
                unparsed_values.append(f'"{attribute_type}": "{value[2]}"')

        if self.unformatted_measurements is not None:
            unparsed_values.append(self.unformatted_measurements)

        if len(unparsed_values) > 0:
            unitless_attributes.append(
                {
                    "guid": self.guid,
                    "attribute_type": "unformatted measurements",
                    "attribute_value": ", ".join(unparsed_values),
                    "attribute_remark": "",
                }
            )

        if self.repro_comments is not None:
            unitless_attributes.append(
                {
                    "guid": self.guid,
                    "attribute_type": "reproductive data",
                    "attribute_value": self.repro_comments,
                    "attribute_remark": "",
                }
            )

        if self.life_stage[0] is not None:
            unitless_attributes.append(
                {
                    "guid": self.guid,
                    "attribute_type": "life stage",
                    "attribute_value": self.life_stage[0].value,
                    "attribute_remark": self.life_stage[1],
                }
            )

        return attributes, unitless_attributes
