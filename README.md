# Moodle to Google Calendar Sync

## Table of Contents

1.  [Introduction](#introduction)
2.  [Getting Started](#getting-started)
    -   [Prerequisites](#prerequisites)
    -   [Installation](#installation)
3.  [Usage](#usage)
    -   [Getting Your Moodle Calendar Link](#getting-your-moodle-calendar-link)
    -   [Setting Up the Google Service Account](#setting-up-the-google-service-account)
    -   [Configuring the .env File](#configuring-the-env-file)
    -   [Running the Program](#running-the-program)
    -   [Running It Automatically with GitHub Actions](#running-it-automatically-with-github-actions)
    -   [What Gets Copied to Google Calendar](#what-gets-copied-to-google-calendar)
4.  [Important Notes](#important-notes)
5.  [Directory Structure](#directory-structure)
6.  [Design Decisions](#design-decisions)
7.  [Contributions and Feedback](#contributions-and-feedback)

## 1. Introduction <a name="introduction"></a>

The Moodle to Google Calendar Sync is a Python program that copies the deadlines and events from my university platform into Google Calendar. It downloads the Moodle feed, reads each event, and then creates or updates the matching event in Google Calendar. It is built with the `requests` and `icalendar` libraries, the Google Calendar API, and GitHub Actions for the daily schedule.

## 2. Getting Started <a name="getting-started"></a>

### Prerequisites <a name="prerequisites"></a>

Before you begin, make sure you have the following:

-   Python 3.x
-   A Moodle account where the calendar can be exported
-   A Google account with access to Google Calendar and Google Cloud Console
-   A GitHub account (only needed if you want the daily automatic run)

### Installation <a name="installation"></a>

Follow these steps to set up the project:

1.  Clone or download this repository to your local machine.

2.  Open a terminal and navigate to the project directory.

3.  Create and activate a virtual environment (optional, but recommended):

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

4.  Install the required packages by running:

    ```bash
    pip install -r requirements.txt
    ```

## 3. Usage <a name="usage"></a>

### Getting Your Moodle Calendar Link <a name="getting-your-moodle-calendar-link"></a>

1. Log in to Moodle and open the Calendar page.
2. Choose "Import or export calendars", then "Export calendar".
3. Select "All events" and pick the longest time period available.
4. Click "Get calendar URL" and copy the link.

Keep this link private. Anyone who has it can see your calendar.

### Setting Up the Google Service Account <a name="setting-up-the-google-service-account"></a>

The program signs in to Google as a service account, which is a separate robot identity that belongs to the program and not to a person.

1. In Google Cloud Console, create a project and enable the Google Calendar API.
2. Create a service account, then open its "Keys" tab and create a new JSON key.
3. Save the downloaded key in the project folder with the name `service_account.json`.
4. In Google Calendar, create a new calendar (for example, "Uni").
5. Open that calendar's settings, share it with the service account's email address, and give it the permission "Make changes to events".
6. In the same settings page, copy the Calendar ID from the "Integrate calendar" section.

### Configuring the .env File <a name="configuring-the-env-file"></a>

Create a file named `.env` in the project folder and provide your details in the following format:

```
MOODLE_ICS_URL=your-moodle-link
CALENDAR_ID=your-calendar-id
TIMEZONE=Europe/London
```

Replace `Europe/London` with your own time zone name. Do not put quote marks around the values.

### Running the Program <a name="running-the-program"></a>

To run the sync, execute the following command:

```bash
python sync.py
```

The program will download your Moodle calendar, sign in as the service account, and add or update each event in your Google Calendar. At the end it prints a short summary, for example `Added: 1 | Updated: 2`.

### Running It Automatically with GitHub Actions <a name="running-it-automatically-with-github-actions"></a>

The workflow in `.github/workflows/sync.yml` runs the sync every day at 06:00 UTC. To use it, add the following four secrets in your repository under Settings, then Secrets and variables, then Actions:

1. `MOODLE_ICS_URL`: Your Moodle calendar link.
2. `CALENDAR_ID`: The ID of your Google calendar.
3. `TIMEZONE`: Your time zone name, such as `Europe/London`.
4. `GOOGLE_SERVICE_ACCOUNT_JSON`: The full contents of your `service_account.json` file.

You can also start the workflow by hand from the Actions tab by clicking "Run workflow". The log of each run shows the same summary line that the program prints on your own computer.

### What Gets Copied to Google Calendar <a name="what-gets-copied-to-google-calendar"></a>

Each Moodle event is converted into a Google Calendar event with the following details:

1.  `Title`: The name of the event as it appears in Moodle.
2.  `Start`: The start date and time. If Moodle does not attach a time zone, the one from your `.env` file is used.
3.  `End`: The end date and time. Many deadlines have no end time, so the program gives them a default length of 30 minutes. All-day events are given a length of one day.
4.  `Description`: The extra details that Moodle stores with the event.

## 4. Important Notes <a name="important-notes"></a>

- You can run the program as many times as you like. Each event is matched by a permanent ID, so existing events are updated and no duplicates are created.
- The program can only see deadlines that exist as real entries in the Moodle calendar. If a lecturer writes a deadline in a PDF or an announcement, Moodle does not turn it into a calendar event, so the program cannot find it.
- The program does not delete events yet. If a deadline is removed from Moodle, the matching event stays in Google Calendar until it is deleted by hand.
- Never upload your `.env` file or `service_account.json` file. Both are listed in `.gitignore` to prevent this.
- Scheduled runs on GitHub can start a few minutes late. GitHub may also pause scheduled workflows in a repository that has had no activity for a long time, so check the Actions tab if the calendar stops updating.

## 5. Directory Structure <a name="directory-structure"></a>

-   `sync.py`: The main program that downloads the Moodle calendar and updates Google Calendar.
-   `google_auth.py`: Handles signing in to Google as the service account.
-   `config.py`: Loads the settings from the `.env` file or from environment variables.
-   `requirements.txt`: The list of Python libraries the project needs.
-   `.gitignore`: Lists the files that must never be uploaded, such as the `.env` file and the service account key.
-   `.github/workflows/sync.yml`: The GitHub Actions workflow that runs the sync every day.

## 6. Design Decisions <a name="design-decisions"></a>

**Avoiding duplicates.** Every Moodle event has a permanent unique ID. The program turns that ID into a hash and uses it as the Google event ID. It then tries to insert the event, and if Google reports that an event with that ID already exists, it updates the existing one instead.

**Using a service account.** I first built this with a normal Google login, but that approach had two problems. While a Google project is in testing mode, the permission expires after about a week, which would break the automation. Publishing the project to avoid this would have required a public home page and privacy policy for a personal script. A service account avoids both problems, because it never expires and does not need a browser to log in. It can also only reach the one calendar that was shared with it, so a bug cannot touch the rest of the Google account.

**A dedicated calendar.** The events go into their own calendar and not the main one. If something goes wrong, that calendar can be deleted and recreated without losing anything else.

**Keeping secrets out of the code.** The Moodle link, the calendar ID, and the service account key are never written into the code. Locally they are read from the `.env` file and the key file, and in the cloud they are read from GitHub Secrets.

## 7. Contributions and Feedback <a name="contributions-and-feedback"></a>

Suggestions for improvements and bug reports are always welcome. A useful next step would be to delete events from Google Calendar when they are removed from Moodle.