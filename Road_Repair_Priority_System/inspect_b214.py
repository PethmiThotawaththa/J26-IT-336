
import pandas as pd
from pathlib import Path

project = Path(__file__).parent

survey_file = project / "outputs" / "combined_road_surveys.csv"
traffic_file = project / "outputs" / "final_traffic.csv"

survey = pd.read_csv(survey_file, low_memory=False)
traffic = pd.read_csv(traffic_file)

# B214 records only
b214_survey = survey[
    survey["Road_ID"] == "B214"
].copy()

b214_traffic = traffic[
    traffic["Road_ID"] == "B214"
].copy()

print("B214 CHAINAGE INVESTIGATION")
print("==========================")

print("\nSurvey Records:", len(b214_survey))

print("\nSurvey Details:")
columns = [
    "Survey_Name",
    "Section",
    "Chainage__km_",
    "Sub_Chainage__km_",
    "Latitude__deg_",
    "Longitude__deg_",
    "Road_Side"
]

print(
    b214_survey[columns]
    .head(10)
    .to_string(index=False)
)

print("\nSurvey Sections:")
print(
    b214_survey["Section"]
    .value_counts(dropna=False)
    .head(15)
)

print("\nTraffic Stations:")
print(
    b214_traffic[
        [
            "Road_ID",
            "Traffic_Chainage_km",
            "Traffic_Date",
            "Vehicles_Per_Hour"
        ]
    ].to_string(index=False)
)

print("\nINVESTIGATION COMPLETED!")
