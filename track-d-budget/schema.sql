-- Categories Table (Parent)
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE NOT NULL,
    monthly_budget_limit REAL NOT NULL
);

-- Transactions Table (Child)
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER,
    amount REAL NOT NULL,
    transaction_date TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);
