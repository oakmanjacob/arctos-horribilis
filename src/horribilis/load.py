from src.horribilis import horribilis, models


def load_ranges_data(
    specimens: list[models.MetricSpecimen], client: horribilis.HorribilisClient
) -> None:
    """Load all of the ranges data into horribilis"""

    client.upload_specimens(specimens)


def load_arctos_data(
    partial_specimens: list[models.PartialSpecimen], client: horribilis.HorribilisClient
) -> None:
    """Supplement existing records with arctos records"""

    client.update_partial_specimens(partial_specimens)
