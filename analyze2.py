import pandas as pd

d = pd.read_csv("data/clean/delays_clean.csv", dtype={"route_id": str, "stop_id": str})
d["date"] = (pd.to_datetime(d["ts"].astype(int), unit="s", utc=True)
             .dt.tz_convert("America/Edmonton").dt.date)

print("1. Share of readings whose trip is in the timetable, by day:")
print((d.groupby("date")["in_timetable"].mean() * 100).round(1).to_string())

d = d[~d["outlier"]].copy()

print("\n2. On-time share under different definitions:")
for name, lo, hi in [("-1 to +5 min", -60, 300),
                     ("-2 to +5 min", -120, 300),
                     ("-3 to +5 min", -180, 300)]:
    p = ((d["delay_sec"] >= lo) & (d["delay_sec"] <= hi)).mean() * 100
    print("%-14s %.1f%%" % (name, p))
print("earlier than -1 min: %.1f%%" % ((d["delay_sec"] < -60).mean() * 100))
print("later than +5 min:   %.1f%%" % ((d["delay_sec"] > 300).mean() * 100))

print("\n3. Delay by position in the trip (is early = holding at the start?):")
d["seq"] = pd.to_numeric(d["stop_sequence"], errors="coerce")
d["pos"] = pd.cut(d["seq"], [0, 1, 3, 10, 30, 1000],
                  labels=["stop 1", "stops 2-3", "stops 4-10", "stops 11-30", "stops 31+"])
print(d.groupby("pos", observed=True)["delay_sec"].agg(["count", "median"]).round(0).to_string())

print("\n4. Weekday vs weekend:")
d["weekend"] = d["weekday"].isin(["Saturday", "Sunday"])
print(d.groupby("weekend")["delay_sec"].agg(["count", "median", "mean"]).round(0).to_string())

print("\n5. Routes by median delay (at least 20 distinct trips):")
r = d.groupby(["route_id", "route_long_name"]).agg(
    readings=("delay_sec", "size"), trips=("trip_id", "nunique"),
    median=("delay_sec", "median"))
r = r[r["trips"] >= 20].round(0)
print("latest:")
print(r.sort_values("median", ascending=False).head(8).to_string())
print("earliest:")
print(r.sort_values("median").head(8).to_string())

print("\n6. Readings in hour 15, by day:")
print(d[d["hour"] == 15].groupby("date").size().to_string())
