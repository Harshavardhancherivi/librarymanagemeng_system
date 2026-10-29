# Library Management System (Python)

A beginner-friendly command-line Library Management System using Python and SQLite.

## Features
- Add/list books
- Register/list members
- Issue books with availability checks
- Return books
- View active loans
- Local persistent SQLite database

## Requirements
Python 3.10+. No third-party packages required.

## Run
```bash
python src/main.py
```
The `library.db` database is created automatically.

## Project structure
```text
library-management-system/
├── src/main.py
├── README.md
├── .gitignore
└── LICENSE
```

## Future improvements
- Add due dates and overdue fines
- Add unit tests
- Add a Tkinter or Flask interface
- Add librarian login and role-based access
