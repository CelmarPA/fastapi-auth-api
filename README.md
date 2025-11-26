# FastAPI Auth API

A production-ready authentication API built with **FastAPI**, featuring:

-   JWT Access Tokens
-   Refresh Tokens (with rotation and revocation)
-   Role-based Authorization (superadmin, admin, user)
-   Secure password hashing (bcrypt)
-   User registration, login, logout
-   Token refresh endpoint
-   Clean project structure
-   Environment variables using pydantic-settings

## Features

### 🔑 Authentication

-   Register users
-   Login with email & password
-   Secure password storage using bcrypt
-   Access token (`15 min`)
-   Refresh token rotation with reuse detection

### 🛡 Authorization (RBAC)

-   `superadmin` --- full control
-   `admin` --- manage users
-   `user` --- standard access

### 🔄 Token System

-   Access token: short-lived JWT
-   Refresh token: stored hashed in database
-   Rotation strategy: every refresh invalidates previous token
-   Reuse detection: blocks compromised tokens

### 📁 Project Structure

    app/
     ├── core/
     │    ├── config.py
     │    ├── security.py
     │    └── tokens.py
     ├── routers/
     │    └── auth.py
     ├── models/
     │    └── user.py
     ├── database.py
     └── main.py

## Installation

``` bash
git clone https://github.com/CelmarPA/fastapi-auth-api.git
cd fastapi-auth-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running

``` bash
uvicorn app.main:app --reload
```

Access Swagger UI:

    http://127.0.0.1:8000/docs

## Environment Variables

Create a `.env` file inside `app/`:

    SECRET_KEY=your-secret-key
    ACCESS_TOKEN_EXPIRE_MINUTES=15
    REFRESH_TOKEN_EXPIRE_DAYS=7
    DATABASE_URL=sqlite:///./db.sqlite3

## License

MIT License
