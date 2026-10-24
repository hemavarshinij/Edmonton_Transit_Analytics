import pandas as pd

v = pd.read_csv("data/raw/vehicle_positions.csv", usecols=["ts"])
ts = pd.Series(sorted(v["ts"].unique()))
print("snapshots:", len(ts))

first = pd.to_datetime(ts.iloc[0], unit="s", utc=True).tz_convert("America/Edmonton")
last = pd.to_datetime(ts.iloc[-1], unit="s", utc=True).tz_convert("America/Edmonton")
print("first snapshot (Edmonton):", first.strftime("%a %d %b %H:%M"))
print("last snapshot  (Edmonton):", last.strftime("%a %d %b %H:%M"))

for i in range(1, len(ts)):
    if ts.iloc[i] - ts.iloc[i - 1] > 180:
        a = pd.to_datetime(ts.iloc[i - 1], unit="s", utc=True).tz_convert("America/Edmonton")
        b = pd.to_datetime(ts.iloc[i], unit="s", utc=True).tz_convert("America/Edmonton")
        mins = int((ts.iloc[i] - ts.iloc[i - 1]) / 60)
        print("gap %d min: %s -> %s (Edmonton)" % (mins, a.strftime("%a %d %H:%M"), b.strftime("%a %d %H:%M")))
