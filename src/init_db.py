from mysql.connector.cursor import MySQLCursor
from main import PROG_NAME


def init_db(cursor: MySQLCursor):
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {PROG_NAME}")
    cursor.execute(f"USE {PROG_NAME}")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rings (
            name      VARCHAR(20)  PRIMARY KEY,
            duration  INT          NOT NULL
        )
    """)
    # Check if there are rows in the table
    cursor.execute("SELECT NULL FROM rings")
    if cursor.fetchall() == []:
        # If not insert default values
        cursor.execute("""
            INSERT INTO rings VALUES
                ("Short",  3 ),
                ("Medium", 5 ),
                ("Long",   10)
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id          INT          PRIMARY KEY AUTO_INCREMENT,
            name        VARCHAR(50)  NOT NULL,
            start_time  TIME         NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS periods (
            schedule_id   INT          NOT NULL,
            period_order  INT          NOT NULL,
            duration      INT          NOT NULL,
            period_name   VARCHAR(50),
            ring_type     VARCHAR(20)  NOT NULL,

            FOREIGN KEY (ring_type) REFERENCES rings(name),
            FOREIGN KEY (schedule_id) REFERENCES schedules(id),
            PRIMARY KEY (schedule_id, period_order)
        )
    """)
