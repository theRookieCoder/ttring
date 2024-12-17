import mysql.connector as sql
from tabulate import tabulate

db = sql.connect(
    host = "localhost",
    user = "root",
    password = "root",
)
cursor = db.cursor()

PROG_NAME = "ttring"
VERSION = "0.1.0"

def main():
    print(f"{PROG_NAME} version {VERSION}")
    
    init_db()
    
    try:
        while True:
            print('\n' + '=' * 7, "TTRING", '=' * 7)
            
            print("1. Begin Service")
            print("2. View Schedules")
            print("3. Edit a Schedule")
            print("4. Create a Schedule")
            print("5. Delete a Schedule")
            print("6. Save and Quit")
            
            choice = input("Enter your option: ")
            
            if choice == '1':
                print("Service is not implemented!")
            
            elif choice == '2':
                display_schedules()
             
            elif choice == '3':
                print("Editing schedules is not implemented!")
            
            elif choice == '4':
                print("Creating schedules is not implemented!")
            
            elif choice == '5':
                id = pick_schedule();
                delete_schedule(id)
            
            else:
                print("Invalid choice")

    except KeyboardInterrupt:
        db.commit()
        print("\nBye.")


def delete_schedule(id: int):
    cursor.execute(f"DELETE FROM schedule WHERE id = {id}")
    cursor.execute(f"DELETE FROM periods WHERE schedule_id = {id}")
    
    print("Successfully deleted")

def pick_schedule() -> int:
    cursor.execute("SELECT id, name FROM schedule")
    schedules = cursor.fetchall()

    print("\nSchedules")
    for (id, name) in schedules:
        print(f"  {id}. {name}")
    input_id = input("ID of schedule to delete: ")

    if not input_id.isdigit():
        print("Invalid schedule ID")
        return None
    
    for (id, name) in schedules:
        if int(input_id) == id:
            return id
    else:
        return None

def display_schedules():
    cursor.execute("SELECT * FROM schedule")
    schedule_data = cursor.fetchall()
    if schedule_data == []:
        print("No schedules configured!")
        return

    for (id, name, start_time) in schedule_data:
        print(f"\nSchedule {name} starts at {start_time}")
        
        cursor.execute(f"""
            SELECT period_name, ring_type, duration
                FROM periods 
                WHERE schedule_id = {id}
                ORDER BY period_order
        """)
        
        periods = cursor.fetchall()
        print(tabulate(
            periods,
            ("Name", "Ring Type", "Duration"),
            tablefmt="rounded_outline",
        ))

def init_db():
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {PROG_NAME}")
    cursor.execute(f"USE {PROG_NAME}")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rings (
            name VARCHAR(20) PRIMARY KEY,
            duration INT NOT NULL
        )
    """)
    cursor.execute("SELECT NULL FROM rings")
    if cursor.fetchall() == []:
        cursor.execute("""
            INSERT INTO rings VALUES
                ("short",  2 ),
                ("medium", 5 ),
                ("long",   10)
        """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INT PRIMARY KEY,
            name VARCHAR(50),
            start_time TIME
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS periods (
            schedule_id INT NOT NULL,
            period_order INT NOT NULL,
            duration INT NOT NULL,
            period_name VARCHAR(50),
            ring_type VARCHAR(20),
            
            FOREIGN KEY (ring_type) REFERENCES rings(name),
            FOREIGN KEY (schedule_id) REFERENCES schedule(id),
            PRIMARY KEY (schedule_id, period_order)
        )
    """)

if __name__ == "__main__":
    main()
