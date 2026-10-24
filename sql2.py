import duckdb

con = duckdb.connect()
con.execute("""
CREATE VIEW v AS
SELECT * FROM read_csv('data/clean/stop_visits.csv', header=true,
    types={'route_id':'VARCHAR','stop_id':'VARCHAR','trip_id':'VARCHAR'})
""")

def show(title, query):
    print("\n" + title)
    print(con.execute(query).df().to_string(index=False))

show("1. Which routes produce the most late visits (>5 min)? Pareto", """
WITH route_stats AS (
    SELECT route_id, route_long_name,
           COUNT(*) AS visits,
           SUM(CASE WHEN delay_sec > 300 THEN 1 ELSE 0 END) AS late_visits
    FROM v
    GROUP BY route_id, route_long_name
),
totals AS (
    SELECT SUM(late_visits) AS total_late,
           100.0 * SUM(late_visits) / SUM(visits) AS sys_pct_late
    FROM route_stats
),
ranked AS (
    SELECT r.*,
           100.0 * r.late_visits / r.visits AS pct_late,
           100.0 * r.late_visits / t.total_late AS share_of_all_late,
           100.0 * SUM(r.late_visits) OVER (
               ORDER BY r.late_visits DESC, r.route_id
               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) / t.total_late AS cumulative_share,
           (100.0 * r.late_visits / r.visits) / t.sys_pct_late AS late_index
    FROM route_stats r CROSS JOIN totals t
)
SELECT RANK() OVER (ORDER BY late_visits DESC) AS late_rank,
       route_id, route_long_name, visits, late_visits,
       ROUND(pct_late, 1) AS pct_late,
       ROUND(share_of_all_late, 1) AS share_of_all_late,
       ROUND(cumulative_share, 1) AS cumulative_share,
       ROUND(late_index, 1) AS late_index
FROM ranked
ORDER BY late_visits DESC, route_id
LIMIT 10
""")

show("2. Top 3 routes by late share within each part of the day (at least 30 visits)", """
WITH banded AS (
    SELECT route_id, route_long_name, delay_sec,
           CASE WHEN hour BETWEEN 6 AND 8 THEN '1 morning peak (6-9)'
                WHEN hour BETWEEN 9 AND 14 THEN '2 midday (9-15)'
                WHEN hour BETWEEN 15 AND 17 THEN '3 afternoon peak (15-18)'
                WHEN hour BETWEEN 18 AND 23 THEN '4 evening (18-24)'
                ELSE '5 night (0-6)' END AS band
    FROM v
),
stats AS (
    SELECT band, route_id, route_long_name,
           COUNT(*) AS visits,
           ROUND(100.0 * AVG(CASE WHEN delay_sec > 300 THEN 1 ELSE 0 END), 1) AS pct_late
    FROM banded
    GROUP BY band, route_id, route_long_name
    HAVING COUNT(*) >= 30
)
SELECT * FROM (
    SELECT band,
           RANK() OVER (PARTITION BY band ORDER BY pct_late DESC) AS rank_in_band,
           route_id, route_long_name, visits, pct_late
    FROM stats
) t
WHERE rank_in_band <= 3
ORDER BY band, rank_in_band
""")

show("3. Daily on-time, early and late share, with change from the previous day", """
WITH daily AS (
    SELECT "date" AS day,
           COUNT(*) AS visits,
           ROUND(100.0 * AVG(CASE WHEN delay_sec BETWEEN -60 AND 300 THEN 1 ELSE 0 END), 1) AS pct_on_time,
           ROUND(100.0 * AVG(CASE WHEN delay_sec < -60 THEN 1 ELSE 0 END), 1) AS pct_early,
           ROUND(100.0 * AVG(CASE WHEN delay_sec > 300 THEN 1 ELSE 0 END), 1) AS pct_late
    FROM v
    GROUP BY "date"
)
SELECT day, visits, pct_on_time, pct_early, pct_late,
       ROUND(pct_on_time - LAG(pct_on_time) OVER (ORDER BY day), 1) AS change_vs_prev_day
FROM daily
ORDER BY day
""")
