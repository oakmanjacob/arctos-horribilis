import csv

COLUMN_RENAME_MAP = {
    "catalognumberint": "mvz_num",
    "mvz #": "mvz_num",
    "mvz#": "mvz_num",
    "mvz": "mvz_num",
    "collectors": "collectors",
    "COLLECTORS": "collectors",
    "date": "collected_date",
    "verbatim_date": "collected_date",
    "verbatim date": "collected_date",
    "collected date": "collected_date",
    "sci name": "scientific_name",
    "scientific name": "scientific_name",
    "subspecies": "scientific_name",
    "spec_locality": "locality",
    "specific locality": "locality",
    "total": "total_length",
    "total length": "total_length",
    "tail": "tail_length",
    "tail length": "tail_length",
    "hf": "hind_foot_with_claw",
    "hind foot with claw": "hind_foot_with_claw",
    "ear": "ear_from_notch",
    "notch": "ear_from_notch",
    "ear from notch": "ear_from_notch",
    "crown": "ear_from_crown",
    "ear from crown": "ear_from_crown",
    "tragus": "tragus_length",
    "tragus length": "tragus_length",
    "forearm": "forearm_length",
    "forearm length": "forearm_length",
    "unit": "distance_unit",
    "distance_units": "distance_unit",
    "length_units": "distance_unit",
    "wt": "weight",
    "units": "weight_unit",
    "weight_units": "weight_unit",
    "life stage": "life_stage",
    "repro comments": "reproductive_data",
    "reproductive data": "reproductive_data",
    "testes l": "testes_length",
    "testis l": "testes_length",
    "testes w": "testes_width",
    "testes r": "testes_width",
    "testis w": "testes_width",
    "testis r": "testes_width",
    "emb count": "embryo_count",
    "embs l": "embryo_count_left",
    "embs r": "embryo_count_right",
    "emb cr": "crown_rump_length",
    "unformatted measurements": "unformatted_measurements",
    "Initials": "initials",
    "tag checked? (or no tag available), initial here": "initials",
    "skin tag checked? (or no skin tag available)": "skin_checked",
    "catalog checked? (or no catalog available)": "catalog_checked",
    "review needed": "review_needed",
}

REQUIRED_COLUMNS = [
    "scientific_name",
    "total_length",
    "tail_length",
    "hind_foot_with_claw",
    "ear_from_notch",
    "ear_from_crown",
    "distance_unit",
    "weight",
    "weight_unit",
    "reproductive_data",
]

EXPORT_COLUMNS = [
    "guid",
    "mvz_num",
    "scientific_name",
    "collectors",
    "collected_date",
    "country",
    "state_prov",
    "county",
    "locality",
    "latitude",
    "longitude",
    "uncertainty",
    "sex",
    "total_length",
    "tail_length",
    "hind_foot_with_claw",
    "ear_from_notch",
    "ear_from_crown",
    "tragus_length",
    "forearm_length",
    "distance_unit",
    "weight",
    "weight_unit",
    "life_stage",
    "reproductive_data",
    "crown_rump_length",
    "testes_length",
    "testes_width",
    "embryo_count",
    "embryo_count_left",
    "embryo_count_right",
    "unformatted_measurements",
    "day",
    "month",
    "year",
    "initials",
    "skin_checked",
    "catalog_checked",
    "review_needed",
]


def extract_ranges_csv(file_path: str) -> list[dict[str, str | None]]:
    with open(file_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        raw_fieldnames = reader.fieldnames or []
        renamed_fieldnames = [
            COLUMN_RENAME_MAP.get(col.lower(), col.lower()) for col in raw_fieldnames
        ]

        missing_columns = []

        if "guid" not in renamed_fieldnames and "mvz_num" not in renamed_fieldnames:
            missing_columns.extend(["guid", "mvz_num"])

        if (
            "skin_checked" not in renamed_fieldnames
            and "catalog_checked" not in renamed_fieldnames
            and "initials" not in renamed_fieldnames
        ):
            missing_columns.extend(["skin_checked", "catalog_checked"])

        missing_columns.extend(
            column for column in REQUIRED_COLUMNS if column not in renamed_fieldnames
        )

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns} in {file_path}"
            )

        export_only_columns = [
            col for col in EXPORT_COLUMNS if col not in renamed_fieldnames
        ]

        rows = []
        for raw_row in reader:
            row = {
                COLUMN_RENAME_MAP.get(k.lower(), k.lower()): v
                for k, v in raw_row.items()
            }
            for column in export_only_columns:
                row[column] = None
            rows.append(row)

        return rows


ARCTOS_REQUIRED_COLUMNS = frozenset(
    {
        "guid",
        "species",
        "subspecies",
        "country",
        "state_prov",
        "county",
        "spec_locality",
        "ended_date",
        "collectors",
        "dec_lat",
        "dec_long",
        "coordinateuncertaintyinmeters",
        "sex",
    }
)


def extract_arctos_csv(file_path: str) -> list[dict[str, str | None]]:
    with open(file_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        raw_fieldnames = reader.fieldnames or []

        missing_columns = []
        missing_columns.extend(
            column for column in ARCTOS_REQUIRED_COLUMNS if column not in raw_fieldnames
        )

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        rows = [raw_row for raw_row in reader]

        return rows
