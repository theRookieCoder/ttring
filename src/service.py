import logging
from time import sleep
from rich.logging import RichHandler
from mysql.connector.cursor import MySQLCursor
from threading import Timer
from datetime import datetime, timedelta, time
from survey import routines as tui

logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(markup=True)],
)
log = logging.getLogger("ttring")


def serve(cursor: MySQLCursor, id: int):
    logging.info("Starting service")

    cursor.execute("SELECT name, start_time FROM schedules WHERE id = %s", (id,))
    row = cursor.fetchone()
    schedule_name: str = row[0]
    start_time: datetime = (
        datetime.combine(datetime.now(), time(hour=0, minute=0)) + row[1]
    )
    logging.info(f"Schedule [bold]{schedule_name}[/bold] starting at {start_time}")

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
        if type(ring_dur) is tuple:
            ring_dur = ring_dur[0]
        time_acc += timedelta(minutes=period_dur)
        if datetime.now() < time_acc:
            del_t: timedelta = time_acc - datetime.now()
            try:
                ring_dur = max(ring_dur, periods[i + 2][2])
            except IndexError:
                pass
            timers.append(
                Timer(
                    del_t.total_seconds(),
                    ring,
                    [ring_dur, name],
                )
            )
            timers[-1].start()
            logging.info(
                f"Registered {timers[-1]} for [bold]{name}[/bold] to ring in {del_t.total_seconds()} s"
            )
        else:
            logging.warning(f"Time already passed for {name} at {time_acc}")

    if timers == []:
        logging.error("No timers were registered")
        return

    while True:
        try:
            sleep((time_acc - datetime.now()).total_seconds() + 5)
            return
        except KeyboardInterrupt:
            if tui.inquire("Stop service? ", default=True):
                for timer in timers:
                    timer.cancel()
                return


def ring(time_s: int, name: str):
    logging.info(f"Subject {name}, ringing for {time_s} seconds")
