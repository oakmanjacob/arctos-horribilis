import sys
import os
import csv
import io

import pandas as pd
import streamlit as st

project_path = os.path.abspath(os.path.dirname(__file__))
if project_path not in sys.path:
    sys.path.insert(0, project_path)

st.set_page_config(page_title="Ranges Tools for Arctos", layout="wide")

MAPPING = {
    "mvz_num": "MVZ_NUM",
    "guid": "GUID",
    "subspecies": "SUBSPECIES",
    "collectors": "COLLECTORS",
    "country": "COUNTRY",
    "state_prov": "STATE_PROV",
    "county": "COUNTY",
    "spec_locality": "SPEC_LOCALITY",
    "parts": "PARTS",
    "ended_date": "ENDED_DATE",
    "total_length": "TOTALLENGTH_VALUE",
    "tail_length": "TAILLENGTH_VALUE",
    "hind_foot_with_claw": "HINDFOOTWITHCLAW_VALUE",
    "ear_from_notch": "EARFROMNOTCH_VALUE",
    "ear_from_crown": "EARFROMCROWN_VALUE",
    "length_units": "TAILLENGTH_UNITS",
    "weight": "WEIGHT_VALUE",
    "weight_units": "WEIGHT_UNITS",
    "lifestage": "LIFESTAGE_VALUE",
    "reproductive_data": "REPRODUCTIVEDATA_VALUE",
    "unformatted_measurements": "UNFORMATTEDMEASUREMENTS_VALUE",
}

# NOTE: Make sure to update the sorting logic if you change these at all
FIELD_NAMES = [
    "mvz_num",
    "guid",
    "subspecies",
    "collectors",
    "country",
    "state_prov",
    "county",
    "spec_locality",
    "ended_date",
    "parts",
    "total_length",
    "tail_length",
    "hind_foot_with_claw",
    "ear_from_notch",
    "ear_from_crown",
    "length_units",
    "weight",
    "weight_units",
    "lifestage",
    "reproductive_data",
    "testes_length",
    "testes_width",
    "embryo_count",
    "embryo_count_left",
    "embryo_count_right",
    "crown_rump_length",
    "scars",
    "unformatted_measurements",
    "initials",
    "day",
    "month",
    "year",
    "review_needed",
]

STATE_PROV_RANGES = [
    "Alaska",
    "Alberta",
    "Arizona",
    "Arkansas",
    "British Columbia",
    "California",
    "Colorado",
    "Idaho",
    "Illinois",
    "Kansas",
    "Mexico",
    "Michigan",
    "Montana",
    "Nebraska",
    "New Mexico",
    "North Dakota",
    "Nevada",
    "Oklahoma",
    "Oregon",
    "Saskatchewan",
    "South Dakota",
    "Texas",
    "Utah",
    "Washington",
    "Wyoming",
    "Aguascalientes",
    "Baja California",
    "Baja California Sur",
    "Campeche",
    "Chiapas",
    "Chihuahua",
    "Coahuila",
    "Colima",
    "Durango",
    "Guanajuato",
    "Guerrero",
    "Hidalgo",
    "Jalisco",
    "México",
    "Mexico",
    "México City",
    "Mexico City",
    "Michoacán",
    "Michoacan",
    "Morelos",
    "Nayarit",
    "Nuevo León",
    "Nuevo Leon",
    "Oaxaca",
    "Puebla",
    "Querétaro",
    "Queretaro",
    "Quintana Roo",
    "Sinaloa",
    "Sonora",
    "San Luis Potosi",
    "Tamaulipas",
    "Tlaxcala",
    "Veracruz",
    "Yucatán",
    "Yucatan",
    "Yukon",
    "Zacatecas",
]

st.title("Sheet Generator")
st.write("Upload a downloaded Arctos sheet CSV, then generate the sorted output sheet.")
arctos_sheet = st.file_uploader("Input CSV", type=["csv"])
if arctos_sheet is None:
    st.stop()

arctos_data = pd.read_csv(arctos_sheet, dtype=str)
arctos_data = arctos_data.fillna("")

missing_fields = [
    value for value in MAPPING.values() if value not in arctos_data.columns
]

if "MVZ_NUM" in missing_fields:
    missing_fields.remove("MVZ_NUM")

if "GUID" in missing_fields:
    st.error(f"GUID missing in input file {arctos_sheet.name}, invalid sheet.")
    st.stop()
else:
    st.warning(
        f"Missing fields {missing_fields} in input file: {arctos_sheet.name}, Assuming no data!"
    )

non_ranges_rows = []
output_rows = []
for row in arctos_data.to_dict(orient="records"):
    row["MVZ_NUM"] = row["GUID"].split(":")[-1]

    output_row = {
        field: (
            row[MAPPING[field]] if field in MAPPING and MAPPING[field] in row else ""
        )
        for field in FIELD_NAMES
    }

    if (
        output_row["country"] not in ["United States", "Mexico", "Canada"]
        or output_row["state_prov"] not in STATE_PROV_RANGES
    ):
        non_ranges_rows.append(output_row)
    else:
        output_rows.append(output_row)

if non_ranges_rows:
    st.write("## The following records are outside the Ranges area")
    st.dataframe(non_ranges_rows)

    result = st.radio(
        "How should we address this issue?",
        [
            "I will fix the sheet and reupload",
            "Include these rows",
            "Ignore these rows",
        ],
    )
    if result == "I will fix the sheet and reupload":
        st.stop()
    elif result == "Include these rows":
        output_rows.extend(non_ranges_rows)


output_rows.sort(
    key=lambda row: (
        row["subspecies"],
        row["country"],
        row["state_prov"],
        row["county"],
        row["spec_locality"],
        row["mvz_num"],
    )
)

output_csv = io.StringIO()
writer = csv.DictWriter(output_csv, fieldnames=FIELD_NAMES, quoting=csv.QUOTE_MINIMAL)
writer.writeheader()
writer.writerows(output_rows)

sheet_name = arctos_sheet.name.split(".")[0].replace(" ", "_").lower()

st.download_button(
    label="Download Generated Sheet",
    data=output_csv.getvalue(),
    file_name=f"{sheet_name}_ranges.csv",
    mime="text/csv",
    icon=":material/download:",
)
st.dataframe(pd.DataFrame(output_rows), hide_index=True)
