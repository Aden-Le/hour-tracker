# Tzu Chi Hour Tracker

A web application for tracking event attendance and volunteer hours for Tzu Chi members. Built with Flask and Bootstrap 5, it runs locally in your browser — no internet connection required after setup.

---

## Table of Contents

- [Requirements](#requirements)
- [Setup (First Time)](#setup-first-time--any-computer)
- [Running the App](#running-the-app-after-setup)
- [Feature Guide](#feature-guide)
  - [File Manager](#file-manager-home-page)
  - [Data Table](#data-table)
  - [Add Event](#add-event)
  - [Edit Member](#edit-member)
  - [Edit Members (Bulk)](#edit-members-bulk)
  - [Hour Counter](#hour-counter)
  - [Family Leaderboard](#family-leaderboard)
  - [Settings](#settings)
- [CSV Format Reference](#csv-format-reference)
- [Troubleshooting](#troubleshooting)
- [Setting Up on a New Computer](#setting-up-on-a-new-computer)

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

The navigation bar at the top of every page provides links to all features. Menu items only appear after you select an active tracker file.

### File Manager (Home Page)

**Route:** `/`

The home page is your tracker file manager. All data is stored in `.csv` files in the project folder.

#### Select an existing tracker
- Click any file name to make it the active tracker.
- The active file is highlighted in green and displayed in the navbar as **Active: filename**.

#### Create a new tracker
- Enter a file name (e.g. `Spring_2026_Tracker`) in the text box and click **Create Tracker**.
- The `.csv` extension is added automatically.
- A blank tracker is created from the included template.

#### Upload a tracker
- Click **Upload CSV** and select a `.csv` file from your computer.
- The file is validated to ensure it has the correct column structure before being imported.
- Use this to import tracker files shared by other users.

#### Rename a tracker
- Click the pencil icon next to any file.
- Enter the new name in the modal dialog and click **Rename**.

#### Download a tracker
- Click the download icon next to any file to save it to your computer.
- Use this to share tracker data with others or create backups.

#### Delete a tracker
- Click the trash icon next to any file.
- A confirmation dialog will appear — this action is permanent.

---

### Data Table

**Route:** `/tracker`

Displays all members and their event data from the active tracker in a scrollable table.

#### Understanding the table layout
- **Row 1** = event type classifications (e.g. Volunteer, General Meeting)
- **Row 2** = event dates
- **Row 3 onward** = member data with hours per event

#### Sortable columns
- Click any column header (in the first 10 columns) to sort ascending or descending.
- The header stays fixed while you scroll horizontally through event columns.

#### Editing a member
- Click on any member row in the table to go directly to their edit page.

#### Adding events
- Click the **Add Event** button above the table.

#### Deleting events
- Click the **Delete Event** dropdown to select which event column to remove.
- A confirmation dialog appears before deletion.
- This action is permanent — use it to correct mistakes made during event entry.

---

### Add Event

**Route:** `/add-event`

Records attendance for a new event using a two-step flow: fill in details, then preview and confirm.

#### Step 1 — Event Details & Attendee Names

| Field | Description |
|---|---|
| **Event Name** | Name of the event (e.g. "Spring Volunteer Day") |
| **Specific Hours** | Checkbox — enable to assign different hours to each member |
| **Duration** | Hours the event lasted (0.5, 1, 1.5, 2, etc.). Hidden when Specific Hours is enabled. |
| **Date** | Date of the event using a date picker |
| **Event Type** | Select from configured event types (e.g. General Meeting, Volunteer, Social) |

##### Pasting names from Excel or Google Sheets

1. Open your attendance list in Excel or Google Sheets.
2. Select exactly **two columns**: **First Name** and **Last Name** (in that order).
3. Copy the selection (`Ctrl+C` / `Cmd+C`).
4. Click in the **Attendee Names** text box and paste (`Ctrl+V` / `Cmd+V`).

Your pasted data should look like this:
```
Dylan    Nguyen
Dylan    Le
Aden     Le
Zoe      Walker
```
Each row is one person. Columns are separated by a Tab character (this happens automatically when copying from spreadsheet apps).

- Names are automatically capitalized.
- Rows that don't have exactly two tab-separated columns are skipped (so header rows are ignored).
- If the same full name appears twice, you'll get an error — remove duplicates before submitting.

Click **Preview Event →** to continue.

#### Step 2 — Preview & Confirm

Review what will happen before saving:

- **Existing Members** (green card): People already in the tracker. The event hours will be recorded for them.
- **New Members** (yellow card): People not yet in the tracker. They will be added as **Member / NoFam**. You can edit their classification and family later.

##### Specific Hours mode
If you enabled Specific Hours in Step 1, a table appears with every attendee listed. You can:
- Enter custom hours for each member individually.
- Use the **"Set all to"** field to bulk-apply the same value to everyone.

Click **Confirm & Save** to finalize, **Go Back** to make changes, or **Cancel** to return to the data table.

---

### Edit Member

**Route:** `/edit-member/<row>`

Edit an individual member's details and event hours. Access this page by clicking a member's row in the Data Table.

#### Member info
- Displays the member's name, current classification, family, and events attended.

#### Change classification & family
- Use the dropdown menus to update their **Classification** (Officer, Junior Officer, Big Sib, Member) and/or **Family** (Kuromi, PomPom, Melody, NoFam).
- Click **Save Changes** to apply.

#### Edit event hours
- A table shows every event the member has attended (hours > 0).
- Each row shows the event name, type badge, date, and an editable hours field.
- Hours accept decimals in increments of 0.25 (e.g. 0.25, 0.5, 1.75).
- Set hours to **0** to remove the member from that event.
- Click **Save Hours** to apply changes.

#### Delete member
- Click the red **Delete Member** button in the danger zone at the bottom.
- A confirmation dialog will appear — this permanently removes the member and all their attendance data.

---

### Edit Members (Bulk)

**Route:** `/edit-members`

Quickly update classification and family assignments for multiple members at once.

- All members are displayed in an editable table.
- Each row has dropdown menus for **Classification** and **Family**.
- Click column headers to sort the table.
- Click **Save All Changes** to apply all modifications at once.

This is useful when onboarding a batch of new members who were all added as Member/NoFam during event entry.

---

### Hour Counter

**Route:** `/hours`

Filter members and calculate their total hours based on selected criteria.

#### Filters

| Filter | Options | Default |
|---|---|---|
| **Classification** | Officer, Junior Officer, Big Sib, Member | All checked |
| **Family** | Kuromi, PomPom, Melody, NoFam | All checked |
| **Event Type** | General Meeting, Officer Meeting, Tabling, Volunteer, Social, Retreat | All checked |
| **Show top N** | Number to limit results (0 = show everyone) | 0 |

Click **Calculate Hours** to run the filter.

#### Results
- Members are displayed in a ranked table with their name and total hours.
- Hours are shown to one decimal place.
- The total number of matching members is displayed.

#### Export to CSV
- After calculating, click **Export CSV** in the results header.
- Downloads a `hour_counter_results.csv` file with the filtered results that you can open in Excel.
- The export preserves your current filter selections.

---

### Family Leaderboard

**Route:** `/leaderboard`

Shows total hours per family, ranked from highest to lowest with visual progress bars.

- Select which event types to include using checkboxes (defaults to General Meeting, Volunteer, Social).
- Click **Show Leaderboard** to see results.
- Families are displayed with medal icons and color-coded bars:
  - 🥇 Gold bar for 1st place
  - 🥈 Silver bar for 2nd place
  - 🥉 Blue bar for 3rd place
- The **NoFam** group is excluded from the leaderboard automatically.
- Hours are shown to one decimal place.

---

### Settings

**Route:** `/settings`

Manage the configurable options used throughout the app. Changes are saved to `config.json` and apply globally to all tracker files.

#### Configurable sections

| Section | Description | Defaults |
|---|---|---|
| **Classifications** | Member role types | Officer, Junior Officer, Big Sib, Member |
| **Families** | Family group names | Kuromi, PomPom, Melody, NoFam |
| **Event Types** | Available event categories | General Meeting, Officer Meeting, Tabling, Volunteer, Social, Retreat |
| **Leaderboard Event Types** | Subset of event types used for the Family Leaderboard | General Meeting, Volunteer, Social |

#### Managing options
- Current items are displayed as badges with an **×** delete button.
- Type a new item name and click **Add** to create one.
- Changes take effect immediately across the app (dropdowns, filters, etc.).

---

## CSV Format Reference

The tracker CSV uses this column structure:

| Column | Description |
|---|---|
| First Name | Member's first name |
| Last Name | Member's last name |
| Class | Classification: Officer, Junior Officer, Big Sib, Member |
| Family | Family group: Kuromi, PomPom, Melody, NoFam |
| Total Hours | Auto-calculated total of all event hours |
| Volunteer Hours | Auto-calculated hours from Volunteer events only |
| General Meeting | Auto-calculated hours from General Meeting events |
| Tabling | Auto-calculated hours from Tabling events |
| Social | Auto-calculated hours from Social events |
| Banquet | Banquet qualification: Yes / No (requires 2+ volunteer events AND 1+ general meeting) |
| [Event columns...] | One column per event. Row 1 = event type, Row 2 = date, Row 3+ = hours per member |

**Notes:**
- The first two data rows in the CSV (after the header) contain event metadata (type and date), not member data.
- Members start at the third data row.
- You can open and edit the CSV directly in Excel — just don't add or remove columns manually unless you know the structure.

---

## Troubleshooting

**"File not found" error when opening the tracker:**
- The CSV file may have been moved or renamed outside the app.
- Go back to the File Manager and re-select or recreate the file.

**Names not parsing from Excel paste:**
- Make sure you copied exactly **two columns** (First Name, Last Name).
- Each row must be separated by a Tab character (this happens automatically when copying from Excel or Google Sheets).
- If you're typing names manually, separate first and last name with a Tab, not spaces.

**"Duplicate names detected" error:**
- Check your pasted list for the same full name appearing twice.
- Remove the duplicate and try again.

**Hour Counter shows 0 hours for everyone:**
- Make sure you have events added to the tracker.
- Check that the event types in your filter match the types of events you've added.

**Uploaded CSV rejected:**
- Ensure the file has the required columns: First Name, Last Name, Class, Family, Total Hours, Volunteer Hours, General Meeting, Tabling, Social, Banquet.
- The file must be a valid `.csv` format.

**App won't start:**
- Make sure you ran `pip install -r requirements.txt`.
- Make sure you're running Python 3.9 or newer (`python --version`).
- Make sure you're in the `hour-tracker` folder when running `python app.py`.

**Port already in use:**
- Another process is using port 5000. Either stop that process, or start Flask on a different port:
  ```bash
  python -c "from app import app; app.run(port=5001, debug=True)"
  ```
  Then open http://localhost:5001.

---

## Setting Up on a New Computer

1. Install Python 3.9+ if not already installed.
2. Clone or download this repository.
3. Open a terminal in the `hour-tracker` folder.
4. Run `pip install -r requirements.txt`.
5. Run `python app.py`.
6. Open http://localhost:5000.

Your CSV tracker files stay on your local computer — they are not synced or uploaded anywhere. To share data between computers, use the **Download** feature to export your `.csv` files and the **Upload** feature to import them on the other machine. You can also store the project in a shared folder (e.g. Google Drive, OneDrive) and run the app from there.
