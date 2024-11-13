# Filter out specimens in an accession that already have measurements in arctos
import argparse
import glob
import json
accession = 14836

file_name = f"./data/{accession}.xlsx" # path to file + file name
#sheet = "13065" # sheet name or sheet number or list of sheet numbers and names

def get_csv_for_field(accession_data, arctos_data, arctos_data_lookup, arctos_field, accession_field):
    results = []
    arctos_data_search = {}
    for arctos_record in arctos_data:
        arctos_data_search[int(arctos_record["catalognumberint"])] = arctos_record

    for specimen in accession_data:
        # if the specimen does not have data in arctos for this field
        if int(specimen["catalognumberint"]) not in arctos_data_lookup[arctos_field] \
            and specimen[accession_field] != None and specimen[accession_field] != "":
            row= {
                "guid": specimen["guid"],
                "attribute":arctos_field.replace("_", " "),
                "attribute_value": specimen[accession_field]
                }
            
            

            if arctos_field == "weight":
                row["attribute_units"] = "g"
            elif arctos_field in ["total_length", "tail_length", "ear_from_notch", "hind_foot_with_claw"]:
                row["attribute_units"] = "mm"

            row["attribute_date"] = arctos_data_search[int(specimen["catalognumberint"])]["ended_date"]

            # DO NOT FORGET TO REMOVE THIS LATER!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            row["determiner"]= "James L. Patton"
            results.append(row)
        
    return results

def convert_arctos_data(arctos_data, fields):
    arctos_data_lookup = {}

    for field in fields:
        arctos_data_lookup[field] = []

    for record in arctos_data:
        for field in fields:
            if record[field] != None and record[field] != "":
                arctos_data_lookup[field].append(int(record["catalognumberint"]))
    
    return arctos_data_lookup


def main():
    parser = argparse.ArgumentParser(
                    prog='ProgramName',
                    description='What the program does',
                    epilog='Text at the bottom of help')
    
    parser.add_argument('-c', '--config', required=False, default="config.json")
    parser.add_argument('-a', '--arctos_file', required=False, default="arctos_data.csv")
    parser.add_argument('-d', '--data_dir', required=False, default="./data")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf8") as config_file:
        config = json.load(config_file)

    accession_files = glob.glob(args.data_dir, "*.xlsx")
    print(accession_files)
    

    # accession_data = pd.read_excel(io=file_name, dtype=str)
    # accession_data = accession_data.fillna("")
    # accession_data = accession_data.to_dict(orient="records")

    # arctos_data = pd.read_excel(io="./data/ArctosAccessionData.xlsx", sheet_name="ArctosAcc")
    # arctos_data = arctos_data.fillna("")
    # arctos_data = arctos_data.to_dict(orient="records")

    # fields = 



    # arctos_data_lookup = convert_arctos_data(arctos_data, fields.keys())
    # with open("arctos_data_lookup.json", "w") as f:
    #     json.dump(arctos_data_lookup, f)

    # for arctos_field, accession_field in fields.items():
    #     csv_data = get_csv_for_field(accession_data, arctos_data, arctos_data_lookup, arctos_field, accession_field)
    #     csv_dataframe = pd.DataFrame.from_records(csv_data)
    #     csv_dataframe.to_csv(f"./output/{accession}_{arctos_field}.csv", index=False)

main()