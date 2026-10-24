import pandas as pd

d = pd.read_csv("data/clean/delays_clean.csv",
                dtype={"route_id": str, "stop_id": str, "trip_id": str})
d = d[~d["outlier"]].copy()
d["seq"] = pd.to_numeric(d["stop_sequence"], errors="coerce")
d["late"] = d["delay_sec"] > 300
d["date"] = (pd.to_datetime(d["ts"].astype(int), unit="s", utc=True)
             .dt.tz_convert("America/Edmonton").dt.date)

print("1. Readings per trip at each stop position")
d["pos"] = pd.cut(d["seq"], [0, 1, 2, 3, 10, 30, 1000],
                  labels=["1", "2", "3", "4-10", "11-30", "31+"])
g = d.groupby("pos", observed=True).agg(
    readings=("delay_sec", "size"),
    trips=("trip_id", "nunique"),
    median=("delay_sec", "median"))
g["readings_per_trip"] = (g["readings"] / g["trips"]).round(1)
print(g.to_string())

print("\n2. At stop 2: does the delay stay frozen within a trip?")
s2 = d[d["seq"] == 2]
per = s2.groupby("trip_id").agg(
    n=("delay_sec", "size"),
    distinct=("delay_sec", "nunique"),
    d_first=("delay_sec", "first"),
    d_last=("delay_sec", "last"))
per = per[per["n"] >= 3]
print("trips with 3+ readings at stop 2:", len(per))
print("share whose delay never changes: %.0f%%" % ((per["distinct"] == 1).mean() * 100))
print("median change, first to last reading (s):", (per["d_last"] - per["d_first"]).median())

print("\n3. Late share by hour, all stops vs stop 4 and later")
def by(df, key):
    out = df.groupby(key).agg(readings=("delay_sec", "size"),
                              pct_late=("late", "mean"),
                              median=("delay_sec", "median"))
    out["pct_late"] = (out["pct_late"] * 100).round(1)
    return out
a = by(d, "hour")
b = by(d[d["seq"] > 3], "hour")
print(a[["pct_late"]].join(b[["readings", "pct_late"]], lsuffix="_all", rsuffix="_stop4plus").to_string())

print("\n4. Routes by late share using stop 4 and later (at least 20 trips)")
r = d[d["seq"] > 3].groupby(["route_id", "route_long_name"]).agg(
    readings=("delay_sec", "size"),
    trips=("trip_id", "nunique"),
    pct_late=("late", "mean"),
    median=("delay_sec", "median"))
r = r[r["trips"] >= 20]
r["pct_late"] = (r["pct_late"] * 100).round(1)
print(r.sort_values("pct_late", ascending=False).head(10).to_string())

print("\n5. Hours 19 and 20 by day: one bad evening or every evening?")
h = d[d["hour"].isin([19, 20])]
x = h.groupby(["date", "hour"]).agg(readings=("delay_sec", "size"), pct_late=("late", "mean"))
x["pct_late"] = (x["pct_late"] * 100).round(1)
print(x.to_string())
