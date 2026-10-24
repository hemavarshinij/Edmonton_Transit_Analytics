# Findings log (as of Sat 24 Oct 2026, data from Mon 19 Oct to Sat 24 Oct)

## Method decisions
- Readings at stops 1 to 3 were 26% of readings but 5% of stop visits (buses waiting at the start of the trip).
- Analysis unit: one reading per trip and stop (the last before the bus reached the stop). 56,585 readings became 23,844 stop visits.

## Headline findings (draft, to be re-checked with Sunday and Monday data)
1. Early running dominates: 61.6% of stop visits were more than 1 minute early; 4.3% were more than 5 minutes late. Early share was 59 to 65% on every weekday.
2. Lateness is concentrated: the top 10 routes produce 54.2% of late visits. Route 052 (Northgate to West Edmonton Mall) is 34.9% late and is in the top 3 in three of four parts of the day.
3. Rush-hour routes: 700X late in the morning peak (57.1%, 42 visits); 560 and 110X in the afternoon peak (80.5% and 60.5%, under 42 visits each). Small samples.

## Data quality
- Gaps: 362 min on Wed 21 Oct (14:09 to 20:11 Edmonton), 6 min on Fri 23 Oct.
- 2,452 duplicate rows with blank trip_id dropped (early run).
- About 44% of live trips match the portal timetable; cause unresolved.
- About 1% of snapshots had one corrupt feed message.
- Each trip appears at about one stop (23,844 stop visits over 23,356 trip instances), so delay build-up along a trip can't be analysed.
