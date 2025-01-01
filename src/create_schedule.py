from mysql.connector.cursor import MySQLCursor
from survey import routines as tui, widgets
from datetime import time


def create_schedule(cursor: MySQLCursor):
    data: dict[str, any] = tui.form(
        "Enter Schedule Details ",
        form={
            "Name": widgets.Input(),
            "Start time": widgets.DateTime(attrs=["hour", "minute"]),
        },
    )
    name: str = data["Name"]
    if name == "":
        print("Name cannot be empty")
        return
    start_time: time = data["Start time"].time()
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
        i: int = tui.select("Choose ring type", options=[name for name, _len in rings])
        ring_type = rings[i][0]
        cursor.execute(
            "INSERT INTO periods VALUE (%s, %s, %s, %s, %s)",
            (schedule_id, period_order, duration, name, ring_type),
        )
