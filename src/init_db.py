from main import cursor, PROG_NAME


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
