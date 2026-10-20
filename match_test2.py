import pandas as pd

t = pd.read_csv("data/raw/gtfs_static/trips.csv", dtype=str,
                usecols=["route_id", "service_id", "trip_id"])
live = pd.read_csv("data/raw/trip_updates.csv", dtype=str)

print("trips.csv rows:", len(t), "| distinct trip_ids:", t.trip_id.nunique())
print("live rows:", len(live), "| empty trip_id rows:", live.trip_id.isna().sum())

L = live.dropna(subset=["trip_id"]).copy()
L["match"] = L.trip_id.isin(t.trip_id)
print("row-weighted match: %.1f%%" % (L.match.mean() * 100))

miss = L[~L.match].drop_duplicates("trip_id")
print("unmatched distinct trip_ids:", len(miss))

tid = pd.to_numeric(t.trip_id, errors="coerce")
mid = pd.to_numeric(miss.trip_id, errors="coerce")
print("trips.csv trip_id range:", tid.min(), "to", tid.max())
print("unmatched live range:", mid.min(), "to", mid.max())

print("\nunmatched by route:")
print(miss.route_id.value_counts().head(8))

L["hr"] = (pd.to_datetime(L.ts.astype(int), unit="s", utc=True)
           .dt.tz_convert("America/Edmonton").dt.hour)
print("\nmatch rate by Edmonton hour:")
print(L.groupby("hr").match.mean().round(2).to_string())

print("\nsample service_ids:")
print(t.service_id.drop_duplicates().head(12).to_string())
