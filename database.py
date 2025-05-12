import sqlite3
import random
import uuid


class database:
    def __init__(self):
        pass

    def initialize_database(self):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        return conn, cursor
    
    @staticmethod
    def create_tables():
        """Create tables in the database"""
        db = database()
        conn, cursor = db.initialize_database()

        sql = """CREATE TABLE Classes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL,
            student_nbr INTEGER NOT NULL
            )"""
        cursor.execute("DROP TABLE IF EXISTS Classes")
        cursor.execute(sql)
        conn.commit()

        sql = """CREATE TABLE Students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            student_name TEXT NOT NULL
            )"""
        cursor.execute("DROP TABLE IF EXISTS Students")
        cursor.execute(sql)
        conn.commit()

        conn.close()
        return
    
    @staticmethod
    def fetch_classes():
        """Fetch all classes from the database"""
        db = database()
        conn, cursor = db.initialize_database()
        
        cursor.execute("SELECT * FROM Classes")
        classes = cursor.fetchall()

        conn.close()
        return classes
    
    @staticmethod
    def fetch_students(class_name:str):
        """Fetch all students of a specific classe from the database"""
        db = database()
        conn, cursor = db.initialize_database()

        cursor.execute("""SELECT Students.*
                        FROM Students
                        JOIN Classes ON Students.class_id = Classes.id
                        WHERE Classes.class_name = ?""", (class_name,))
        students = cursor.fetchall()

        conn.close()
        return students
    
    @staticmethod
    def add_class(class_name:str, student_nbr:int, students:list):
        """Add a class in the database"""

        db = database()
        conn, cursor = db.initialize_database()

        cursor.execute("""INSERT INTO Classes(class_name, student_nbr)
                       VALUES(?, ?)""", (class_name, student_nbr,))
        conn.commit()

        cursor.execute("SELECT MAX(id) FROM Classes")
        class_id = cursor.fetchone()[0]
        # class_id = cursor.lastrowid
        print(class_id)
        db.add_students(class_id, students)
        conn.close()
        return
    
    def add_students_to_class(class_name:str, student_nbr:int, students:list):
        """Add students to a class in the database"""

        db = database()
        conn, cursor = db.initialize_database()

        cursor.execute("""SELECT * FROM Classes WHERE class_name = ?""", (class_name,))
        class_info = cursor.fetchone()
        class_id = class_info[0]
        nbr = class_info[-1]
        conn.commit()

        print(class_id)
        db.add_students(class_id, students)
        db.update_student_nbr(class_name, student_nbr+nbr)
        conn.close()
        return
    
    @staticmethod
    def check_classe_name(class_name:str):
        """Check if a class name already exists in the database"""

        class_list = database.fetch_classes()

        for id, name, nbr in class_list:
            if name == class_name:
                return True
            
        return False

    @staticmethod
    def add_students(class_id:int, students:list):
        """Add a students in the database"""

        db = database()
        conn, cursor = db.initialize_database()

        for student_name in students:
            cursor.execute("""INSERT INTO Students(class_id, student_name)
                           VALUES(?, ?)""", (class_id, student_name,))
            conn.commit()

        conn.close()
        return

    @staticmethod
    def update_student_nbr(class_name:str, student_nbr:int):
        """Update the number of students in the database"""
        db = database()
        conn, cursor = db.initialize_database()

        cursor.execute(f"""UPDATE Classes
                        SET student_nbr = {student_nbr}
                        WHERE class_name = '{class_name}'""")
        conn.commit()
        conn.close()
        return

    @staticmethod
    def get_last_student_id():
        """Get the last student id from the database"""

        db = database()
        conn, cursor = db.initialize_database()

        cursor.execute("SELECT MAX(id) FROM Students")
        last_id = cursor.fetchone()[0]

        print(last_id)
        conn.close()
        return last_id if last_id != None else 0

    @staticmethod
    def delete_student(class_name:str, student_name:str):
        """Remove a user from the database"""
        db = database()
        conn, cursor = db.initialize_database()

        cursor.execute(f"""SELECT * FROM Classes WHERE class_name = ?""", (class_name,))
        class_info = cursor.fetchone()

        if len(class_info) == 0:
            print("Class not found")
            return

        cursor.execute(f"""DELETE FROM Students
                        WHERE class_id={class_info[0]} AND student_name='{student_name}'""")
        conn.commit()

        cursor.execute(f"""UPDATE Classes
                        SET student_nbr = {class_info[-1]-1}
                        WHERE class_name = '{class_name}'""")
        conn.commit()
        conn.close()
        return


    def read_classes(self):
        conn, cursor = self.initialize_database()
        cursor.execute("""SELECT * FROM Classes""")
        rows = cursor.fetchall()
        conn.close()
        print(*rows, sep="\n")
        return

    def read_students(self, class_name:str):
        conn, cursor = self.initialize_database()

        cursor.execute("""SELECT Students.*
                        FROM Students
                        JOIN Classes ON Students.class_id = Classes.id
                        WHERE Classes.class_name = ?""", (class_name,))
        students = cursor.fetchall()
        conn.close()
        print(*students, sep="\n")
        return

if __name__ == "__main__":
    db = database()
    database.create_tables()
    # database.add_user(str(uuid.uuid4()), "MedOnly", "mohamed.rouane.23@ump.ac.ma", "password", random.randint(100000, 999999), 1)
    # db.read_users()
    # database.update_user_password("mohamed.rouane.23@ump.ac.ma", "new")
    db.read_classes()
    db.read_students('gi')
    # db.delete_student('gi', 'mohamed rouane')
    # db.read_students('gi')
    # db.read_students('IDSCC')
    database.get_last_student_id()
