# collector.py - saves a snapshot of live Edmonton bus data every 60 seconds
import csv, os, time, requests
from google.transit import gtfs_realtime_pb2

BASE = "http://gtfs.edmonton.ca/TMGTFSRealTimeWebService"
TU = BASE + "/TripUpdate/TripUpdates.pb"      # delays
VP = BASE + "/Vehicle/VehiclePositions.pb"    # where buses are
os.makedirs("data/raw", exist_ok=True)

def open_csv(path, header):
    new = not os.path.exists(path)
    f = open(path, "a", newline="")
    w = csv.writer(f)
    if new:
        w.writerow(header)
    return f, w

f1, w1 = open_csv("data/raw/trip_updates.csv",
    ["ts", "trip_id", "route_id", "stop_id", "stop_sequence", "delay_sec"])
f2, w2 = open_csv("data/raw/vehicle_positions.csv",
    ["ts", "vehicle_id", "trip_id", "route_id", "lat", "lon", "speed_mps"])

def get(url):
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(requests.get(url, timeout=20).content)
    return feed

while True:
    now = int(time.time())
    try:
        n1 = 0
        for e in get(TU).entity:
            if e.HasField("trip_update"):
                tu = e.trip_update
                for s in list(tu.stop_time_update)[:1]:      # next stop only
                    if s.HasField("arrival") and s.arrival.HasField("delay"):
                        w1.writerow([now, tu.trip.trip_id, tu.trip.route_id,
                                     s.stop_id, s.stop_sequence, s.arrival.delay])
                        n1 += 1
        f1.flush()
    except Exception as ex:
        n1 = f"error {ex}"
    try:
        n2 = 0
        for e in get(VP).entity:
            if e.HasField("vehicle"):
                v = e.vehicle
                w2.writerow([now, v.vehicle.id, v.trip.trip_id, v.trip.route_id,
                             v.position.latitude, v.position.longitude, v.position.speed])
                n2 += 1
        f2.flush()
    except Exception as ex:
        n2 = f"error {ex}"
    print(time.strftime("%H:%M:%S"), "trip rows:", n1, "| vehicle rows:", n2)
    time.sleep(60)

