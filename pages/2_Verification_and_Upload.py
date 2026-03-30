import sys
import os
import io
import csv
import pint
import numpy as np
import plotly.express as px

ureg = pint.UnitRegistry()

import streamlit as st
import pandas as pd

from ranges.sheets import SheetParser
from ranges.specimen import Specimen

st.set_page_config(page_title="Verification and Upload", layout="wide")
st.title("Prepare Ranges Sheets for Upload to Arctos")

st.write("Add the file you want to prepare to upload to Arctos")
upload_sheet = st.file_uploader("Sheet to prepare for upload", type=["csv"])
if upload_sheet is None:
    st.stop()


accession_data = pd.read_csv(upload_sheet, dtype=str)
accession_data = accession_data.fillna("")
accession_data = accession_data.to_dict(orient="records")

warnings = []

if len(accession_data) == 0:
    warnings.append("The uploaded sheet is empty")

missing_columns = SheetParser.verify_columns_exist(accession_data[0].keys())
if len(missing_columns) > 0:
    warnings.append(f"Missing columns in Uploaded File: {missing_columns}")

if warnings:
    st.write("## Warnings")
    for warning in warnings:
        st.write(warning)

    ignore_warnings = st.checkbox(
        "I have read these warnings and they are not relevant"
    )
    if not ignore_warnings:
        st.stop()


review_needed = []
specimens = []
for raw_record in accession_data:
    try:
        specimen = Specimen.from_raw_record(raw_record)
        specimens.append(specimen)
    except Exception as ex:
        review_needed.append([raw_record["guid"], str(ex)])

if review_needed:
    st.write(
        "## Please address these issues or remove these records and reupload the sheet!"
    )
    df = pd.DataFrame(
        review_needed,
        columns=["guid", "Issue"],
    )
    st.dataframe(df, hide_index=True)

    ignore_review = st.checkbox("Ignore these records and proceed.")
    if not ignore_review:
        st.stop()


st.write("## Outlier Analysis")

species_data = pd.DataFrame([specimen.to_dict() for specimen in specimens])


def convert_to_metric(value, unit):
    if value is None:
        return value

    preferred_units = [
        ureg.mm,
        ureg.g,
    ]

    return (value * ureg.parse_units(unit)).to_preferred(preferred_units).magnitude


for attribute in [
    "total_length",
    "tail_length",
    "hind_foot_with_claw",
    "ear_from_notch",
    "ear_from_crown",
]:
    species_data[attribute] = species_data.apply(
        lambda x: convert_to_metric(x[attribute], x["distance_unit"]), axis=1
    )

species_data["weight"] = species_data.apply(
    lambda x: x["weight"] * 28.3495 if x["weight_unit"] == "oz" else x["weight"], axis=1
)

fig = px.scatter(
    species_data,
    x="total_length",
    y="tail_length",
    hover_data=["guid"],
    title="Total Length vs Tail Length Outliers",
    height=800,
)

fig.update_traces(
    marker=dict(size=15, line=dict(width=1, color="DarkSlateGrey")),
    selector=dict(mode="markers"),
)

st.plotly_chart(fig)

fig = px.scatter(
    species_data,
    x="total_length",
    y="weight",
    hover_data=["guid"],
    title="Total Length vs Weight Outliers",
    height=800,
)

fig.update_traces(
    marker=dict(size=15, line=dict(width=1, color="DarkSlateGrey")),
    selector=dict(mode="markers"),
)

st.plotly_chart(fig)

fig = px.scatter(
    species_data,
    x="total_length",
    y="ear_from_notch",
    hover_data=["guid"],
    title="Total Length vs Ear From Notch Outliers",
    height=800,
)

fig.update_traces(
    marker=dict(size=15, line=dict(width=1, color="DarkSlateGrey")),
    selector=dict(mode="markers"),
)
st.plotly_chart(fig)

fig = px.scatter(
    species_data,
    x="hind_foot_with_claw",
    y="ear_from_notch",
    hover_data=["guid"],
    title="Hind Foor With Claw vs Ear From Notch Outliers",
    height=800,
)

fig.update_traces(
    marker=dict(size=15, line=dict(width=1, color="DarkSlateGrey")),
    selector=dict(mode="markers"),
)
st.plotly_chart(fig)

accept_outliers = st.checkbox(
    "I have reviewed possible outliers and the data is fit for upload."
)
if not accept_outliers:
    st.stop()

st.write("## Upload a Recent Arctos Attributes Download")
st.write("This is needed so we can avoid double uploading existing attributes.")
arctos_sheet = st.file_uploader("Recent attributes download from Arctos", type=["csv"])
if arctos_sheet is None:
    st.stop()

arctos_data = pd.read_csv(arctos_sheet, dtype=str)
arctos_data = arctos_data.fillna("")
arctos_data = arctos_data.to_dict(orient="records")

if (
    "GUID" not in arctos_data[0]
    or "ATTRIBUTE_TYPE" not in arctos_data[0]
    or "ATTRIBUTE_VALUE" not in arctos_data[0]
):
    st.error(
        "Uploaded sheet doesn't contain all expected fields. Missing one of GUID, ATTRIBUTE_TYPE, ATTRIBUTE_VALUE"
    )
    st.stop()

arctos_data_lookup = {
    (record["GUID"], record["ATTRIBUTE_TYPE"]): record["ATTRIBUTE_VALUE"]
    for record in arctos_data
}

attributes = []
unitless_attributes = []
failures = []
skips = 0


for specimen in specimens:
    try:
        if specimen.collectors is None:
            specimen.collectors = "Museum of Vertebrate Zoology"

        specimen_attributes, specimen_unitless_attributes = specimen.export_attributes()

        for attribute in specimen_attributes:
            if (attribute["guid"], attribute["attribute_type"]) in arctos_data_lookup:
                if float(
                    arctos_data_lookup[(attribute["guid"], attribute["attribute_type"])]
                ) != float(attribute["attribute_value"]):

                    failures.append(
                        {
                            "guid": attribute["guid"],
                            "type": attribute["attribute_type"],
                            "arctos_value": arctos_data_lookup[
                                (attribute["guid"], attribute["attribute_type"])
                            ],
                            "sheet_value": attribute["attribute_value"],
                        }
                    )
                else:
                    # If the duplicate is exactly the same then we can skip it in the upload.
                    skips += 1
            else:
                attributes.append(attribute)

        for attribute in specimen_unitless_attributes:
            if (attribute["guid"], attribute["attribute_type"]) in arctos_data_lookup:
                if (
                    arctos_data_lookup[(attribute["guid"], attribute["attribute_type"])]
                    != attribute["attribute_value"]
                ):
                    failures.append(
                        {
                            "guid": attribute["guid"],
                            "type": attribute["attribute_type"],
                            "arctos_value": arctos_data_lookup[
                                (attribute["guid"], attribute["attribute_type"])
                            ],
                            "sheet_value": attribute["attribute_value"],
                        }
                    )
                else:
                    # If the duplicate is exactly the same then we can skip it in the upload.
                    skips += 1
            else:
                unitless_attributes.append(attribute)

    except Exception as ex:
        st.write(ex, specimen.to_dict())

st.write("## Comparison with existing Arctos Records")
if skips:
    st.write(f"Skipped {skips} attributes which are already uploaded to Arctos.")

if failures:
    st.error(
        "The following values in the upload sheet don't match what has been already uploaded to arctos!"
    )
    st.dataframe(failures)

    accept_failures = st.checkbox(
        "I understand that these records will not be included in the Arctos upload."
    )
    if not accept_failures:
        st.stop()


if not skips and not failures:
    st.info(
        "No values in the Arctos sheet matched with the upload sheet. Double check that this is expected."
    )


def rows_to_csv(data: list[list[str]]) -> str:
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=data[0].keys(), quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    writer.writerows(data)
    return out.getvalue()


st.write("## The Following Sheets are Formatted for Arctos Upload")
sheet_name = upload_sheet.name.split(".")[0].replace(" ", "_").lower()

if attributes:
    st.write("### Attributes with Units")
    st.download_button(
        label="Download Attributes with Units",
        data=rows_to_csv(attributes),
        file_name=f"{sheet_name}_unit_attributes.csv",
        mime="text/csv",
        icon=":material/download:",
    )
    st.dataframe(pd.DataFrame(attributes))

if unitless_attributes:
    st.write("### Attributes without Units")
    st.download_button(
        label="Download Attributes without Units",
        data=rows_to_csv(unitless_attributes),
        file_name=f"{sheet_name}_unitless_attributes.csv",
        mime="text/csv",
        icon=":material/download:",
    )
    st.dataframe(pd.DataFrame(unitless_attributes))

if not attributes and not unitless_attributes:
    st.warning("No attributes generated!")
