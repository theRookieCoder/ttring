import logging
from rich.logging import RichHandler
from mysql.connector.cursor import MySQLCursor
from threading import Timer
from datetime import datetime, timedelta


logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("ttring")


def serve(cursor: MySQLCursor, id: int):
    logging.info("Starting service")

    cursor.execute("SELECT name, start_time FROM schedule WHERE id = %s", (id,))
    (schedule_name, start_time) = cursor.fetchone()
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

    time_acc: datetime = start_time.datetime()
    timers: list[Timer] = []

    # starting bell
    del_t: timedelta = datetime.now() - time_acc
    timers.append(Timer(del_t.total_seconds(), ring, max_ring))

    # for (i, (name, period_dur, ring_dur)) in enumerate(periods):


def ring(time_s: int):
    logging.info(f"Ringing for {time_s} seconds")
