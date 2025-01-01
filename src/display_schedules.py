from mysql.connector.cursor import MySQLCursor
from tabulate import tabulate


def display_schedules(cursor: MySQLCursor):
    cursor.execute("SELECT * FROM schedule")
    schedule_data: list[tuple[int, str, str]] = cursor.fetchall()
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

        periods: list[tuple[str, str, int, int]] = cursor.fetchall()
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
