import requests
from icalendar import Calendar

from config import MOODLE_ICS_URL

response = requests.get(MOODLE_ICS_URL)
response.raise_for_status()

calendar = Calendar.from_ical(response.content)

for event in calendar.walk("VEVENT"):
    title = event.get("SUMMARY")
    start = event.get("DTSTART").dt
    print(title, "|", start)