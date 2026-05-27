import sqlite3
from datetime import datetime

# Custom Exception for Operational Safety
class OverBudgetWarningException(Exception):
    """Raised to flag when a category transaction slips past threshold bounds."""
    pass

# --- OOP CLASS LAYER ---

class FinancialEntry:
    def __init__(self, amount: float):
        self._amount = amount

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        if value <= 0:
            raise ValueError("Transaction values must be strictly positive figures.")
        self._amount = value


class ExpenseTransaction(FinancialEntry):
    def __init__(self, amount: float, category_name: str, date_str: str, notes: str):
        super().__init__(amount)
        self.category_name = category_name
        self.date_str = date_str
        self.notes = notes

    def __str__(self):
        return f"[{self.date_str}] Category: {self.category_name} | Amount: ${self.amount:.2f} ({self.notes})"


# --- ENGINE & DATABASE CRUD PERSISTENCE LAYER ---

class BudgetDatabase:
    def __init__(self, db_file="budget.db"):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.init_tables()

    def init_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT UNIQUE NOT NULL,
                monthly_budget_limit REAL NOT NULL
            )""")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                amount REAL NOT NULL,
                transaction_date TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (category_id) REFERENCES categories(category_id)
                )""")
        self.conn.commit()

    def seed_category(self, name: str, limit: float):
        """C in CRUD: Populates base lookup parameters safely."""
        try:
            self.cursor.execute("INSERT OR IGNORE INTO categories (category_name, monthly_budget_limit) VALUES (?, ?)", (name, limit))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database insertion fault: {e}")

    def add_transaction(self, category_name: str, amount: float, notes: str):
        """C in CRUD: Postings checking business thresholds actively."""
        # Find structural category matching configuration
        self.cursor.execute("SELECT category_id, monthly_budget_limit FROM categories WHERE category_name = ?", (category_name,))
        res = self.cursor.fetchone()
        if not res:
            print("Category selection index not found.")
            return
        
        cat_id, budget_limit = res
        
        # Calculate existing balance positions (Advanced Read Filtering)
        self.cursor.execute("SELECT SUM(amount) FROM transactions WHERE category_id = ?", (cat_id,))
        current_sum = self.cursor.fetchone()[0] or 0.0
        
        if current_sum + amount > budget_limit:
            raise OverBudgetWarningException(f"Warning: Transaction of ${amount:.2f} exceeds the ${budget_limit:.2f} budget cap! Current total spent: ${current_sum:.2f}")

        date_string = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.cursor.execute("INSERT INTO transactions (category_id, amount, transaction_date, notes) VALUES (?, ?, ?, ?)",
                            (cat_id, amount, date_string, notes))
        self.conn.commit()

    def get_summary_report(self):
        """R in CRUD: Multi-table aggregation join processing query."""
        query = """
            SELECT c.category_name, c.monthly_budget_limit, SUM(t.amount) as total_spent
            FROM categories c
            LEFT JOIN transactions t ON c.category_id = t.category_id
            GROUP BY c.category_id
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def purge_transaction(self, t_id: int):
        """D in CRUD: Drop functionality control blocks."""
        self.cursor.execute("DELETE FROM transactions WHERE transaction_id = ?", (t_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()


# --- CLI MANAGEMENT RUNNER INTERFACE ---

def generate_csv_export(records):
    """File I/O Operation: Export historical analytics to a CSV format."""
    filename = "spending_audit.csv"
    with open(filename, "w") as f:
        f.write("Category,Budget Limit,Total Aggregated Spent\n")
        for row in records:
            spent = row[2] if row[2] else 0.0
            f.write(f"{row[0]},{row[1]},{spent}\n")
    print(f"CSV ledger summary written output cleanly to {filename}")


def main():
    db = BudgetDatabase()
    # Populate framework defaults safely
    db.seed_category("Food", 300.0)
    db.seed_category("Utilities", 150.0)
    db.seed_category("Entertainment", 100.0)

    while True:
        print("\n--- BUDGET TRACKER CONSOLE ENGINE ---")
        print("1. Record Expense Transaction")
        print("2. View Category Budgets & Spending Summary")
        print("3. Export Financial Statements (CSV)")
        print("4. Exit App")
        
        choice = input("Select operation run context (1-4): ")
        
        try:
            if choice == "1":
                cat = input("Enter category context (Food / Utilities / Entertainment): ").strip()
                amt = float(input("Enter Transaction Cost Amount ($): "))
                note = input("Memo transaction line description: ")
                
                # Active Custom Exception Monitoring Context
                try:
                    db.add_transaction(cat, amt, note)
                    print("Transaction entered into ledger securely.")
                except OverBudgetWarningException as owe:
                    print(owe)
                    confirm = input("Override warnings and apply transactional entry regardless? (y/n): ")
                    if confirm.lower() == 'y':
                        # Internal manual bypass logic override running explicitly
                        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                        db.cursor.execute("SELECT category_id FROM categories WHERE category_name = ?", (cat,))
                        c_id = db.cursor.fetchone()[0]
                        db.cursor.execute("INSERT INTO transactions (category_id, amount, transaction_date, notes) VALUES (?, ?, ?, ?)",
                                            (c_id, amt, date_str, f"[OVERRIDE APPROVED] {note}"))
                        db.conn.commit()
                        print("Forced transaction committed to database.")
                        
            elif choice == "2":
                summary = db.get_summary_report()
                print("\nCategory | Budget Cap | Total Expenditure Status")
                for item in summary:
                    spent = item[2] if item[2] else 0.0
                    print(f"- {item[0]}: ${spent:.2f} spent out of ${item[1]:.2f}")
                    
            elif choice == "3":
                summary = db.get_summary_report()
                generate_csv_export(summary)
                
            elif choice == "4":
                db.close()
                print("System database connections exited gracefully.")
                break
        except ValueError:
            print("Processing Input Error: Verify all numerical entry formats conform strictly.")
        except Exception as general_error:
            print(f"Critical execution catch blocks preserved functionality: {general_error}")

if __name__ == "__main__":
    main()
