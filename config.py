import os

from dotenv import load_dotenv

load_dotenv()

MOODLE_ICS_URL = os.environ["MOODLE_ICS_URL"]
CALENDAR_ID = os.environ["CALENDAR_ID"]
TIMEZONE = os.environ.get("TIMEZONE", "Europe/London")