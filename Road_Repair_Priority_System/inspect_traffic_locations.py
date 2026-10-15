
import pandas as pd
from pathlib import Path

project = Path(__file__).parent

traffic_file = project / "outputs" / "final_traffic.csv"
survey_file = project / "outputs" / "combined_road_surveys.csv"

traffic = pd.read_csv(traffic_file)
survey = pd.read_csv(survey_file, low_memory=False)

print("TRAFFIC LOCATION ANALYSIS")
print("=========================")

# Traffic dates format කිරීම
traffic["Traffic_Date"] = pd.to_datetime(
    traffic["Traffic_Date"],
    errors="coerce"
)

# Survey chainage numeric කිරීම
survey["Chainage__km_"] = pd.to_numeric(
    survey["Chainage__km_"],
    errors="coerce"
)

roads = sorted(traffic["Road_ID"].dropna().unique())

for road in roads:

    road_traffic = traffic[
        traffic["Road_ID"] == road
    ].copy()

    road_survey = survey[
        survey["Road_ID"] == road
    ].copy()

    print("\n----------------------------")
    print("ROAD:", road)

    print("Survey Records:", len(road_survey))

    print(
        "Survey Chainage Range:",
        road_survey["Chainage__km_"].min(),
        "to",
        road_survey["Chainage__km_"].max()
    )

    print("\nTraffic Stations:")

    columns = [
        "Traffic_Chainage_km",
        "Traffic_Date",
        "Total_Vehicles",
        "Count_Hours",
        "Vehicles_Per_Hour"
    ]

    print(
        road_traffic[columns].to_string(index=False)
    )

print("\nANALYSIS COMPLETED!")
