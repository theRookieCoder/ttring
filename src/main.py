import mysql.connector as sql
from mysql.connector.cursor import MySQLCursor
from survey import routines as tui
from survey._widgets import Escape
import os

import init_db
import create_schedule
import display_schedules
from service import serve


PROG_NAME = "ttring"
VERSION = "0.2.0"

db = sql.connect(
    host="localhost",
    user=os.environ.get("MYSQL_USER", os.getlogin()),
    password=os.environ.get("MYSQL_PASSWORD", ""),
)
cursor: MySQLCursor = db.cursor()


def main():
    print(f"{PROG_NAME} version {VERSION}")

    init_db.init_db(cursor)

    while True:
        try:
            print()
            print("=" * 7, "TTRING", "=" * 7)

            choice: int = tui.select(
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
                id = pick_schedule()

                if id is not None:
                    serve(cursor, id)
                else:
                    print("Action cancelled")

            elif choice == 1:
                display_schedules.display_schedules(cursor)

            elif choice == 2:
                print("Editing schedules is not implemented!")

            elif choice == 3:
                create_schedule.create_schedule(cursor)

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

        except Escape or KeyboardInterrupt or EOFError:
            print()
            try:
                if tui.inquire("Quit without saving? ", default=True):
                    return
            except Escape or KeyboardInterrupt or EOFError:
                print("\nDiscarded changes")
                return


def pick_schedule() -> int | None:
    cursor.execute("SELECT id, name FROM schedule")
    schedules: list[tuple[int, str]] = cursor.fetchall()

    try:
        i: int = tui.select(
            "Pick a schedule: ", options=[name for _id, name in schedules]
        )
        return schedules[i][0]
    except Escape or KeyboardInterrupt or EOFError:
        return None


if __name__ == "__main__":
    main()
    db.close()
    print("Bye.")
