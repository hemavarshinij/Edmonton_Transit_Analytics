import pandas as pd

t = pd.read_csv("data/raw/gtfs_static/trips.csv", dtype=str, usecols=["route_id", "trip_id"])
st = pd.read_csv("data/raw/gtfs_static/stop_times.csv", dtype=str, usecols=["trip_id"])
r = pd.read_csv("data/raw/gtfs_static/routes.csv", dtype=str, usecols=["route_id"])
live = pd.read_csv("data/raw/trip_updates.csv", dtype=str)

tmax = pd.to_numeric(t.trip_id, errors="coerce").max()
has = live.dropna(subset=["trip_id"]).copy()
has["in_trips"] = has.trip_id.isin(t.trip_id)
has["in_stop_times"] = has.trip_id.isin(st.trip_id.unique())

miss = has[~has.in_trips].drop_duplicates("trip_id")
num = pd.to_numeric(miss.trip_id, errors="coerce")
print("unmatched distinct trip_ids:", len(miss))
print("  above the trips.csv max id:", int((num > tmax).sum()))
print("  inside the id range (gaps):", int((num <= tmax).sum()))
print("  also found in stop_times.csv: %.0f%%" % (miss.in_stop_times.mean() * 100))

e = live[live.trip_id.isna()]
key = ["ts", "stop_id", "stop_sequence", "delay_sec"]
m = e.merge(has[key].drop_duplicates(), on=key, how="left", indicator=True)
print("\nempty-trip rows:", len(e))
print("  exact copy of a row that has a trip_id: %.0f%%" % ((m._merge == "both").mean() * 100))

print("\nlive rows whose route_id exists in routes.csv: %.1f%%"
      % (live.route_id.isin(r.route_id).mean() * 100))
print("(empty route_id counts as not found)")
