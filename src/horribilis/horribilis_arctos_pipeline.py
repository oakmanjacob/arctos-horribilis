import tqdm

from src.horribilis import extract, horribilis, load, transform


def main():
    client = horribilis.HorribilisClient()

    extracted_data = extract.extract_arctos_csv(
        "./data/horribilis/arctos/Arctos-coords.csv"
    )
    partial_specimens = transform.transform_arctos_data(tqdm.tqdm(extracted_data))

    load.load_arctos_data(partial_specimens, client)


if __name__ == "__main__":
    main()
