import dataclasses
import datetime
import decimal
import enum
import sqlite3
from collections.abc import Iterable

from src.horribilis import models


def normalize_value(value):
    if value is None:
        return None
    if isinstance(value, decimal.Decimal):
        return float(
            value.quantize(decimal.Decimal("0.01"), rounding="ROUND_HALF_EVEN")
        )
    if isinstance(value, enum.Enum):
        return value.value
    if isinstance(value, datetime.date):
        return value.isoformat()
    return value


def specimen_to_dict(specimen: models.MetricSpecimen) -> dict:
    data = dataclasses.asdict(specimen)
    return {k: normalize_value(v) for k, v in data.items()}


def partial_specimen_to_dict(specimen: models.PartialSpecimen) -> dict:
    data = dataclasses.asdict(specimen)
    return {k: normalize_value(v) for k, v in data.items()}


class HorribilisClient:
    def __init__(self, connection: sqlite3.Connection | None = None) -> None:
        self.connection = connection or sqlite3.connect("./data/horribilis.db")

    def init_database(self, schema: str | None = None):
        cursor = self.connection.cursor()

        if not schema:
            with open("./src/schema.sql", "r", encoding="utf8") as schema_file:
                schema = schema_file.read()

        cursor.executescript(schema)

    def upload_specimens(self, specimens: Iterable[models.MetricSpecimen]) -> None:
        cursor = self.connection.cursor()
        cursor.executemany(
            (
                "INSERT INTO specimens VALUES ("
                " :guid,"
                " :scientific_name,"
                " :collectors,"
                " :collected_date,"
                " :country,"
                " :state_prov,"
                " :county,"
                " :spec_locality,"
                " :dec_lat,"
                " :dec_long,"
                " :coordinate_uncertainty,"
                " :sex,"
                " :total_length,"
                " :tail_length,"
                " :hind_foot_with_claw,"
                " :ear_from_notch,"
                " :ear_from_crown,"
                " :tragus_length,"
                " :forearm_length,"
                " :weight,"
                " :life_stage,"
                " :testes_length,"
                " :testes_width,"
                " :embryo_count,"
                " :embryo_count_left,"
                " :embryo_count_right,"
                " :crown_rump_length,"
                " :scars,"
                " :unformatted_measurements,"
                " :reproductive_data,"
                " :source,"
                " :ranges_date,"
                " :initials"
                ") ON CONFLICT(guid) DO NOTHING"
            ),
            [specimen_to_dict(s) for s in specimens],
        )
        self.connection.commit()

    def update_partial_specimens(
        self, partial_specimens: Iterable[models.PartialSpecimen]
    ) -> None:
        cursor = self.connection.cursor()
        cursor.executemany(
            (
                "UPDATE specimens SET"
                " scientific_name = :scientific_name,"
                " collectors = :collectors,"
                " collected_date = :collected_date,"
                " country = :country,"
                " state_prov = :state_prov,"
                " county = :county,"
                " spec_locality = :spec_locality,"
                " dec_lat = :dec_lat,"
                " dec_long = :dec_long,"
                " coordinate_uncertainty = :coordinate_uncertainty,"
                " sex = :sex"
                " WHERE guid = :guid"
            ),
            [partial_specimen_to_dict(s) for s in partial_specimens],
        )
        self.connection.commit()


if __name__ == "__main__":
    client = HorribilisClient()
    client.init_database()
