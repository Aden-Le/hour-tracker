import os
import io
import json
from collections import defaultdict
from datetime import datetime
from glob import glob

import pandas as pd
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, send_file
)

from deprecated.main import process_main_tracker, apply_event, hour_counter, saver, Student

app = Flask(__name__)
app.secret_key = 'tzu-chi-hour-tracker-secret'

TEMPLATE_FILE = 'blank_template.csv'
CONFIG_FILE = 'config.json'

DEFAULT_CONFIG = {
    "classifications": ["Officer", "Junior Officer", "Big Sib", "Member"],
    "families": ["Kuromi", "PomPom", "Melody", "NoFam"],
    "event_types": ["General Meeting", "Officer Meeting", "Tabling", "Volunteer", "Social", "Retreat"],
    "leaderboard_event_types": ["General Meeting", "Volunteer", "Social"],
}


def load_config():
    """Load configuration from config.json, creating it with defaults if missing."""
    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    save_config(DEFAULT_CONFIG)
    return dict(DEFAULT_CONFIG)


def save_config(cfg):
    """Write configuration to config.json."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=2)


def get_all_classes():
    return load_config()["classifications"]


def get_all_families():
    return load_config()["families"]


def get_all_event_types():
    return load_config()["event_types"]


def get_leaderboard_event_types():
    return load_config()["leaderboard_event_types"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_tracker_file():
    """Return the currently selected tracker CSV filename, or None."""
    return session.get('tracker_file')


def load_data(tracker_file):
    """Load event_data and student_data from the given CSV file."""
    return process_main_tracker(tracker_file)


def list_csv_files():
    """Return all *.csv files in the working directory (excluding template/blank/example)."""
    skip = {'template.csv', 'blank_template.csv', 'blank.csv', 'example.csv', 'names.csv'}
    files = [os.path.basename(f) for f in glob('*.csv')]
    return [f for f in sorted(files) if f not in skip]


def parse_pasted_names(text):
    """Parse pasted names (tab-separated or space-separated) into two lists.
    Handles Excel copy-paste (First\tLast), trailing spaces, and space-only separators."""
    first_names, last_names = [], []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        # Try tab-separated first (standard Excel copy), fall back to any whitespace
        if '\t' in line:
            parts = [p.strip() for p in line.split('\t')]
        else:
            parts = line.split(None, 1)  # split on any whitespace, max 2 parts
        if len(parts) >= 2:
            f = parts[0].strip().capitalize()
            l = parts[1].strip().capitalize()
            if f and l:
                first_names.append(f)
                last_names.append(l)
    return first_names, last_names


def safe_load_table_html(tracker_file):
    """Return a Bootstrap-styled HTML table string from the CSV, or an error message."""
    try:
        df = pd.read_csv(tracker_file, dtype=str).fillna('')
        # Strip pandas duplicate suffixes (.1, .2, …) so display names stay clean
        import re
        df.columns = [re.sub(r'\.\d+$', '', col) for col in df.columns]
        html = df.to_html(
            classes='table table-sm table-striped table-hover table-bordered',
            border=0,
            index=False,
        )
        return html
    except Exception as e:
        return f'<p class="text-danger">Could not load table: {e}</p>'


# ---------------------------------------------------------------------------
# File Manager Routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    csv_files = list_csv_files()
    active = get_tracker_file()
    return render_template('index.html', csv_files=csv_files, active=active)


@app.route('/select-file', methods=['POST'])
def select_file():
    filename = request.form.get('filename', '').strip()
    if not filename or not os.path.isfile(filename):
        flash(f'File "{filename}" not found.', 'danger')
        return redirect(url_for('index'))
    session['tracker_file'] = filename
    return redirect(url_for('tracker'))


@app.route('/new-file', methods=['POST'])
def new_file():
    name = request.form.get('filename', '').strip()
    if not name:
        flash('Please enter a file name.', 'danger')
        return redirect(url_for('index'))
    if not name.endswith('.csv'):
        name += '.csv'
    if os.path.isfile(name):
        flash(f'"{name}" already exists. Choose a different name.', 'danger')
        return redirect(url_for('index'))
    import shutil
    shutil.copy(TEMPLATE_FILE, name)
    session['tracker_file'] = name
    flash(f'Created new tracker: {name}', 'success')
    return redirect(url_for('tracker'))


@app.route('/rename-file', methods=['POST'])
def rename_file():
    old_name = request.form.get('old_name', '').strip()
    new_name = request.form.get('new_name', '').strip()
    if not new_name.endswith('.csv'):
        new_name += '.csv'
    if not os.path.isfile(old_name):
        flash(f'File "{old_name}" not found.', 'danger')
        return redirect(url_for('index'))
    if os.path.isfile(new_name):
        flash(f'"{new_name}" already exists.', 'danger')
        return redirect(url_for('index'))
    os.rename(old_name, new_name)
    if session.get('tracker_file') == old_name:
        session['tracker_file'] = new_name
    flash(f'Renamed "{old_name}" → "{new_name}"', 'success')
    return redirect(url_for('index'))


@app.route('/upload-file', methods=['POST'])
def upload_file():
    uploaded = request.files.get('file')
    if not uploaded or uploaded.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('index'))
    filename = uploaded.filename.strip()
    if not filename.endswith('.csv'):
        flash('Only CSV files are allowed.', 'danger')
        return redirect(url_for('index'))
    # Sanitise: keep only the basename to prevent path traversal
    filename = os.path.basename(filename)
    if os.path.isfile(filename):
        flash(f'"{filename}" already exists. Rename it first or delete the existing file.', 'danger')
        return redirect(url_for('index'))
    # Validate CSV format before saving
    try:
        content = uploaded.read()
        df = pd.read_csv(io.BytesIO(content), dtype=str, nrows=0)
        expected = ['First Name', 'Last Name', 'Class', 'Family', 'Total Hours',
                    'Volunteer Hours', 'General Meeting', 'Tabling', 'Social', 'Banquet']
        actual = list(df.columns[:10])
        if actual != expected:
            flash(f'Invalid tracker format. Expected columns: {", ".join(expected)}. '
                  f'Got: {", ".join(actual)}.', 'danger')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Could not read CSV file: {e}', 'danger')
        return redirect(url_for('index'))

    with open(filename, 'wb') as f:
        f.write(content)
    session['tracker_file'] = filename
    flash(f'Uploaded and selected "{filename}".', 'success')
    return redirect(url_for('index'))


@app.route('/download-file/<path:filename>')
def download_file(filename):
    filename = os.path.basename(filename)
    if not os.path.isfile(filename):
        flash(f'File "{filename}" not found.', 'danger')
        return redirect(url_for('index'))
    return send_file(filename, mimetype='text/csv',
                     as_attachment=True, download_name=filename)


@app.route('/delete-file', methods=['POST'])
def delete_file():
    filename = request.form.get('filename', '').strip()
    if not filename or not os.path.isfile(filename):
        flash(f'File "{filename}" not found.', 'danger')
        return redirect(url_for('index'))
    os.remove(filename)
    if session.get('tracker_file') == filename:
        session.pop('tracker_file', None)
    flash(f'Deleted "{filename}".', 'success')
    return redirect(url_for('index'))


# ---------------------------------------------------------------------------
# Tracker (Data Table)
# ---------------------------------------------------------------------------

@app.route('/tracker')
def tracker():
    tf = get_tracker_file()
    if not tf:
        flash('Please select or create a tracker file first.', 'warning')
        return redirect(url_for('index'))
    if not os.path.isfile(tf):
        flash(f'Tracker file "{tf}" not found.', 'danger')
        session.pop('tracker_file', None)
        return redirect(url_for('index'))
    table_html = safe_load_table_html(tf)
    event_data, student_data = load_data(tf)
    events = [(i, e.name, e.classification, e.date) for i, e in enumerate(event_data)]
    return render_template('tracker.html', table_html=table_html, tracker_file=tf, events=events)


# ---------------------------------------------------------------------------
# Add Event (two-step)
# ---------------------------------------------------------------------------

@app.route('/add-event', methods=['GET', 'POST'])
def add_event():
    tf = get_tracker_file()
    if not tf:
        flash('Please select a tracker file first.', 'warning')
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('add_event.html', event_types=get_all_event_types())

    # POST — validate and store in session
    event_name = request.form.get('event_name', '').strip()
    event_duration = request.form.get('event_duration', '').strip()
    event_date_raw = request.form.get('event_date', '').strip()
    event_type = request.form.get('event_type', '').strip()
    specific_hours = bool(request.form.get('specific_hours'))

    # Convert YYYY-MM-DD from date picker to MM/DD/YYYY for storage
    event_date = event_date_raw
    if event_date_raw:
        try:
            event_date = datetime.strptime(event_date_raw, '%Y-%m-%d').strftime('%m/%d/%Y')
        except ValueError:
            pass  # keep as-is if already in another format

    errors = []
    if not event_name:
        errors.append('Event name is required.')
    if not event_date:
        errors.append('Event date is required.')
    if event_type not in get_all_event_types():
        errors.append('Please select a valid event type.')
    if not specific_hours:
        try:
            float(event_duration)
        except (ValueError, TypeError):
            errors.append('Duration must be a number (e.g. 1, 1.5, 2).')

    pasted = request.form.get('names_paste', '').strip()
    if not pasted:
        errors.append('Please paste attendee names from Excel.')
    first_names, last_names = parse_pasted_names(pasted) if pasted else ([], [])
    if pasted and not first_names:
        errors.append('Could not parse any names. Make sure you copied two columns (First Name, Last Name) from Excel.')

    if errors:
        return render_template('add_event.html', event_types=get_all_event_types(),
                               errors=errors,
                               event_name=event_name, event_duration=event_duration,
                               event_date=event_date_raw, event_type=event_type,
                               names_paste=pasted, specific_hours=specific_hours)

    session['pending_event'] = {
        'name': event_name,
        'duration': event_duration,
        'date': event_date,
        'type': event_type,
        'specific_hours': specific_hours,
    }
    session['pending_first'] = first_names
    session['pending_last'] = last_names
    return redirect(url_for('add_event_confirm'))


@app.route('/add-event/confirm', methods=['GET', 'POST'])
def add_event_confirm():
    tf = get_tracker_file()
    pending = session.get('pending_event')
    if not tf or not pending:
        return redirect(url_for('add_event'))

    first_names = session.get('pending_first', [])
    last_names = session.get('pending_last', [])

    event_data, student_data = load_data(tf)
    existing_pairs = {(s.first_name, s.last_name) for s in student_data}
    incoming_pairs = list(zip(first_names, last_names))

    matched = [f"{f} {l}" for f, l in incoming_pairs if (f, l) in existing_pairs]
    new_people = [f"{f} {l}" for f, l in incoming_pairs if (f, l) not in existing_pairs]
    all_attendees = [f"{f} {l}" for f, l in incoming_pairs]
    specific_hours = pending.get('specific_hours', False)

    if request.method == 'GET':
        return render_template('add_event_confirm.html',
                               pending=pending,
                               matched=matched,
                               new_people=new_people,
                               specific_hours=specific_hours,
                               all_attendees=all_attendees)

    # POST — execute apply_event + saver
    if len(incoming_pairs) != len(set(incoming_pairs)):
        flash('ERROR: Duplicate names detected in the attendee list. Remove duplicates and try again.', 'danger')
        return redirect(url_for('add_event'))

    # Collect per-member hours if in specific_hours mode
    member_hours = None
    if specific_hours:
        member_hours = {}
        errors = []
        for idx, (f, l) in enumerate(incoming_pairs):
            val = request.form.get(f'member_hours_{idx}', '').strip()
            try:
                hrs = float(val)
                if hrs < 0:
                    errors.append(f'{f} {l}: hours cannot be negative.')
                else:
                    member_hours[(f, l)] = str(hrs)
            except (ValueError, TypeError):
                errors.append(f'{f} {l}: invalid hours value "{val}".')
        if errors:
            flash('Please fix hour values: ' + '; '.join(errors), 'danger')
            return render_template('add_event_confirm.html',
                                   pending=pending,
                                   matched=matched,
                                   new_people=new_people,
                                   specific_hours=specific_hours,
                                   all_attendees=all_attendees)

    try:
        new_student_data, new_event_data = apply_event(
            student_data, event_data,
            pending['name'], pending['type'], pending['date'], pending['duration'],
            list(first_names), list(last_names),
            member_hours=member_hours
        )
    except ValueError as e:
        flash(f'ERROR: {e}', 'danger')
        return redirect(url_for('add_event'))

    saver(new_student_data, new_event_data, tf)
    session.pop('pending_event', None)
    session.pop('pending_first', None)
    session.pop('pending_last', None)
    flash(f'Event "{pending["name"]}" added and saved successfully!', 'success')
    return redirect(url_for('tracker'))


# ---------------------------------------------------------------------------
# Hour Counter
# ---------------------------------------------------------------------------

@app.route('/hours', methods=['GET', 'POST'])
def hours():
    tf = get_tracker_file()
    if not tf:
        flash('Please select a tracker file first.', 'warning')
        return redirect(url_for('index'))

    results = None
    selected_classes = get_all_classes()[:]
    selected_families = get_all_families()[:]
    selected_events = get_all_event_types()[:]
    top_n = 0

    if request.method == 'POST':
        selected_classes = request.form.getlist('classification') or get_all_classes()[:]
        selected_families = request.form.getlist('family') or get_all_families()[:]
        selected_events = request.form.getlist('event_type') or get_all_event_types()[:]
        try:
            top_n = int(request.form.get('top_n', 0))
        except ValueError:
            top_n = 0

        event_data, student_data = load_data(tf)
        member_times = hour_counter(selected_classes, selected_families, selected_events,
                                    student_data, event_data)
        sorted_times = sorted(member_times.items(), key=lambda x: x[1], reverse=True)
        if top_n > 0:
            sorted_times = sorted_times[:top_n]
        results = sorted_times

    return render_template('hour_counter.html',
                           all_classes=get_all_classes(),
                           all_families=get_all_families(),
                           all_event_types=get_all_event_types(),
                           selected_classes=selected_classes,
                           selected_families=selected_families,
                           selected_events=selected_events,
                           top_n=top_n,
                           results=results)


@app.route('/hours/export', methods=['POST'])
def hours_export():
    tf = get_tracker_file()
    if not tf:
        flash('Please select a tracker file first.', 'warning')
        return redirect(url_for('index'))

    selected_classes = request.form.getlist('classification') or get_all_classes()[:]
    selected_families = request.form.getlist('family') or get_all_families()[:]
    selected_events = request.form.getlist('event_type') or get_all_event_types()[:]
    try:
        top_n = int(request.form.get('top_n', 0))
    except ValueError:
        top_n = 0

    event_data, student_data = load_data(tf)
    member_times = hour_counter(selected_classes, selected_families, selected_events,
                                student_data, event_data)
    sorted_times = sorted(member_times.items(), key=lambda x: x[1], reverse=True)
    if top_n > 0:
        sorted_times = sorted_times[:top_n]

    df = pd.DataFrame(sorted_times, columns=['Name', 'Hours'])
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return send_file(buf, mimetype='text/csv',
                     as_attachment=True, download_name='hour_counter_results.csv')


# ---------------------------------------------------------------------------
# Family Leaderboard
# ---------------------------------------------------------------------------

@app.route('/leaderboard', methods=['GET', 'POST'])
def leaderboard():
    tf = get_tracker_file()
    if not tf:
        flash('Please select a tracker file first.', 'warning')
        return redirect(url_for('index'))

    results = None
    selected_events = get_leaderboard_event_types()[:]

    if request.method == 'POST':
        selected_events = request.form.getlist('event_type') or get_leaderboard_event_types()[:]
        event_data, student_data = load_data(tf)

        families = {}
        for fam in get_all_families():
            if fam == 'NoFam':
                continue
            times = hour_counter(get_all_classes(), [fam], selected_events, student_data, event_data)
            families[f'{fam} Family'] = round(sum(times.values()), 2)

        results = sorted(families.items(), key=lambda x: x[1], reverse=True)

    return render_template('leaderboard.html',
                           leaderboard_event_types=get_leaderboard_event_types(),
                           selected_events=selected_events,
                           results=results)


# ---------------------------------------------------------------------------
# Edit Members (bulk table)
# ---------------------------------------------------------------------------

@app.route('/edit-members', methods=['GET', 'POST'])
def edit_members():
    tf = get_tracker_file()
    if not tf:
        flash('Please select a tracker file first.', 'warning')
        return redirect(url_for('index'))

    event_data, student_data = load_data(tf)

    if request.method == 'GET':
        return render_template('edit_members.html',
                               students=student_data,
                               all_classes=get_all_classes(),
                               all_families=get_all_families())

    # POST — bulk update all members
    changed = 0
    for i, student in enumerate(student_data):
        new_class = request.form.get(f'class_{i}', '').strip()
        new_family = request.form.get(f'family_{i}', '').strip()

        if not new_class or not new_family:
            continue
        if new_class not in get_all_classes() or new_family not in get_all_families():
            continue

        if new_class != student.classification or new_family != student.family:
            student_data[i] = Student(student.first_name, student.last_name,
                                     new_class, new_family,
                                     student.event_list, student.row_number)
            changed += 1

    if changed > 0:
        saver(student_data, event_data, tf)
        flash(f'Updated {changed} member(s) successfully.', 'success')
    else:
        flash('No changes detected.', 'info')

    return redirect(url_for('edit_members'))


# ---------------------------------------------------------------------------
# Settings (manage classifications, families, event types)
# ---------------------------------------------------------------------------

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    cfg = load_config()

    if request.method == 'GET':
        return render_template('settings.html', config=cfg)

    # POST — update config
    section = request.form.get('section', '')
    action = request.form.get('action', '')
    value = request.form.get('value', '').strip()

    if section not in ('classifications', 'families', 'event_types', 'leaderboard_event_types'):
        flash('Invalid section.', 'danger')
        return redirect(url_for('settings'))

    if action == 'add' and value:
        if value not in cfg[section]:
            cfg[section].append(value)
            save_config(cfg)
            flash(f'Added "{value}" to {section.replace("_", " ")}.', 'success')
        else:
            flash(f'"{value}" already exists.', 'warning')
    elif action == 'remove' and value:
        if value in cfg[section]:
            cfg[section].remove(value)
            save_config(cfg)
            flash(f'Removed "{value}" from {section.replace("_", " ")}.', 'success')
        else:
            flash(f'"{value}" not found.', 'warning')

    return redirect(url_for('settings'))


# ---------------------------------------------------------------------------
# Delete Event (pick which one)
# ---------------------------------------------------------------------------

@app.route('/delete-event', methods=['POST'])
def delete_event():
    tf = get_tracker_file()
    if not tf:
        flash('Please select a tracker file first.', 'warning')
        return redirect(url_for('index'))

    event_data, student_data = load_data(tf)
    if not event_data:
        flash('No events to delete.', 'warning')
        return redirect(url_for('tracker'))

    try:
        event_index = int(request.form.get('event_index', -1))
    except (ValueError, TypeError):
        flash('Invalid event selection.', 'danger')
        return redirect(url_for('tracker'))

    if event_index < 0 or event_index >= len(event_data):
        flash('Event not found.', 'danger')
        return redirect(url_for('tracker'))

    removed = event_data.pop(event_index)

    # Remove the event from every student's event_list
    for student in student_data:
        student._Student__event_list = [e for e in student._Student__event_list if e != removed.name]

    saver(student_data, event_data, tf)
    flash(f'Deleted event "{removed.name}" and saved.', 'success')
    return redirect(url_for('tracker'))


# ---------------------------------------------------------------------------
# Edit Single Member (click from Data Table)
# ---------------------------------------------------------------------------

@app.route('/edit-member/<int:row>', methods=['GET', 'POST'])
def edit_member(row):
    tf = get_tracker_file()
    if not tf:
        flash('Please select a tracker file first.', 'warning')
        return redirect(url_for('index'))

    event_data, student_data = load_data(tf)

    if row < 0 or row >= len(student_data):
        flash('Member not found.', 'danger')
        return redirect(url_for('tracker'))

    student = student_data[row]

    # Build list of events this member has hours for (attendance > 0)
    member_events = []
    for i, event in enumerate(event_data):
        att = event.attendance
        if row < len(att):
            try:
                hrs = float(att[row])
            except (ValueError, TypeError):
                hrs = 0.0
            if hrs > 0:
                member_events.append({'index': i, 'name': event.name,
                                      'type': event.classification,
                                      'date': event.date, 'hours': hrs})

    if request.method == 'GET':
        return render_template('edit_member.html',
                               student=student,
                               row=row,
                               all_classes=get_all_classes(),
                               all_families=get_all_families(),
                               member_events=member_events)

    # POST — update classification and family
    new_class = request.form.get('classification', '').strip()
    new_family = request.form.get('family', '').strip()

    if new_class not in get_all_classes():
        flash('Invalid classification.', 'danger')
        return redirect(url_for('edit_member', row=row))
    if new_family not in get_all_families():
        flash('Invalid family.', 'danger')
        return redirect(url_for('edit_member', row=row))

    updated = Student(student.first_name, student.last_name, new_class, new_family,
                      student.event_list, student.row_number)
    student_data[row] = updated
    saver(student_data, event_data, tf)
    flash(f'Updated {student.first_name} {student.last_name} successfully.', 'success')
    return redirect(url_for('edit_member', row=row))


# ---------------------------------------------------------------------------
# Edit Member Event Hours
# ---------------------------------------------------------------------------

@app.route('/edit-member-hours/<int:row>', methods=['POST'])
def edit_member_hours(row):
    tf = get_tracker_file()
    if not tf:
        flash('Please select a tracker file first.', 'warning')
        return redirect(url_for('index'))

    event_data, student_data = load_data(tf)

    if row < 0 or row >= len(student_data):
        flash('Member not found.', 'danger')
        return redirect(url_for('tracker'))

    student = student_data[row]
    changed = 0

    for i, event in enumerate(event_data):
        field_name = f'hours_{i}'
        new_val = request.form.get(field_name)
        if new_val is None:
            continue

        new_val = new_val.strip()
        try:
            new_hours = float(new_val)
            if new_hours < 0:
                new_hours = 0.0
        except (ValueError, TypeError):
            continue

        att = list(event.attendance)
        old_hours = float(att[row]) if row < len(att) else 0.0

        if new_hours != old_hours:
            att[row] = str(new_hours)
            event._Event__attendance = att

            # Update student event_list: add if hours > 0 and not listed, remove if 0
            if new_hours > 0 and event.name not in student._Student__event_list:
                student._Student__event_list.append(event.name)
            elif new_hours == 0 and event.name in student._Student__event_list:
                student._Student__event_list = [e for e in student._Student__event_list if e != event.name]

            changed += 1

    if changed > 0:
        saver(student_data, event_data, tf)
        flash(f'Updated hours for {changed} event(s).', 'success')
    else:
        flash('No changes detected.', 'info')

    return redirect(url_for('edit_member', row=row))


# ---------------------------------------------------------------------------
# Delete Member
# ---------------------------------------------------------------------------

@app.route('/delete-member/<int:row>', methods=['POST'])
def delete_member(row):
    tf = get_tracker_file()
    if not tf:
        flash('Please select a tracker file first.', 'warning')
        return redirect(url_for('index'))

    event_data, student_data = load_data(tf)

    if row < 0 or row >= len(student_data):
        flash('Member not found.', 'danger')
        return redirect(url_for('tracker'))

    removed = student_data.pop(row)

    # Remove this member's attendance entry from all events
    for event in event_data:
        att = list(event.attendance)
        if row < len(att):
            att.pop(row)
        event._Event__attendance = att

    # Re-number remaining students
    for i, student in enumerate(student_data):
        student._Student__row_number = i

    saver(student_data, event_data, tf)
    flash(f'Deleted member {removed.first_name} {removed.last_name}.', 'success')
    return redirect(url_for('tracker'))


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
