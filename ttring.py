import mysql.connector as sql
from mysql.connector.cursor import MySQLCursor
from tabulate import tabulate
from survey import routines as tui  # type: ignore
from survey import widgets  # type: ignore
from survey._widgets import Escape  # type: ignore
from datetime import datetime
import os

db = sql.connect(
    host="localhost",
    user=os.environ.get("MYSQL_USER", os.getlogin()),
    password=os.environ.get("MYSQL_PASSWORD", ""),
)
cursor: MySQLCursor = db.cursor()  # type: ignore

PROG_NAME = "ttring"
VERSION = "0.2.0"


def main():
    print(f"{PROG_NAME} version {VERSION}")

    init_db()

    while True:
        try:
            # term_clear()
            print()
            print("=" * 7, "TTRING", "=" * 7)

            choice: int = tui.select(  # type: ignore
                "Select an action: ",
                options=[
                    "Begin Service",
                    "View Schedules",
                    "Edit a Schedule",
                    "Create a Schedule",
                    "Delete a Schedule",
                    "Save and Quit",
                ],
            )

            if choice == 0:
                print("Service is not implemented!")

            elif choice == 1:
                display_schedules()

            elif choice == 2:
                print("Editing schedules is not implemented!")

            elif choice == 3:
                create_schedule()

            elif choice == 4:
                id = pick_schedule()
                if id is None:
                    print("Action cancelled")
                else:
                    delete_schedule(id)

            elif choice == 5:
                db.commit()
                return

            else:
                print("Invalid choice")

        except Escape or KeyboardInterrupt or EOFError:
            print()
            try:
                if tui.inquire("Quit without saving? ", default=True):  # type: ignore
                    return
            except Escape or KeyboardInterrupt or EOFError:
                print("\nDiscarded changes")
                return


def delete_schedule(id: int):
    cursor.execute("DELETE FROM periods WHERE schedule_id = %s", (id,))
    cursor.execute("DELETE FROM schedule WHERE id = %s", (id,))

    print("Successfully deleted")


def pick_schedule() -> int | None:
    cursor.execute("SELECT id, name FROM schedule")
    schedules: list[tuple[int, str]] = cursor.fetchall()  # type: ignore

    try:
        i: int = tui.select(  # type: ignore
            "Pick a schedule: ", options=[name for _id, name in schedules]
        )
        return schedules[i][0]
    except Escape or KeyboardInterrupt or EOFError:
        return None


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


def display_schedules():
    cursor.execute("SELECT * FROM schedule")
    schedule_data: list[tuple[int, str, str]] = cursor.fetchall()  # type: ignore
    if schedule_data == []:
        print("No schedules configured!")
        return

    for id, name, start_time in schedule_data:
        print(f"\nSchedule {name} starts at {start_time}")

        cursor.execute(
            """
            SELECT period_name, ring_type, periods.duration, rings.duration
                FROM periods JOIN rings ON ring_type = name
                WHERE schedule_id = %s
                ORDER BY period_order
            """,
            (id,),
        )

        periods: list[tuple[str, str, int, int]] = cursor.fetchall()  # type: ignore
        print(
            tabulate(
                [
                    (name, f"{ring_name} ({ring_len} s)", f"{period_len} min")
                    for name, ring_name, period_len, ring_len in periods
                ],
                ("Name", "Ring", "Duration"),
                tablefmt="rounded_outline",
            )
        )


def init_db():
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {PROG_NAME}")
    cursor.execute(f"USE {PROG_NAME}")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rings (
            name      VARCHAR(20)  PRIMARY KEY,
            duration  INT          NOT NULL
        )
    """)
    cursor.execute("SELECT NULL FROM rings")
    if cursor.fetchall() == []:
        cursor.execute("""
            INSERT INTO rings VALUES
                ("Short",  2 ),
                ("Medium", 5 ),
                ("Long",   10)
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id          INT  PRIMARY KEY AUTO_INCREMENT,
            name        VARCHAR(50),
            start_time  TIME
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS periods (
            schedule_id   INT NOT NULL,
            period_order  INT NOT NULL,
            duration      INT NOT NULL,
            period_name   VARCHAR(50),
            ring_type     VARCHAR(20),
            
            FOREIGN KEY (ring_type) REFERENCES rings(name),
            FOREIGN KEY (schedule_id) REFERENCES schedule(id),
            PRIMARY KEY (schedule_id, period_order)
        )
    """)


if __name__ == "__main__":
    main()
    db.close()
    print("Bye.")
