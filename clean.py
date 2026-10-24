import pandas as pd

RAW = "data/raw/"
STATIC = "data/raw/gtfs_static/"
OUT = "data/clean/"

# 1. Live delays: drop duplicates and blank-ID rows
t = pd.read_csv(RAW + "trip_updates.csv", dtype=str)
t = t.dropna(subset=["trip_id"]).drop_duplicates()
t["delay_sec"] = pd.to_numeric(t["delay_sec"], errors="coerce")
t = t.dropna(subset=["delay_sec"])

# 2. Time: Unix seconds to Edmonton local time
ts = pd.to_datetime(t["ts"].astype(int), unit="s", utc=True).dt.tz_convert("America/Edmonton")
t["local_time"] = ts
t["hour"] = ts.dt.hour
t["weekday"] = ts.dt.day_name()

# 3. Flag extreme delays (keep them, just mark them)
t["outlier"] = (t["delay_sec"] < -600) | (t["delay_sec"] > 3600)

# 4. Join to routes and stops (these do not depend on trips.csv)
r = pd.read_csv(STATIC + "routes.csv", dtype=str,
                usecols=["route_id", "route_long_name"])
s = pd.read_csv(STATIC + "stops.csv", dtype=str,
                usecols=["stop_id", "stop_name", "stop_lat", "stop_lon"])
t = t.merge(r, on="route_id", how="left").merge(s, on="stop_id", how="left")

# 5. Flag whether the trip is in the timetable
tr = pd.read_csv(STATIC + "trips.csv", dtype=str, usecols=["trip_id"])
t["in_timetable"] = t["trip_id"].isin(tr["trip_id"])

t.to_csv(OUT + "delays_clean.csv", index=False)

print("clean rows:", len(t))
print("outliers flagged:", int(t["outlier"].sum()))
print("route found: %.1f%%" % (t["route_long_name"].notna().mean() * 100))
print("stop found: %.1f%%" % (t["stop_name"].notna().mean() * 100))
print("in timetable: %.1f%%" % (t["in_timetable"].mean() * 100))
print(t["delay_sec"].describe())

