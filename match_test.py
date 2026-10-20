import pandas as pd

t = pd.read_csv("data/raw/gtfs_static/trips.csv", dtype=str,
                usecols=["route_id", "service_id", "trip_id"])
live = pd.read_csv("data/raw/trip_updates.csv", dtype=str)

ids = live["trip_id"].dropna().unique()
share = pd.Series(ids).isin(t["trip_id"]).mean() * 100

print("distinct live trip_ids:", len(ids))
print("found in trips.csv: %.1f%%" % share)
print(t["service_id"].str[:8].value_counts().head())
