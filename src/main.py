"""Command-line Library Management System using Python and SQLite."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "library.db"


def connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def initialize_database():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE,
            available INTEGER NOT NULL DEFAULT 1 CHECK (available IN (0, 1))
        );
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE
        );
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL REFERENCES books(id),
            member_id INTEGER NOT NULL REFERENCES members(id),
            issue_date TEXT NOT NULL DEFAULT (date('now')),
            return_date TEXT
        );
        """)


def required(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def add_book():
    title, author = required("Title: "), required("Author: ")
    isbn = input("ISBN (optional): ").strip() or None
    try:
        with connect() as db:
            db.execute("INSERT INTO books(title, author, isbn) VALUES (?, ?, ?)",
                       (title, author, isbn))
        print("Book added.")
    except sqlite3.IntegrityError:
        print("That ISBN already exists.")


def list_books():
    with connect() as db:
        rows = db.execute("SELECT * FROM books ORDER BY id").fetchall()
    if not rows:
        print("No books found.")
    for b in rows:
        status = "Available" if b["available"] else "Issued"
        print(f'ID {b["id"]}: {b["title"]} — {b["author"]} | '
              f'ISBN: {b["isbn"] or "N/A"} | {status}')


def register_member():
    name = required("Member name: ")
    email = input("Email (optional): ").strip() or None
    try:
        with connect() as db:
            db.execute("INSERT INTO members(name, email) VALUES (?, ?)", (name, email))
        print("Member registered.")
    except sqlite3.IntegrityError:
        print("That email is already registered.")


def list_members():
    with connect() as db:
        rows = db.execute("SELECT * FROM members ORDER BY id").fetchall()
    if not rows:
        print("No members found.")
    for m in rows:
        print(f'ID {m["id"]}: {m["name"]} | Email: {m["email"] or "N/A"}')


def issue_book():
    try:
        book_id = int(required("Book ID: "))
        member_id = int(required("Member ID: "))
    except ValueError:
        print("IDs must be whole numbers.")
        return
    with connect() as db:
        book = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
        member = db.execute("SELECT * FROM members WHERE id = ?", (member_id,)).fetchone()
        if book is None:
            print("Book not found.")
            return
        if member is None:
            print("Member not found.")
            return
        if not book["available"]:
            print("Book is already issued.")
            return
        db.execute("UPDATE books SET available = 0 WHERE id = ?", (book_id,))
        db.execute("INSERT INTO loans(book_id, member_id) VALUES (?, ?)",
                   (book_id, member_id))
    print("Book issued.")


def return_book():
    try:
        loan_id = int(required("Loan ID: "))
    except ValueError:
        print("Loan ID must be a whole number.")
        return
    with connect() as db:
        loan = db.execute(
            "SELECT * FROM loans WHERE id = ? AND return_date IS NULL", (loan_id,)
        ).fetchone()
        if loan is None:
            print("Active loan not found.")
            return
        db.execute("UPDATE loans SET return_date = date('now') WHERE id = ?", (loan_id,))
        db.execute("UPDATE books SET available = 1 WHERE id = ?", (loan["book_id"],))
    print("Book returned.")


def active_loans():
    with connect() as db:
        rows = db.execute("""
            SELECT loans.id AS loan_id, books.title, members.name, loans.issue_date
            FROM loans JOIN books ON books.id = loans.book_id
            JOIN members ON members.id = loans.member_id
            WHERE loans.return_date IS NULL ORDER BY loans.id
        """).fetchall()
    if not rows:
        print("No active loans.")
    for row in rows:
        print(f'Loan {row["loan_id"]}: "{row["title"]}" to {row["name"]} '
              f'| Issued: {row["issue_date"]}')


def main():
    initialize_database()
    actions = {
        "1": add_book, "2": list_books, "3": register_member,
        "4": list_members, "5": issue_book, "6": return_book,
        "7": active_loans,
    }
    while True:
        print("""
=== LIBRARY MANAGEMENT SYSTEM ===
1. Add book
2. List books
3. Register member
4. List members
5. Issue book
6. Return book
7. View active loans
0. Exit
""")
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
