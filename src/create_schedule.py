from mysql.connector.cursor import MySQLCursor
from survey import routines as tui
from datetime import time


def create_schedule(cursor: MySQLCursor):
    print("Enter Schedule Details")
    name: str = tui.input("Name: ")
    start_time: time = (
        tui.datetime("Start time: ", attrs=["hour", "minute"]).time().replace(second=0)
    )
    if name == "":
        print("Name cannot be empty")
        return
    cursor.execute(
        "INSERT INTO schedule(name, start_time) VALUE (%s, %s) RETURNING id",
        (name, start_time.isoformat(timespec="seconds")),
    )
    schedule_id: int = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM rings")
    rings: list[tuple[str, int]] = cursor.fetchall()

    period_order = 0
    while tui.inquire("Add a period? "):
        period_order += 1
        name: str = tui.input("Name: ").strip()
        duration: int = tui.numeric("Duration (in minutes): ", decimal=False)
        i: int = tui.select(
            "Choose ring type: ", options=[f"{name} ({len} s)" for name, len in rings]
        )
        ring_type = rings[i][0]
        cursor.execute(
            "INSERT INTO periods VALUE (%s, %s, %s, %s, %s)",
            (schedule_id, period_order, duration, name, ring_type),
        )
