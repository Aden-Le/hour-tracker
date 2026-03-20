import os
import io
from collections import defaultdict
from glob import glob

import pandas as pd
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, send_file
)

from main import process_main_tracker, apply_event, hour_counter, saver, Student

app = Flask(__name__)
app.secret_key = 'tzu-chi-hour-tracker-secret'

TEMPLATE_FILE = 'blank_template.csv'
ALL_CLASSES = ["Officer", "Junior Officer", "Big Sib", "Member"]
ALL_FAMILIES = ["Kuromi", "PomPom", "Melody", "NoFam"]
ALL_EVENT_TYPES = ["General Meeting", "Officer Meeting", "Tabling", "Volunteer", "Social", "Retreat"]
LEADERBOARD_EVENT_TYPES = ["General Meeting", "Volunteer", "Social"]


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
    return render_template('tracker.html', table_html=table_html, tracker_file=tf)


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
        return render_template('add_event.html', event_types=ALL_EVENT_TYPES)

    # POST — validate and store in session
    event_name = request.form.get('event_name', '').strip()
    event_duration = request.form.get('event_duration', '').strip()
    event_date = request.form.get('event_date', '').strip()
    event_type = request.form.get('event_type', '').strip()

    errors = []
    if not event_name:
        errors.append('Event name is required.')
    if not event_date:
        errors.append('Event date is required.')
    if event_type not in ALL_EVENT_TYPES:
        errors.append('Please select a valid event type.')
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
        return render_template('add_event.html', event_types=ALL_EVENT_TYPES,
                               errors=errors,
                               event_name=event_name, event_duration=event_duration,
                               event_date=event_date, event_type=event_type,
                               names_paste=pasted)

    session['pending_event'] = {
        'name': event_name,
        'duration': event_duration,
        'date': event_date,
        'type': event_type,
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

    if request.method == 'GET':
        return render_template('add_event_confirm.html',
                               pending=pending,
                               matched=matched,
                               new_people=new_people)

    # POST — execute apply_event + saver
    if len(incoming_pairs) != len(set(incoming_pairs)):
        flash('ERROR: Duplicate names detected in the attendee list. Remove duplicates and try again.', 'danger')
        return redirect(url_for('add_event'))

    try:
        new_student_data, new_event_data = apply_event(
            student_data, event_data,
            pending['name'], pending['type'], pending['date'], pending['duration'],
            list(first_names), list(last_names)
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
    selected_classes = ALL_CLASSES[:]
    selected_families = ALL_FAMILIES[:]
    selected_events = ALL_EVENT_TYPES[:]
    top_n = 0

    if request.method == 'POST':
        selected_classes = request.form.getlist('classification') or ALL_CLASSES[:]
        selected_families = request.form.getlist('family') or ALL_FAMILIES[:]
        selected_events = request.form.getlist('event_type') or ALL_EVENT_TYPES[:]
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
                           all_classes=ALL_CLASSES,
                           all_families=ALL_FAMILIES,
                           all_event_types=ALL_EVENT_TYPES,
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

    selected_classes = request.form.getlist('classification') or ALL_CLASSES[:]
    selected_families = request.form.getlist('family') or ALL_FAMILIES[:]
    selected_events = request.form.getlist('event_type') or ALL_EVENT_TYPES[:]
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
    selected_events = LEADERBOARD_EVENT_TYPES[:]

    if request.method == 'POST':
        selected_events = request.form.getlist('event_type') or LEADERBOARD_EVENT_TYPES[:]
        event_data, student_data = load_data(tf)

        families = {}
        for family_name, family_key in [('Kuromi Family', 'Kuromi'),
                                         ('PomPom Family', 'PomPom'),
                                         ('Melody Family', 'Melody')]:
            times = hour_counter(ALL_CLASSES, [family_key], selected_events, student_data, event_data)
            families[family_name] = round(sum(times.values()), 2)

        results = sorted(families.items(), key=lambda x: x[1], reverse=True)

    return render_template('leaderboard.html',
                           leaderboard_event_types=LEADERBOARD_EVENT_TYPES,
                           selected_events=selected_events,
                           results=results)


# ---------------------------------------------------------------------------
# Edit Member
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

    if request.method == 'GET':
        return render_template('edit_member.html',
                               student=student,
                               row=row,
                               all_classes=ALL_CLASSES,
                               all_families=ALL_FAMILIES)

    # POST — update classification and family
    new_class = request.form.get('classification', '').strip()
    new_family = request.form.get('family', '').strip()

    if new_class not in ALL_CLASSES:
        flash('Invalid classification.', 'danger')
        return redirect(url_for('edit_member', row=row))
    if new_family not in ALL_FAMILIES:
        flash('Invalid family.', 'danger')
        return redirect(url_for('edit_member', row=row))

    updated = Student(student.first_name, student.last_name, new_class, new_family,
                      student.event_list, student.row_number)
    student_data[row] = updated
    saver(student_data, event_data, tf)
    flash(f'Updated {student.first_name} {student.last_name} successfully.', 'success')
    return redirect(url_for('tracker'))


# ---------------------------------------------------------------------------
# Delete Last Event
# ---------------------------------------------------------------------------

@app.route('/delete-last-event', methods=['POST'])
def delete_last_event():
    tf = get_tracker_file()
    if not tf:
        flash('Please select a tracker file first.', 'warning')
        return redirect(url_for('index'))

    event_data, student_data = load_data(tf)
    if not event_data:
        flash('No events to delete.', 'warning')
        return redirect(url_for('tracker'))

    removed = event_data[-1]
    event_data = event_data[:-1]

    # Remove the last event from every student's event_list and attendance
    for student in student_data:
        if removed.name in student.event_list:
            student.event_list  # access via property
            student._Student__event_list = [e for e in student._Student__event_list if e != removed.name]

    # Trim the last attendance entry from all remaining events
    for event in event_data:
        if len(event.attendance) > len(student_data):
            event._Event__attendance = event.attendance[:len(student_data)]

    saver(student_data, event_data, tf)
    flash(f'Deleted event "{removed.name}" and saved.', 'success')
    return redirect(url_for('tracker'))


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
