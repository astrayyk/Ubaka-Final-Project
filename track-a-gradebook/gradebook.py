import sqlite3

# Custom Exception for Validation
class InvalidGradeError(Exception):
    """Raised when an inputted grade value is out of the 0-100 range."""
    pass

# --- OBJECT ORIENTED PROGRAMMING LAYER ---

class Person:
    """Base class demonstrating encapsulation with protected attributes."""
    def __init__(self, name: str):
        self._name = name  # Protected attribute

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not value.strip():
            raise ValueError("Name cannot be empty.")
        self._name = value


class Student(Person):
    """Derived class demonstrating inheritance and method overriding."""
    def __init__(self, student_id: int, name: str, grade_level: int):
        super().__init__(name)
        self.student_id = student_id
        self.grade_level = grade_level

    def __str__(self):
        """Overriding the __str__ method for clean data output."""
        return f"ID: {self.student_id} | Name: {self.name} | Grade: {self.grade_level}"


# --- DATABASE & CRUD OPERATIONS LAYER ---

class DatabaseManager:
    def __init__(self, db_name="gradebook.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    grade_level INTEGER NOT NULL
                )""")
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS grades (
                    grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    assignment_name TEXT NOT NULL,
                    score REAL NOT NULL,
                    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
                )""")
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database setup error: {e}")

    def create_student(self, name: str, grade_level: int):
        """C in CRUD: Create Operations"""
        try:
            self.cursor.execute("INSERT INTO students (name, grade_level) VALUES (?, ?)", (name, grade_level))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error saving student record: {e}")

    def read_students(self):
        """R in CRUD: Read Operations"""
        self.cursor.execute("SELECT * FROM students")
        return self.cursor.fetchall()

    def update_student(self, student_id: int, new_name: str, new_level: int):
        """U in CRUD: Update Operations"""
        self.cursor.execute("UPDATE students SET name = ?, grade_level = ? WHERE student_id = ?", (new_name, new_level, student_id))
        self.conn.commit()

    def delete_student(self, student_id: int):
        """D in CRUD: Delete Operations"""
        self.cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        self.conn.commit()

    def add_grade(self, student_id: int, assignment: str, score: float):
        if score < 0 or score > 100:
            raise InvalidGradeError("Grades must be between 0 and 100.")
        self.cursor.execute("INSERT INTO grades (student_id, assignment_name, score) VALUES (?, ?, ?)", (student_id, assignment, score))
        self.conn.commit()

    def get_student_stats(self, student_id: int):
        """Advanced calculations and analytical filtering."""
        self.cursor.execute("SELECT score FROM grades WHERE student_id = ?", (student_id,))
        scores = [row[0] for row in self.cursor.fetchall()]
        if not scores:
            return 0.0, "N/A"
        avg = sum(scores) / len(scores)
        return avg, scores

    def close(self):
        self.conn.close()


# --- USER INTERFACE & UTILITIES LAYER ---

def export_report_card(db: DatabaseManager, student_id: int, student_name: str):
    """File I/O Operation: Writes data out to an external file."""
    avg, scores = db.get_student_stats(student_id)
    filename = f"report_{student_id}.txt"
    with open(filename, "w") as f:
        f.write(f"Official Academic Report Card\n")
        f.write(f"==============================\n")
        f.write(f"Student: {student_name}\n")
        f.write(f"Overall Average: {avg:.2f}%\n")
        f.write(f"Individual Scores: {str(scores)}\n")
    print(f"Report cleanly exported to {filename}!")


def main():
    db = DatabaseManager()
    
    while True:
        print("\n--- GRADEBOOK CONSOLE INTERFACE ---")
        print("1. Add New Student")
        print("2. View All Students")
        print("3. Record Assignment Grade")
        print("4. View Student Average & Export Report")
        print("5. Exit Application")
        
        choice = input("Select an option (1-5): ")
        
        # Try-Except blocks for bulletproof user input validation
        try:
            if choice == "1":
                name = input("Enter Student Full Name: ")
                level = int(input("Enter Grade Level (9-12): "))
                s_id = db.create_student(name, level)
                print(f"Success! Record created with Student ID: {s_id}")
                
            elif choice == "2":
                records = db.read_students()
                for row in records:
                    stu = Student(row[0], row[1], row[2])
                    print(stu)
                    
            elif choice == "3":
                s_id = int(input("Enter Student ID: "))
                assign = input("Enter Assignment Name: ")
                score = float(input("Enter Numeric Score (0-100): "))
                db.add_grade(s_id, assign, score)
                print("Grade logged cleanly.")
                
            elif choice == "4":
                s_id = int(input("Enter Student ID: "))
                name = input("Confirm Student Name for verification: ")
                avg, _ = db.get_student_stats(s_id)
                print(f"Current Calculated Average: {avg:.2f}%")
                export_report_card(db, s_id, name)
                
            elif choice == "5":
                db.close()
                print("Database connections securely closed. Goodbye!")
                break
            else:
                print("Invalid operational choice. Please select 1 through 5.")
        except InvalidGradeError as ie:
            print(f"Validation failure: {ie}")
        except ValueError:
            print("Format processing exception: Please enter numbers only where requested.")
        except Exception as e:
            print(f"An unexpected loop crash error was safely handled: {e}")

if __name__ == "__main__":
    main()
