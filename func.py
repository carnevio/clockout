from pydantic import BaseModel
from datetime import datetime, timedelta
import isodate

class Item(BaseModel):
    string: list[datetime]
    lunch_time: timedelta | None = None
    target: timedelta | None = None
# Example
#    {
#  "string": ["2026-01-22T12:14:00+01:00","2026-01-22T11:31:00+01:00","2026-01-22T07:41:00+01:00"],
#  "lunch_time": "P0Y0M0DT0H30M0S",
#  "target": "P0Y0M0DT8H0M0S"
#    }


async def get_end_times(time_list: list[datetime], lunch_time: timedelta | None = None, target: timedelta | None = None):
    # Differenz berechnen
    times = []
    for i in time_list:
        times.append(datetime.fromisoformat(i))
    lunch_time = isodate.parse_duration(lunch_time)
    target = isodate.parse_duration(target)
    # Lunch time berechnen
    pause = timedelta()
    for j in range(1, len(times)-1, 2):
        pause += times[j-1] - times[j]

    if pause > lunch_time:
        lunch_time = pause
    print(f"Pause: {lunch_time}, Zielzeit: {target}, Zeiten: {times[-1]}")
    end_time = times[-1] + target + lunch_time
    return end_time