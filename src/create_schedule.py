from main import cursor

from survey import routines as tui, widgets  # type: ignore
from datetime import datetime


def create_schedule():
    data: dict[str, any] = tui.form(  # type: ignore
        "Enter Schedule Details ",
        form={
            "Name": widgets.Input(),
            "Start time": widgets.DateTime(attrs=["hour", "minute"]),
        },
    )
    name: str = data["Name"]  # type: ignore
    if name == "":
        print("Name cannot be empty")
        return
    start_time: datetime = data["Start time"]  # type: ignore
    cursor.execute(
        "INSERT INTO schedule(name, start_time) VALUE (%s, %s) RETURNING id",
        (name, start_time.time().isoformat(timespec="seconds")),  # type: ignore
    )
    schedule_id: int = cursor.fetchone()[0]  # type: ignore

    cursor.execute("SELECT * FROM rings")
    rings: list[tuple[str, int]] = cursor.fetchall()  # type: ignore

    period_order = 0
    while tui.inquire("Add a period? "):  # type: ignore
        period_order += 1
        name: str = tui.input("Name: ").strip()  # type: ignore
        duration: int = tui.numeric("Duration (in minutes): ", decimal=False)  # type: ignore
        i: int = tui.select(  # type: ignore
            "Choose ring type", options=[name for name, _len in rings]
        )
        ring_type = rings[i][0]
        cursor.execute(
            "INSERT INTO periods VALUE (%s, %s, %s, %s, %s)",
            (schedule_id, period_order, duration, name, ring_type),  # type: ignore
        )
