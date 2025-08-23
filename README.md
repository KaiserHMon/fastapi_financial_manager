# 💰 Finance manager API

API for personal financial management. It allows users to manage their income and expenses, organize them by categories and origin, visualize their balance, calculate their savings compared to the previous month, and access expense distribution graphs. It also provides updated quotes for currencies of interest from the official API of the Central Bank of Argentina (BCRA).

---

## 🧠 Purpose

The main purpose of this API is to facilitate the management of personal finances from a web platform, eliminating the need to carry manual calculations in Excel or paper. It provides visual tools and useful economic information to make better financial decisions.  
It was developed as a personal practice project to strengthen and apply knowledge in backend development.

---

## ⚙️ Technologies used

- **Python**
- **FastAPI** - Main Framework
- **SQLAlchemy**  ORM for database connection
- **MySQL** - Relational database
- **Redis** - In-memory data store for caching
- **JWT** - Token-based authentication
- **Alembic** - Database Version Control
- **Ruff** - Linter and code formatter
- **Pytest** - Framework for testing

---

## 🚀 Getting Started

### Prerequisites

*   Python 3.11+
*   Poetry for dependency management
*   Redis

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/api-financial-manager.git
    cd api-financial-manager
    ```
2.  Install the dependencies using Poetry:
    ```bash
    poetry install
    ```


### Configuration

1.  Create a `.env` file in the root of the project by copying the example file:
    ```bash
    cp .env.example .env
    ```
2.  Update the `.env` file with your database credentials and other environment variables:
    ```
    DATABASE_URL=yourdatabase_url_here
    ASYNC_DATABASE_URL=your_async_database_url_here
    # Example: DATABASE_URL=mysql+pymysql://user:password@localhost/dbname
    # Example: ASYNC_DATABASE_URL=mysql+aiomysql://user:password@localhost/dbname


    JWT_SECRET=your_jwt_secret_here
    JWT_ALGORITHM=your_jwt_algorithm_here
    ACCESS_TOKEN_EXPIRE_MINUTES=your_access_token_expire_minutes_here
    REFRESH_TOKEN_EXPIRE_DAYS=your_refresh_token_expire_minutes_here


    

    REDIS_URL=your_redis_port
    ```

### Running the application

1.  Apply the database migrations:
    ```bash
    poetry run alembic upgrade head
    ```
2.  Start the application:
    ```bash
    poetry run uvicorn src.main:app --reload
    ```

---

## Caching

This application uses Redis for caching to improve performance. The following endpoints are cached:

*   `GET /categories/`
*   `GET /categories/{category_id}`
*   `GET /incomes/`
*   `GET /incomes/{income_id}`
*   `GET /expenses/`
*   `GET /expenses/{expense_id}`
*   `GET /user/balance`
*   `GET /user/balance/incomes`
*   `GET /user/balance/expenses`

The cache expires after 1 hour (3600 seconds). For memory management, the Redis server can be configured to use an LRU (Least Recently Used) eviction policy.

---

## 🧪 Testing

To run the tests, use the following command:

```bash
poetry run pytest
```

---

## 📖 API Endpoints

The following endpoints are available:

*   `/auth`: Authentication (login, refresh token, logout)
*   `/users`: User management (create, read, update, delete)
*   `/categories`: Category management
*   `/incomes`: Income management
*   `/expenses`: Expense management
*   `/user_balance`: User balance (total, incomes and expenses)
*   `/exchange`: Get all available currency exchange rates from the BCRA API.
*   `/exchange/dollar`: Get the exchange rate for the US Dollar.
*   `/exchange/euro`: Get the exchange rate for the Euro.
*   `/exchange/real`: Get the exchange rate for the Brazilian Real.

For more details on each endpoint, you can access the interactive documentation at `http://localhost:8000/docs` when the application is running.

---

## ✒️ Authoring

This project was developed by [Juan Segundo Hardoy](https://github.com/KaiserHMon).

---