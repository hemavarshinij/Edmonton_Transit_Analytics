import pandas as pd

d = pd.read_csv("data/clean/delays_clean.csv", dtype={"route_id": str, "stop_id": str})
d = d[~d["outlier"]]

print("rows used (outliers removed):", len(d))

print("\nBy hour (Edmonton time):")
h = d.groupby("hour")["delay_sec"].agg(["count", "median", "mean"]).round(0)
print(h.to_string())

by_route = d.groupby(["route_id", "route_long_name"])["delay_sec"].agg(["count", "median", "mean"]).round(0)
by_route = by_route[by_route["count"] >= 30]

print("\nLatest routes (median delay, at least 30 readings):")
print(by_route.sort_values("median", ascending=False).head(8).to_string())

print("\nEarliest routes:")
print(by_route.sort_values("median").head(8).to_string())
