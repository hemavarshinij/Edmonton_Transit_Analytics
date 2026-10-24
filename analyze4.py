import pandas as pd

d = pd.read_csv("data/clean/delays_clean.csv",
                dtype={"route_id": str, "stop_id": str, "trip_id": str})
d = d[~d["outlier"]].copy()
d["seq"] = pd.to_numeric(d["stop_sequence"], errors="coerce")
d = d.dropna(subset=["seq"])
d["ts"] = d["ts"].astype(int)
d["date"] = (pd.to_datetime(d["ts"], unit="s", utc=True)
             .dt.tz_convert("America/Edmonton").dt.date)

# One row per stop visit: the last reading before the bus reached that stop
v = (d.sort_values("ts")
       .groupby(["date", "trip_id", "seq"])
       .tail(1)
       .copy())
v["trip_key"] = v["date"].astype(str) + "_" + v["trip_id"]
v["late"] = v["delay_sec"] > 300
v["early"] = v["delay_sec"] < -60

print("readings:", len(d), "-> stop visits:", len(v))
print("trip instances (date + trip_id):", v["trip_key"].nunique())
print("median delay (s): %.0f" % v["delay_sec"].median())

print("\n1. On-time share per stop visit")
for name, lo, hi in [("-1 to +5 min", -60, 300),
                     ("-2 to +5 min", -120, 300),
                     ("-3 to +5 min", -180, 300)]:
    p = ((v["delay_sec"] >= lo) & (v["delay_sec"] <= hi)).mean() * 100
    print("%-14s %.1f%%" % (name, p))
print("earlier than -1 min: %.1f%%" % (v["early"].mean() * 100))
print("later than +5 min:   %.1f%%" % (v["late"].mean() * 100))

print("\n2. Delay by position in the trip (one row per stop visit)")
v["pos"] = pd.cut(v["seq"], [0, 1, 2, 3, 10, 30, 1000],
                  labels=["1", "2", "3", "4-10", "11-30", "31+"])
print(v.groupby("pos", observed=True)["delay_sec"]
        .agg(["count", "median"]).round(0).to_string())

print("\n3. By hour (Edmonton time)")
h = v.groupby("hour").agg(stop_visits=("delay_sec", "size"),
                          pct_late=("late", "mean"),
                          pct_early=("early", "mean"),
                          median=("delay_sec", "median"))
h["pct_late"] = (h["pct_late"] * 100).round(1)
h["pct_early"] = (h["pct_early"] * 100).round(1)
h["median"] = h["median"].round(0)
print(h.to_string())

print("\n4. Routes (at least 20 trip instances)")
r = v.groupby(["route_id", "route_long_name"]).agg(
    stop_visits=("delay_sec", "size"),
    trips=("trip_key", "nunique"),
    pct_late=("late", "mean"),
    pct_early=("early", "mean"),
    median=("delay_sec", "median"))
r = r[r["trips"] >= 20].copy()
r["pct_late"] = (r["pct_late"] * 100).round(1)
r["pct_early"] = (r["pct_early"] * 100).round(1)
r["median"] = r["median"].round(0)
print("most late:")
print(r.sort_values("pct_late", ascending=False).head(10).to_string())
print("most early:")
print(r.sort_values("pct_early", ascending=False).head(5).to_string())

print("\n5. Hours 19 and 20 by day")
x = v[v["hour"].isin([19, 20])].groupby(["date", "hour"]).agg(
    stop_visits=("delay_sec", "size"), pct_late=("late", "mean"))
x["pct_late"] = (x["pct_late"] * 100).round(1)
print(x.to_string())

v.to_csv("data/clean/stop_visits.csv", index=False)
print("\nsaved data/clean/stop_visits.csv")
