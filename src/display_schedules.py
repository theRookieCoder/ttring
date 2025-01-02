from mysql.connector.cursor import MySQLCursor
from tabulate import tabulate
from datetime import time, timedelta, datetime
from rich import print


def display_schedules(cursor: MySQLCursor):
    cursor.execute("SELECT id, name, start_time FROM schedules")
    schedule_data: list[tuple[int, str, time]] = cursor.fetchall()
    if schedule_data == []:
        print("No schedules configured!")
        return

    for id, name, start_time in schedule_data:
        start_time = (
            datetime.combine(datetime.now(), time(hour=0, minute=0)) + start_time
        )
        print(
            f"\nSchedule [bold]{name}[/bold] starts at [yellow]{start_time.strftime("%H:%M")}[/yellow]"
        )

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
        time_acc = start_time
        print(
            tabulate(
                [
                    (
                        name,
                        f"{ring_name} ({ring_len} s)",
                        f"{period_len} min",
                        time_acc.strftime("%H:%M"),
                        time_acc := time_acc + timedelta(minutes=period_len),
                    )[:-1]
                    for name, ring_name, period_len, ring_len in periods
                ],
                ("Name", "Ring", "Duration", "Time"),
                tablefmt="rounded_outline",
            )
        )
