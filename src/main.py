import mysql.connector as sql
from mysql.connector.cursor import MySQLCursor
from survey import routines as tui  # type: ignore
from survey._widgets import Escape  # type: ignore
import os

from init_db import init_db
from create_schedule import create_schedule
from display_schedules import display_schedules
from service import serve

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
                serve()

            elif choice == 1:
                display_schedules()

            elif choice == 2:
                print("Editing schedules is not implemented!")

            elif choice == 3:
                create_schedule()

            elif choice == 4:
                id = pick_schedule()

                if id is not None:
                    cursor.execute("DELETE FROM periods WHERE schedule_id = %s", (id,))
                    cursor.execute("DELETE FROM schedule WHERE id = %s", (id,))
                    print("Successfully deleted")

                else:
                    print("Action cancelled")

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


if __name__ == "__main__":
    main()
    db.close()
    print("Bye.")
