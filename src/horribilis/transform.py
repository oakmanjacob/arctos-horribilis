import datetime
import re
from collections.abc import Iterable
from decimal import Decimal

import pint
from dateutil import parser

from src.horribilis import models

UNIT_REGISTRY = pint.UnitRegistry(non_int_type=Decimal)
GUID_PATTERN = re.compile(r"(?=.{3,20}:[^:]+$)([A-Za-z]+:[A-Za-z]+):([^:]+)")


def parse_guid(raw_value: str) -> str:
    matched = GUID_PATTERN.fullmatch(raw_value)

    if not matched:
        raise ValueError("Guid does not match valid Arctos format", raw_value)

    return matched.group(1), matched.group(2)


def try_parse_date_or_none(raw_value: str | None) -> datetime.date | None:
    if not raw_value:
        return None

    try:
        return parser.parse(raw_value).date()
    except:
        return None


RESOURCE_CHECKED_PATTERN = re.compile(
    r"(?P<initials>[A-Z]{2,3}) (?P<date>[^,]*?[0-9]{4})"
)


def parse_resource_checked_or_none(raw_value: str | None) -> tuple[str, datetime.date]:
    if not raw_value:
        return None, None

    matched_iter = RESOURCE_CHECKED_PATTERN.finditer(raw_value)

    result = (None, None)
    for matched in matched_iter:
        date = parser.parse(matched.group("date")).date()

        if not result[1] or result[1] < date:
            result = (matched.group("initials"), date)

    return result


NUMERICAL_ATTRIBUTE_PATTERN = re.compile(
    r"(?:(?:(?:(?P<whole>[1-9][0-9]*) )?(?P<numerator>[1-9][0-9]*)/(?P<denominator>[1-9][0-9]*))|(?P<decimal>[0-9]+(?:\.[0-9]+)?))(?P<suffix>[^0-9\+\-\?]*)"
)


def parse_measurement(
    raw_value: str,
    default_unit: pint.Unit,
    unit_registry: pint.UnitRegistry = UNIT_REGISTRY,
) -> pint.Quantity:
    matched = NUMERICAL_ATTRIBUTE_PATTERN.fullmatch(raw_value)

    if not matched:
        raise ValueError("Could not parse magnitude from raw_value", raw_value)

    if matched.group("decimal"):
        magnitude = Decimal(matched.group("decimal"))
    else:
        magnitude = Decimal(matched.group("whole") or 0) + (
            Decimal(matched.group("numerator")) / Decimal(matched.group("denominator"))
        )

    try:
        unit = (
            unit_registry.Unit(matched.group("suffix"))
            if matched.group("suffix")
            else default_unit
        )
    except AssertionError as e:
        print(raw_value, matched.group("suffix"))
        raise ValueError("Failed to parse unit sufix") from e
    return unit_registry.Quantity(magnitude, unit)


def parse_measurement_or_none(
    raw_value: str | None,
    default_unit: pint.Unit,
    to_unit: pint.Unit,
    unit_registry: pint.UnitRegistry = UNIT_REGISTRY,
) -> Decimal | None:
    if not raw_value:
        return None

    return (
        parse_measurement(raw_value, default_unit, unit_registry).to(to_unit).magnitude
    )


# 5 lbs 10 oz
POUNDS_OUNCE_PATTERN = re.compile(r"(?P<pounds>[0-9]+) ?lbs? (?P<ounces>[0-9]+) ?oz")


def parse_weight_or_none(
    raw_value: str | None,
    default_unit: pint.Unit,
    to_unit: pint.Unit,
    unit_registry: pint.UnitRegistry = UNIT_REGISTRY,
) -> Decimal | None:
    if not raw_value:
        return None

    matched = POUNDS_OUNCE_PATTERN.fullmatch(raw_value)
    if matched:
        return (
            (
                unit_registry.Quantity(
                    int(matched.group("pounds")), unit_registry.pounds
                )
                + unit_registry.Quantity(
                    int(matched.group("ounces")), unit_registry.ounces
                )
            )
            .to(to_unit)
            .magnitude
        )

    return (
        parse_measurement(raw_value, default_unit, unit_registry).to(to_unit).magnitude
    )


def parse_lifestage_or_none(raw_value: str | None) -> models.LifeStage | None:
    if not raw_value:
        return None

    return models.LifeStage.from_string(raw_value)


def parse_int_or_none(raw_value: str) -> int | None:
    if not raw_value:
        return None

    return int(raw_value.strip())


def parse_sex_or_none(raw_value: str) -> models.Sex | None:
    if not raw_value:
        return None

    if raw_value[-1] == "?":
        return models.Sex.UNKNOWN

    if raw_value == "hermaphrodite":
        return models.Sex.UNKNOWN

    return models.Sex(raw_value.strip().lower())


NULL_SENTINELS = frozenset(
    {
        "",
        "not recorded",
        "?",
        "no recorded",
        "already in arctos",
        "no measurements",
        "not recoded",
        "no data",
        "null.",
        "select",
        "na",
    }
)


def clean_raw_value(raw_value: str | None) -> str | None:
    if raw_value is None:
        return None

    value = raw_value.strip()
    if value.lower() in NULL_SENTINELS:
        return None
    return value


def transform_horribilis(
    ranges_sheet: Iterable[dict[str, str | None]],
) -> tuple[list[models.MetricSpecimen], list[dict[str, str | None]]]:

    records = []
    invalid_records = []
    for record in ranges_sheet:
        try:
            record = {key: clean_raw_value(value) for key, value in record.items()}

            if not record["guid"] and not record["mvz_num"]:
                raise ValueError("Could not find guid or mvz_num field")

            distance_unit = UNIT_REGISTRY.Unit(
                record["distance_unit"] or UNIT_REGISTRY.millimeters
            )
            weight_unit = UNIT_REGISTRY.Unit(
                record["weight_unit"] or UNIT_REGISTRY.grams
            )

            if record["review_needed"] is not None:
                raise ValueError(
                    "Record has been marked with Review Needed:",
                    record["review_needed"],
                )

            if record["year"] and record["month"]:
                try:
                    month = int(record["month"])
                except:
                    month = parser.parse(record["month"]).month
                ranges_date = datetime.date(
                    year=int(record["year"]),
                    month=month,
                    day=int(record["day"]) if record["day"] else 1,
                )
            else:
                ranges_date = None

            if record["initials"] == "no skin":
                record["initials"] = None

            if record["skin_checked"] == "no skin":
                record["skin_checked"] = None

            if record["initials"] is None and (
                record["skin_checked"] or record["catalog_checked"]
            ):
                record["initials"], ranges_date = parse_resource_checked_or_none(
                    record["skin_checked"] or record["catalog_checked"]
                )

                record["initials"] = (
                    record["initials"]
                    or record["skin_checked"]
                    or record["catalog_checked"]
                )

            records.append(
                models.MetricSpecimen(
                    guid=(
                        ":".join(parse_guid(record["guid"]))
                        if record["guid"]
                        else f"MVZ:Mamm:{int(record['mvz_num'])}"
                    ),
                    scientific_name=record["scientific_name"],
                    collectors=record["collectors"],
                    collected_date=try_parse_date_or_none(record["collected_date"]),
                    country=record["country"],
                    state_prov=record["state_prov"],
                    county=record["county"],
                    spec_locality=record["locality"],
                    dec_lat=record["latitude"],
                    dec_long=record["longitude"],
                    coordinate_uncertainty=record["uncertainty"],
                    sex=parse_sex_or_none(record["sex"]),
                    total_length=parse_measurement_or_none(
                        record["total_length"],
                        distance_unit,
                        UNIT_REGISTRY.millimeters,
                    ),
                    tail_length=parse_measurement_or_none(
                        record["tail_length"],
                        distance_unit,
                        UNIT_REGISTRY.millimeters,
                    ),
                    hind_foot_with_claw=parse_measurement_or_none(
                        record["hind_foot_with_claw"],
                        distance_unit,
                        UNIT_REGISTRY.millimeters,
                    ),
                    ear_from_notch=parse_measurement_or_none(
                        record["ear_from_notch"],
                        distance_unit,
                        UNIT_REGISTRY.millimeters,
                    ),
                    ear_from_crown=parse_measurement_or_none(
                        record["ear_from_crown"],
                        distance_unit,
                        UNIT_REGISTRY.millimeters,
                    ),
                    tragus_length=parse_measurement_or_none(
                        record["tragus_length"],
                        distance_unit,
                        UNIT_REGISTRY.millimeters,
                    ),
                    forearm_length=parse_measurement_or_none(
                        record["forearm_length"],
                        distance_unit,
                        UNIT_REGISTRY.millimeters,
                    ),
                    weight=parse_weight_or_none(
                        record["weight"], weight_unit, UNIT_REGISTRY.grams
                    ),
                    unformatted_measurements=record["unformatted_measurements"],
                    life_stage=parse_lifestage_or_none(record["life_stage"]),
                    testes_length=parse_measurement_or_none(
                        record["testes_length"],
                        distance_unit,
                        UNIT_REGISTRY.millimeters,
                    ),
                    testes_width=parse_measurement_or_none(
                        record["testes_width"],
                        distance_unit,
                        UNIT_REGISTRY.millimeters,
                    ),
                    embryo_count=parse_int_or_none(record["embryo_count"]),
                    embryo_count_left=parse_int_or_none(record["embryo_count_left"]),
                    embryo_count_right=parse_int_or_none(record["embryo_count_right"]),
                    crown_rump_length=parse_measurement_or_none(
                        record["crown_rump_length"],
                        distance_unit,
                        UNIT_REGISTRY.millimeters,
                    ),
                    scars=record["scars"],
                    reproductive_data=record["reproductive_data"],
                    source=(
                        models.DataSource.RANGES
                        if record["initials"]
                        else models.DataSource.ARCTOS
                    ),
                    ranges_date=ranges_date,
                    initials=record["initials"],
                )
            )
        except (
            ValueError,
            pint.UndefinedUnitError,
            pint.DimensionalityError,
            AssertionError,
        ) as e:
            invalid_records.append((record, e))

    return records, invalid_records


def transform_arctos_data(
    arctos_sheet: Iterable[dict[str, str | None]],
) -> list[models.PartialSpecimen]:

    results = []
    for raw_record in arctos_sheet:
        record = {key: value.strip() or None for key, value in raw_record.items()}

        results.append(
            models.PartialSpecimen(
                guid=record["guid"],
                scientific_name=record["subspecies"] or record["species"],
                collectors=record["collectors"],
                collected_date=try_parse_date_or_none(record["ended_date"]),
                country=record["country"],
                state_prov=record["state_prov"],
                county=record["county"],
                spec_locality=record["spec_locality"],
                dec_lat=float(record["dec_lat"]) if record["dec_lat"] else None,
                dec_long=float(record["dec_long"]) if record["dec_long"] else None,
                coordinate_uncertainty=(
                    int(record["coordinateuncertaintyinmeters"])
                    if record["coordinateuncertaintyinmeters"]
                    else None
                ),
                sex=parse_sex_or_none(record["sex"]),
            )
        )
    return results
