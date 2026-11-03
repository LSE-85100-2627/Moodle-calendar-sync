import hashlib
from datetime import datetime, timedelta

import requests
from icalendar import Calendar
from googleapiclient.errors import HttpError

from config import MOODLE_ICS_URL, CALENDAR_ID, TIMEZONE
from google_auth import get_calendar_service


def make_event_id(uid):
    return hashlib.sha1(uid.encode()).hexdigest()


def to_google_time(value):
    if isinstance(value, datetime):
        result = {"dateTime": value.isoformat()}
        if value.tzinfo is None:
            result["timeZone"] = TIMEZONE
        return result
    return {"date": value.isoformat()}


def build_google_event(event):
    start = event.get("DTSTART").dt
    end_property = event.get("DTEND")
    end = end_property.dt if end_property else start

    if end <= start:
        if isinstance(start, datetime):
            end = start + timedelta(minutes=30)
        else:
            end = start + timedelta(days=1)

    return {
        "id": make_event_id(str(event.get("UID"))),
        "summary": str(event.get("SUMMARY", "Untitled")),
        "description": str(event.get("DESCRIPTION", "")),
        "start": to_google_time(start),
        "end": to_google_time(end),
    }


def main():
    response = requests.get(MOODLE_ICS_URL)
    response.raise_for_status()
    calendar = Calendar.from_ical(response.content)

    service = get_calendar_service()

    added = 0
    updated = 0

    for event in calendar.walk("VEVENT"):
        body = build_google_event(event)
        try:
            service.events().insert(calendarId=CALENDAR_ID, body=body).execute()
            added += 1
        except HttpError as error:
            if error.resp.status == 409:
                service.events().update(
                    calendarId=CALENDAR_ID, eventId=body["id"], body=body
                ).execute()
                updated += 1
            else:
                raise

    print("Added:", added, "| Updated:", updated)


main()