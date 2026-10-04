import json
from pathlib import Path

import tqdm

from src.horribilis import extract, horribilis, load, transform


def main():
    directory_path = Path("./data/horribilis/")
    files = list(directory_path.glob("*.csv"))
    client = horribilis.HorribilisClient()

    for file in files:
        extracted_data = extract.extract_ranges_csv(
            f"./data/horribilis/{file.stem}.csv"
        )
        horribilis_specimens, invalid_records = transform.transform_horribilis(
            tqdm.tqdm(extracted_data)
        )

        load.load_ranges_data(horribilis_specimens, client)

        print(len(horribilis_specimens), len(invalid_records))

        if invalid_records:
            with open(
                f"./data/horribilis/invalid_records/{file.stem} invalid_records.json",
                "w",
                encoding="utf8",
            ) as out_file:
                json.dump(invalid_records, out_file, indent=4, default=str)


if __name__ == "__main__":
    main()
