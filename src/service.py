import logging
from time import sleep
from rich.logging import RichHandler
from mysql.connector.cursor import MySQLCursor
from threading import Timer
from datetime import datetime, timedelta, time


logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("ttring")


def serve(cursor: MySQLCursor, id: int):
    logging.info("Starting service")

    cursor.execute("SELECT name, start_time FROM schedule WHERE id = %s", (id,))
    row = cursor.fetchone()
    schedule_name: str = row[0]
    start_time: datetime = (
        datetime.combine(datetime.now(), time(hour=0, minute=0)) + row[1]
    )
    logging.info(f"Schedule {schedule_name} starting at {start_time}")

    cursor.execute(
        """SELECT periods.period_name, periods.duration, rings.duration
                FROM periods JOIN rings
                    ON periods.ring_type = rings.name
                WHERE periods.schedule_id = %s
                ORDER BY periods.period_order ASC
        """,
        (id,),
    )
    periods: list[tuple[str, int, int]] = cursor.fetchall()
    logging.info(f"Fetched {len(periods)} periods")

    cursor.execute("SELECT MAX(duration) FROM rings")
    max_ring: int = cursor.fetchone()

    time_acc: datetime = start_time
    timers: list[Timer] = []

    for i, (name, period_dur, ring_dur) in enumerate(
        [("Starting", 0, max_ring)] + periods
    ):
        time_acc += timedelta(minutes=period_dur)
        if datetime.now() < time_acc:
            del_t: timedelta = datetime.now() - time_acc
            timers.append(
                Timer(
                    del_t.total_seconds(),
                    ring,
                    max(ring_dur, periods[i + 1][2]),
                    name,
                )
            )
            logging.info(f"Registered {timers[-1]}")
        else:
            logging.warning(f"Time already passed for {name} at {time_acc}")

    if timers == []:
        logging.error("No timers were registered")
        return

    sleep((datetime.now() - time_acc).total_seconds() + 5)


def ring(time_s: int, name: str):
    logging.info(f"Subject {name}, ringing for {time_s} seconds")
