import duckdb

con = duckdb.connect()
con.execute("""
CREATE VIEW d AS
SELECT * FROM read_csv('data/clean/delays_clean.csv', header=true,
    types={'route_id':'VARCHAR','stop_id':'VARCHAR','trip_id':'VARCHAR'})
""")

def show(title, query):
    print("\n" + title)
    print(con.execute(query).df().to_string(index=False))

show("1. Routes with the highest share of late readings (>5 min), at least 20 trips", """
WITH clean AS (
    SELECT route_id, route_long_name, trip_id, delay_sec
    FROM d
    WHERE delay_sec BETWEEN -600 AND 3600
),
route_stats AS (
    SELECT route_id, route_long_name,
           COUNT(DISTINCT trip_id) AS trips,
           COUNT(*) AS readings,
           ROUND(MEDIAN(delay_sec)) AS median_delay,
           ROUND(100.0 * AVG(CASE WHEN delay_sec > 300 THEN 1 ELSE 0 END), 1) AS pct_late
    FROM clean
    GROUP BY route_id, route_long_name
    HAVING COUNT(DISTINCT trip_id) >= 20
)
SELECT RANK() OVER (ORDER BY pct_late DESC) AS late_rank, *
FROM route_stats
ORDER BY late_rank
LIMIT 10
""")

show("2. Late and early share by hour, with a 3-hour rolling average", """
WITH hourly AS (
    SELECT hour,
           COUNT(*) AS readings,
           100.0 * AVG(CASE WHEN delay_sec > 300 THEN 1 ELSE 0 END) AS pct_late,
           100.0 * AVG(CASE WHEN delay_sec < -60 THEN 1 ELSE 0 END) AS pct_early
    FROM d
    WHERE delay_sec BETWEEN -600 AND 3600
    GROUP BY hour
)
SELECT hour, readings,
       ROUND(pct_late, 1) AS pct_late,
       ROUND(pct_early, 1) AS pct_early,
       ROUND(AVG(pct_late) OVER (ORDER BY hour ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING), 1) AS late_3h_avg
FROM hourly
ORDER BY hour
""")

show("3. The first five stops of a trip, one at a time (checking the stops 2-3 bump)", """
SELECT CAST(stop_sequence AS INTEGER) AS seq,
       COUNT(*) AS readings,
       ROUND(MEDIAN(delay_sec)) AS median_delay
FROM d
WHERE delay_sec BETWEEN -600 AND 3600
  AND CAST(stop_sequence AS INTEGER) <= 5
GROUP BY seq
ORDER BY seq
""")
