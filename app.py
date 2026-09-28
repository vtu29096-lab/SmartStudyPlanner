import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime


# ================= DATABASE =================

conn = sqlite3.connect("study_planner.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    exam_date TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    study_hours INTEGER NOT NULL,
    progress INTEGER DEFAULT 0
)
""")

try:
    cursor.execute(
        "ALTER TABLE subjects ADD COLUMN progress INTEGER DEFAULT 0"
    )
except sqlite3.OperationalError:
    pass

conn.commit()


# ================= COLORS =================

BG = "#F4F7FB"
CARD = "#FFFFFF"
TEXT = "#1F2937"
ACCENT = "#4F46E5"
SECONDARY = "#E0E7FF"


# ================= PRIORITY =================

def calculate_priority(exam_date, difficulty, hours):

    try:
        exam = datetime.strptime(exam_date, "%d-%m-%Y")
        days_left = (exam - datetime.now()).days
        days_left = max(days_left, 0)
    except ValueError:
        return "Invalid"

    score = 0

    if days_left <= 3:
        score += 5
    elif days_left <= 7:
        score += 4
    elif days_left <= 14:
        score += 3
    elif days_left <= 30:
        score += 2
    else:
        score += 1

    score += {
        "Easy": 1,
        "Medium": 2,
        "Hard": 3
    }.get(difficulty, 1)

    if hours >= 5:
        score += 2
    elif hours >= 3:
        score += 1

    if score >= 7:
        return "HIGH"
    elif score >= 5:
        return "MEDIUM"
    return "LOW"


# ================= ADD SUBJECT =================

def add_subject():

    window = tk.Toplevel(root)
    window.title("Add Subject")
    window.geometry("500x520")
    window.configure(bg=BG)
    window.resizable(False, False)

    tk.Label(
        window,
        text="Add New Subject",
        font=("Segoe UI", 22, "bold"),
        bg=BG,
        fg=TEXT
    ).pack(pady=25)

    form = tk.Frame(window, bg=CARD, padx=30, pady=25)
    form.pack(padx=30, fill="both")

    tk.Label(
        form,
        text="Subject Name",
        bg=CARD,
        fg=TEXT,
        font=("Segoe UI", 11)
    ).pack(anchor="w")

    subject_entry = ttk.Entry(form, width=40)
    subject_entry.pack(pady=(5, 15))

    tk.Label(
        form,
        text="Exam Date (DD-MM-YYYY)",
        bg=CARD,
        fg=TEXT,
        font=("Segoe UI", 11)
    ).pack(anchor="w")

    date_entry = ttk.Entry(form, width=40)
    date_entry.pack(pady=(5, 15))

    tk.Label(
        form,
        text="Difficulty",
        bg=CARD,
        fg=TEXT,
        font=("Segoe UI", 11)
    ).pack(anchor="w")

    difficulty = ttk.Combobox(
        form,
        values=["Easy", "Medium", "Hard"],
        state="readonly",
        width=37
    )
    difficulty.set("Easy")
    difficulty.pack(pady=(5, 15))

    tk.Label(
        form,
        text="Study Hours",
        bg=CARD,
        fg=TEXT,
        font=("Segoe UI", 11)
    ).pack(anchor="w")

    hours_entry = ttk.Entry(form, width=40)
    hours_entry.pack(pady=(5, 20))

    def save():

        subject = subject_entry.get().strip()
        exam_date = date_entry.get().strip()
        level = difficulty.get()
        hours = hours_entry.get().strip()

        if not subject or not exam_date or not hours:
            messagebox.showwarning(
                "Missing Information",
                "Please fill all fields."
            )
            return

        try:
            datetime.strptime(exam_date, "%d-%m-%Y")
        except ValueError:
            messagebox.showwarning(
                "Invalid Date",
                "Use DD-MM-YYYY format."
            )
            return

        try:
            hours = int(hours)

            if hours <= 0:
                raise ValueError

        except ValueError:
            messagebox.showwarning(
                "Invalid Hours",
                "Enter a positive number."
            )
            return

        cursor.execute("""
            INSERT INTO subjects
            (subject, exam_date, difficulty, study_hours, progress)
            VALUES (?, ?, ?, ?, 0)
        """, (subject, exam_date, level, hours))

        conn.commit()

        messagebox.showinfo(
            "Success",
            "Subject added successfully!"
        )

        window.destroy()

    ttk.Button(
        form,
        text="Save Subject",
        command=save
    ).pack(pady=10)


# ================= VIEW SUBJECTS =================

def view_subjects():

    window = tk.Toplevel(root)
    window.title("My Subjects")
    window.geometry("1000x550")
    window.configure(bg=BG)

    tk.Label(
        window,
        text="My Subjects",
        font=("Segoe UI", 24, "bold"),
        bg=BG,
        fg=TEXT
    ).pack(pady=20)

    table_frame = tk.Frame(window, bg=CARD)
    table_frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=10
    )

    columns = (
        "ID",
        "Subject",
        "Exam Date",
        "Difficulty",
        "Hours",
        "Priority",
        "Progress"
    )

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )

    for column in columns:

        tree.heading(
            column,
            text=column
        )

        tree.column(
            column,
            width=120,
            anchor="center"
        )

    tree.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    subjects = cursor.execute(
        "SELECT * FROM subjects"
    ).fetchall()

    for row in subjects:

        subject_id = row[0]
        subject = row[1]
        exam_date = row[2]
        difficulty = row[3]
        hours = row[4]
        progress = row[5]

        priority = calculate_priority(
            exam_date,
            difficulty,
            hours
        )

        tree.insert(
            "",
            "end",
            values=(
                subject_id,
                subject,
                exam_date,
                difficulty,
                hours,
                priority,
                f"{progress}%"
            )
        )


# ================= TIMETABLE =================

def generate_timetable():

    window = tk.Toplevel(root)
    window.title("Smart Timetable")
    window.geometry("850x550")
    window.configure(bg=BG)

    tk.Label(
        window,
        text="Smart Study Timetable",
        font=("Segoe UI", 24, "bold"),
        bg=BG,
        fg=TEXT
    ).pack(pady=20)

    columns = (
        "Subject",
        "Exam Date",
        "Difficulty",
        "Hours",
        "Priority"
    )

    tree = ttk.Treeview(
        window,
        columns=columns,
        show="headings"
    )

    for column in columns:

        tree.heading(
            column,
            text=column
        )

        tree.column(
            column,
            width=150,
            anchor="center"
        )

    tree.pack(
        fill="both",
        expand=True,
        padx=30,
        pady=10
    )

    subjects = cursor.execute("""
        SELECT subject, exam_date,
               difficulty, study_hours
        FROM subjects
    """).fetchall()

    timetable = []

    for subject, exam_date, difficulty, hours in subjects:

        priority = calculate_priority(
            exam_date,
            difficulty,
            hours
        )

        timetable.append(
            (
                subject,
                exam_date,
                difficulty,
                hours,
                priority
            )
        )

    priority_order = {
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3
    }

    timetable.sort(
        key=lambda x: priority_order.get(
            x[4], 4
        )
    )

    for item in timetable:
        tree.insert(
            "",
            "end",
            values=item
        )

    tk.Label(
        window,
        text="HIGH priority subjects should be studied first.",
        font=("Segoe UI", 11, "bold"),
        bg=BG,
        fg=ACCENT
    ).pack(pady=15)


# ================= PROGRESS =================

def progress_summary():

    window = tk.Toplevel(root)
    window.title("Progress")
    window.geometry("600x450")
    window.configure(bg=BG)

    tk.Label(
        window,
        text="Study Progress",
        font=("Segoe UI", 24, "bold"),
        bg=BG,
        fg=TEXT
    ).pack(pady=30)

    subjects = cursor.execute(
        "SELECT progress FROM subjects"
    ).fetchall()

    if not subjects:

        tk.Label(
            window,
            text="No subjects added yet.",
            font=("Segoe UI", 14),
            bg=BG
        ).pack(pady=30)

        return

    average = sum(
        row[0] for row in subjects
    ) / len(subjects)

    tk.Label(
        window,
        text=f"{average:.1f}%",
        font=("Segoe UI", 40, "bold"),
        bg=BG,
        fg=ACCENT
    ).pack(pady=10)

    tk.Label(
        window,
        text="Overall Study Progress",
        font=("Segoe UI", 13),
        bg=BG,
        fg=TEXT
    ).pack()

    progress_bar = ttk.Progressbar(
        window,
        length=400,
        maximum=100,
        value=average
    )

    progress_bar.pack(pady=25)

    completed = sum(
        1 for row in subjects
        if row[0] == 100
    )

    tk.Label(
        window,
        text=f"Completed Subjects: {completed}/{len(subjects)}",
        font=("Segoe UI", 13),
        bg=BG,
        fg=TEXT
    ).pack(pady=10)


# ================= MAIN DASHBOARD =================

root = tk.Tk()
root.title("Smart Study Planner")
root.geometry("1000x650")
root.configure(bg=BG)
root.resizable(False, False)


# Header

header = tk.Frame(
    root,
    bg=ACCENT,
    height=120
)

header.pack(
    fill="x"
)

tk.Label(
    header,
    text="SMART STUDY PLANNER",
    font=("Segoe UI", 28, "bold"),
    bg=ACCENT,
    fg="white"
).pack(pady=(25, 5))

tk.Label(
    header,
    text="Plan smarter • Study better • Achieve your goals",
    font=("Segoe UI", 11),
    bg=ACCENT,
    fg="white"
).pack()


# Dashboard

tk.Label(
    root,
    text="Student Dashboard",
    font=("Segoe UI", 20, "bold"),
    bg=BG,
    fg=TEXT
).pack(pady=30)


card_frame = tk.Frame(
    root,
    bg=BG
)

card_frame.pack()


def create_card(text, command):

    card = tk.Frame(
        card_frame,
        bg=CARD,
        width=250,
        height=120
    )

    card.pack_propagate(False)

    tk.Button(
        card,
        text=text,
        command=command,
        font=("Segoe UI", 13, "bold"),
        bg=CARD,
        fg=TEXT,
        relief="flat",
        cursor="hand2"
    ).pack(
        fill="both",
        expand=True
    )

    return card


create_card(
    "➕\nAdd Subject",
    add_subject
).grid(
    row=0,
    column=0,
    padx=15,
    pady=15
)

create_card(
    "📚\nView Subjects",
    view_subjects
).grid(
    row=0,
    column=1,
    padx=15,
    pady=15
)

create_card(
    "📅\nSmart Timetable",
    generate_timetable
).grid(
    row=1,
    column=0,
    padx=15,
    pady=15
)

create_card(
    "📊\nProgress",
    progress_summary
).grid(
    row=1,
    column=1,
    padx=15,
    pady=15
)


# Footer

tk.Label(
    root,
    text="Smart Study Planner • Python + Tkinter + SQLite",
    font=("Segoe UI", 10),
    bg=BG,
    fg="#6B7280"
).pack(
    side="bottom",
    pady=20
)


# ================= CLOSE =================

def close_app():

    conn.close()
    root.destroy()


root.protocol(
    "WM_DELETE_WINDOW",
    close_app
)

root.mainloop()