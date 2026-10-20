# Data Dictionary: Edmonton Transit Delay Analysis

Source: City of Edmonton Open Data (static GTFS timetable) and the ETS
GTFS-Realtime feed (live), collected from 19 Oct 2026.
Rule: all ID columns are read as text, because values like "007" or "S8200"
lose meaning if read as numbers.

## routes.csv (static) - one row per bus route
- route_id: unique code for the route, text with leading zeros (e.g. 001A)
- route_short_name: the route label riders see (same as route_id in this file)
- route_long_name: where the route runs, e.g. "Downtown - Capilano"
- route_desc: description (empty in the rows seen)
- route_type: GTFS code for the vehicle type; 3 means bus
- route_type_descr: the same thing in words ("Bus")
- route_url: web page for the route (empty in the rows seen)

## trips.csv (static) - one row per scheduled bus run
- route_id: the route this trip belongs to (links to routes.csv)
- service_id: which calendar/day pattern the trip runs on (e.g. weekday, Saturday)
- trip_id: unique code for the trip (links to the live feed and stop_times.csv)
- trip_headsign: destination shown on the bus
- direction_id: 0 or 1, the two directions of the route
- block_id: unclear (probably groups trips run by the same bus)
- shape_id: code for the route's path on the map
- wheelchair_accessible: true/false
- bikes_allowed: true/false
- line_length: length of the route path; unit unclear (probably metres)
- geometry_line: the route path as map coordinates; very large, not needed, skipped when loading

## stops.csv (static) - one row per bus stop
- stop_id: unique stop code, text (e.g. 4380 or S8200)
- stop_code: code shown on the stop sign
- stop_name: name of the stop
- stop_desc: description (empty in the rows seen)
- stop_lat: latitude of the stop
- stop_lon: longitude of the stop
- zone_id: unclear (some fare or area zone code)
- stop_url: web page for the stop (empty in the rows seen)
- location_type: 0 means a normal stop
- parent_station: parent station if the stop is part of one (empty in the rows seen)
- level_name: unclear (e.g. "Ground Level")
- geometry_point: the stop location again in map format; duplicate of lat/lon, not needed

## stop_times.csv (static) - one row per bus at one stop, with the planned time
- trip_id: the trip (links to trips.csv)
- arrival_time: planned arrival at the stop, as text HH:MM:SS (can go past 24:00)
- departure_time: planned departure from the stop, as text
- stop_id: the stop (links to stops.csv)
- stop_sequence: the order of this stop within the trip (1 = first stop)
- pickup_type: whether passengers can board here; 0 = normal, 1 = no pickup
- drop_off_type: whether passengers can get off here; 0 = normal, 1 = none
- arrival_time_fixed: unclear (looks like a cleaned copy of arrival_time)
- departure_time_fixed: unclear (looks like a cleaned copy of departure_time)

## trip_updates.csv (live, collected by collector.py) - delay at a bus's next stop
- ts: snapshot time as Unix seconds (seconds since 1 Jan 1970, UTC)
- trip_id: the trip (links to trips.csv; blank in some rows)
- route_id: the route (links to routes.csv; blank in some rows)
- stop_id: the next stop the bus will reach (links to stops.csv)
- stop_sequence: the position of that stop within the trip
- delay_sec: delay in seconds; positive = late, negative = early

## vehicle_positions.csv (live, collected by collector.py) - where each bus is
- ts: snapshot time as Unix seconds
- vehicle_id: the physical bus
- trip_id: the trip the bus is running
- route_id: the route the bus is running
- lat: latitude of the bus
- lon: longitude of the bus
- speed_mps: speed in metres per second (0 = stopped)

## Data quality notes (found 20 Oct 2026)
- 2,452 of 12,412 trip_updates rows (about 20%) had blank trip_id and route_id.
  All were exact duplicates of rows that do have IDs, so they are dropped.
- Only about 46% of distinct live trip_ids were found in trips.csv, and none of
  the unmatched ones were in stop_times.csv. The cause is still being investigated.
- Joins on route_id (to routes.csv) and stop_id (to stops.csv) do not depend on
  trips.csv, so analysis by route, stop and hour is still possible.
- About 1% of snapshots had one corrupt feed message ("Wire format was corrupt").
  The next minute was always normal.
