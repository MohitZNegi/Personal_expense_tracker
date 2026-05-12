# Expense Tracker

A full-stack personal finance app built with Flask, SQLAlchemy, and Jinja2. This is **Project 1** of a five-project Python backend learning series, focusing on OOP best practices, the app factory pattern, and relational database design.

---

## What it does

- Register and log in with a personal account (passwords are hashed, never stored in plain text)
- Add, edit, and delete expenses with a description, amount, date, and optional notes
- Organise expenses into colour-coded categories
- View a monthly summary showing total spend and a breakdown by category
- Drill into any category to see all its expenses

---

## Tech stack

| Layer         | Technology                              |
| ------------- | --------------------------------------- |
| Web framework | Flask 3.x                               |
| ORM           | SQLAlchemy (via Flask-SQLAlchemy)       |
| Database      | SQLite (dev)                            |
| Auth          | Flask-Login + Werkzeug password hashing |
| Templates     | Jinja2                                  |
| Forms         | Flask-WTF                               |
| Config        | python-dotenv                           |

---

## Project structure

```
expense_tracker/
├── app/
│   ├── __init__.py            # App factory — create_app()
│   ├── extensions.py          # db, login_manager (created once, bound in factory)
│   ├── models/
│   │   ├── __init__.py        # Re-exports User, Expense, Category
│   │   ├── user.py            # User ORM model + auth helpers
│   │   ├── expense.py         # Expense ORM model + query class methods
│   │   └── category.py        # Category ORM model
│   ├── blueprints/
│   │   ├── auth/
│   │   │   └── routes.py      # /auth/register, /auth/login, /auth/logout
│   │   ├── expenses/
│   │   │   └── routes.py      # /expenses/ CRUD + /expenses/summary
│   │   └── categories/
│   │       └── routes.py      # /categories/ CRUD + /categories/<id>
│   ├── templates/
│   │   ├── base.html          # Shared HTML shell (nav, flash messages)
│   │   ├── auth/
│   │   ├── expenses/
│   │   └── categories/
│   └── static/css/
├── config.py                  # Config classes: Base → Dev / Test / Prod
├── run.py                     # Entry point
└── requirements.txt
```

---

## Quick start

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd expense_tracker

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create a .env file
echo "SECRET_KEY=your-secret-key-here" > .env
echo "FLASK_ENV=development" >> .env

# 5. Run the app
python run.py
```

Visit `http://127.0.0.1:5000` — register an account and start adding expenses.

---

## Key routes

| Method   | Route                     | Description                 |
| -------- | ------------------------- | --------------------------- |
| GET/POST | `/auth/register`          | Create an account           |
| GET/POST | `/auth/login`             | Log in                      |
| GET      | `/auth/logout`            | Log out                     |
| GET      | `/expenses/`              | List all expenses           |
| GET/POST | `/expenses/add`           | Add a new expense           |
| GET/POST | `/expenses/<id>/edit`     | Edit an expense             |
| POST     | `/expenses/<id>/delete`   | Delete an expense           |
| GET      | `/expenses/summary`       | Monthly summary by category |
| GET      | `/categories/`            | List all categories         |
| GET/POST | `/categories/add`         | Add a category              |
| GET/POST | `/categories/<id>/edit`   | Edit a category             |
| POST     | `/categories/<id>/delete` | Delete a category           |
| GET      | `/categories/<id>`        | All expenses in a category  |

---

## OOP concepts applied

**Inheritance** — `DevelopmentConfig(Config)` inherits shared settings and only overrides what differs. `User(UserMixin, db.Model)` inherits both Flask-Login behaviour and SQLAlchemy ORM capabilities.

**Encapsulation** — password logic (`set_password`, `check_password`) lives inside the `User` class, not scattered across route handlers. Routes never touch `password_hash` directly.

**Class methods** — `User.get_by_email()`, `Expense.get_monthly_total()`, `Expense.get_by_category()` are query helpers that belong to the model. Routes stay thin and readable.

**Composition** — `Expense` has a `Category` (via FK), `User` has many `Expense` objects (via relationship). SQLAlchemy handles the joins.

**Single responsibility** — each blueprint owns one domain (auth, expenses, categories). Models handle data and queries. Templates handle display. Nothing is mixed.

---

## Environment variables

| Variable       | Description                              | Default                     |
| -------------- | ---------------------------------------- | --------------------------- |
| `SECRET_KEY`   | Flask session signing key                | `dev-secret-change-in-prod` |
| `FLASK_ENV`    | `development` / `production` / `testing` | `development`               |
| `DATABASE_URL` | Production DB URI (PostgreSQL etc.)      | SQLite in dev               |

---

## Running tests

```bash
pip install pytest
pytest
```

Tests use `TestingConfig` which points to an in-memory SQLite database — the file is wiped after every test run.

---

## Next steps

- Add CSV export for expense reports
- Swap SQLite for PostgreSQL for production
- Add a React frontend (covered in Project 2)
- Deploy with Docker (covered in Project 4)
