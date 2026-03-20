# Tzu Chi Hour Tracker

A web application for tracking event attendance and volunteer hours for Tzu Chi members. Runs locally in your browser — no internet connection required after setup.

---

## Requirements

- **Python 3.9 or newer** — [Download Python](https://www.python.org/downloads/)
- **pip** (comes with Python)
- A modern web browser (Chrome, Firefox, Edge, Safari)

---

## Setup (First Time — Any Computer)

### 1. Clone the repository

```bash
git clone https://github.com/Aden-Le/hour-tracker.git
cd hour-tracker
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

This installs Flask and pandas. Only needs to be done once.

### 3. Start the app

```bash
python app.py
```

You should see output like:

```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### 4. Open your browser

Go to: **http://localhost:5000**

---

## Running the App (After Setup)

Every time you want to use the tracker:

```bash
cd hour-tracker
python app.py
```

Then open **http://localhost:5000** in your browser.

To stop the app, press `Ctrl+C` in the terminal.

---

## Feature Guide

### File Manager (Home Page `/`)

The home page is your tracker file manager. All your data is stored in `.csv` files in the project folder.

**Select an existing tracker:**
- Click any file name to make it the active tracker.
- The active file is shown in green and displayed in the top navbar.

**Create a new tracker:**
- Enter a file name (e.g. `2025_2026_Tracker`) in the text box and click **Create Tracker**.
- The `.csv` extension is added automatically.
- A blank tracker file is created from the included `template.csv`.

**Rename a tracker:**
- Click the ✏️ pencil icon next to any file.
- Enter the new name and click **Rename**.

---

### Data Table (`/tracker`)

Displays all members and their event data from the active tracker CSV.

- **Row 1** of the data = event classifications (e.g. Volunteer, General Meeting)
- **Row 2** = event dates
- **Row 3 onward** = member data

**Delete Last Event:**
- Click the red **Delete Last Event** button to remove the most recently added event column.
- A confirmation dialog will appear before anything is deleted.
- ⚠️ This action is permanent — use it to correct mistakes made during event entry.

---

### Add Event (`/add-event`)

Records attendance for a new event. Uses a two-step flow: fill in details → preview → confirm.

#### Step 1 — Event Details & Names

**Event fields:**
| Field | Description |
|---|---|
| Event Name | Name of the event (e.g. "Spring Volunteer Day") |
| Duration | How long the event was in hours (0.5, 1, 1.5, 2, etc.) |
| Date | Date of the event (e.g. 03/15/2025) |
| Event Type | Select from: General Meeting, Officer Meeting, Tabling, Volunteer, Social, Retreat |

**Pasting names from Excel:**

1. Open your Excel/Google Sheets attendance list.
2. Select **two columns**: **First Name** and **Last Name** (in that order).
3. Copy the selection (`Ctrl+C` / `Cmd+C`).
4. Click in the **Attendee Names** text box and paste (`Ctrl+V` / `Cmd+V`).

Your pasted data should look like this in the text box:
```
Dylan    Nguyen
Dylan    Le
Aden     Le
Zoe      Walker
```
(Each row is one person, columns are separated by a Tab character from Excel.)

- Names are automatically capitalized.
- You do not need to remove a header row — rows that don't have two tab-separated columns are skipped.
- If the same full name appears twice, you'll get an error — remove duplicates before submitting.

Click **Preview Event →** to continue.

#### Step 2 — Preview & Confirm

Review what will happen:

- **Existing Members** (green): People already in the tracker. This event will be recorded for them.
- **New Members** (yellow): People not yet in the tracker. They will be added as **Member / NoFam**. You can edit their classification and family later.

Click **Confirm & Save** to finalize, or **Go Back** to make changes.

---

### Hour Counter (`/hours`)

Filter members and calculate their total hours.

**Filters:**
- **Classification**: Check any combination of Officer, Junior Officer, Big Sib, Member (defaults to all).
- **Family**: Check any combination of Kuromi, PomPom, Melody, NoFam (defaults to all).
- **Event Type**: Check any combination of event types (defaults to all).
- **Show top N**: Enter a number to only show the top N members by hours. Leave at 0 to show everyone.

Click **Calculate Hours** to run the filter.

**Export Results:**
- After calculating, click **⬇ Export CSV** in the results header.
- Downloads a `hour_counter_results.csv` file you can open in Excel.

---

### Family Leaderboard (`/leaderboard`)

Shows total hours per family (Kuromi, PomPom, Melody), sorted highest to lowest.

- Check which event types to include (General Meeting, Volunteer, Social).
- Click **Show Leaderboard** to see the results with a visual progress bar.

---

### Edit Member (`/edit-member/<row>`)

Change a member's classification or family assignment.

To find a member's row number:
1. Go to the **Data Table**.
2. Members start at row 0 (the first data row after the two metadata rows).
3. Navigate to `/edit-member/0` for the first member, `/edit-member/1` for the second, etc.

Update their **Classification** (Officer, Junior Officer, Big Sib, Member) and/or **Family** (Kuromi, PomPom, Melody, NoFam), then click **Save Changes**.

---

## CSV Format Reference

The tracker CSV uses this column structure:

| Column | Description |
|---|---|
| First Name | Member's first name |
| Last Name | Member's last name |
| Class | Classification: Officer, Junior Officer, Big Sib, Member |
| Family | Family: Kuromi, PomPom, Melody, NoFam |
| Total Hours | Auto-calculated total hours |
| Volunteer Hours | Auto-calculated volunteer hours |
| General Meeting | Auto-calculated general meeting hours |
| Tabling | Auto-calculated tabling hours |
| Social | Auto-calculated social hours |
| Banquet | Banquet qualification: Yes / No (requires 2+ volunteer events AND 1+ general meeting) |
| [Event columns...] | One column per event. Row 1 = event type, Row 2 = date, Row 3+ = hours attended |

**Notes:**
- The first two data rows in the CSV (after the header) contain event metadata (classification and date), not member data.
- Members start at the third data row (CSV row index 2).
- You can open and edit the CSV directly in Excel — just don't add/remove columns manually unless you know the structure.

---

## Troubleshooting

**"File not found" error when opening the tracker:**
- The CSV file may have been moved or renamed outside the app.
- Go back to the File Manager and re-select or recreate the file.

**Names not parsing from Excel paste:**
- Make sure you copied exactly **two columns** (First Name, Last Name).
- Each row must be separated by a Tab character (this happens automatically when copying from Excel).
- If you're copying from Google Sheets, it also uses tabs when copying multiple columns — should work the same.

**"Duplicate names detected" error:**
- Check your pasted list for the same full name appearing twice.
- Remove the duplicate and try again.

**Hour Counter shows 0 hours for everyone:**
- Make sure you have events added to the tracker.
- Check that the event types in the filter match the types of events you've added.

**App won't start:**
- Make sure you ran `pip install -r requirements.txt`.
- Make sure you're running Python 3.9 or newer (`python --version`).
- Make sure you're in the `hour-tracker` folder when running `python app.py`.

**Port already in use:**
- Another process is using port 5000. Either stop that process, or start Flask on a different port:
  ```bash
  python -c "from app import app; app.run(port=5001, debug=True)"
  ```
  Then open http://localhost:5001

---

## Setting Up on a New Computer

1. Install Python 3.9+ if not already installed.
2. Clone or download this repository.
3. Open a terminal in the `hour-tracker` folder.
4. Run `pip install -r requirements.txt`.
5. Run `python app.py`.
6. Open http://localhost:5000.

Your CSV tracker files stay on your local computer — they are not synced or uploaded anywhere. To share data between computers, copy the `.csv` files manually or use a shared folder (e.g. Google Drive, OneDrive) and run the app from that folder.

---

## CLI Usage (Original Terminal Interface)

The original command-line interface is still available:

```bash
python main.py
```

This requires `2025_2026_Main_Tracker.csv` and `names.csv` to exist in the folder.
