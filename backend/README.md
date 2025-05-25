# 💰 Finance manager API

API for personal financial management. It allows users to manage their income and expenses, organize them by categories and origin, visualize their balance, calculate their savings compared to the previous month, and access expense distribution graphs. It also provides updated quotes for currencies of interest such as the MEP dollar, blue dollar, Brazilian real and euro.

---

## 🧠 Purpose

The main purpose of this API is to facilitate the management of personal finances from a web platform, eliminating the need to carry manual calculations in Excel or paper. It provides visual tools and useful economic information to make better financial decisions.  
It was developed as a personal practice project to strengthen and apply knowledge in backend development.

---

## ⚙️ Technologies used

- Python
- FastAPI** - Main Framework
- **SQLAlchemy** - ORM for database connection
- MySQL** - Relational database
- JWT** - Token-based authentication
- Alembic** - Database Version Control
- Ruff** - Linter and code formatter
- Pytest** - Framework for testing

---

## Testing

--

## Authoring

--

## Project structure

/src
  /models           # SQLAlchemy model definitions
  /schemas          # Pydantic schemas
  /routes           # API routes
  /services         # Business logic
  /utils            # Auxiliary functions
  /tests            # Unit tests
/tests              # Integration tests
main.py             # Application entry point
alembic.ini         # Migration configuration
.env.example        # Environment variable template