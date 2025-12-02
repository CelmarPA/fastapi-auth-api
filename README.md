# FastAPI Auth API

A **production-ready authentication and product management API** built with **FastAPI**, featuring advanced security mechanisms, role-based access control, and robust testing coverage.

---

## 🚀 Features

### Authentication & Security

* **User registration** with role assignment (`superadmin`, `admin`, `user`)
* **Login** with email & password
* **Secure password storage** with bcrypt hashing
* **JWT Access Tokens** (short-lived)
* **Refresh Tokens** with rotation and revocation
* **Logout endpoint** that revokes refresh tokens
* **Rate limiting** and **brute-force protection** per IP and email
* **Comprehensive security logging** for all authentication events

### Authorization (Role-Based Access Control - RBAC)

* `superadmin`: full access to users and products
* `admin`: can manage products and user roles
* `user`: standard limited access

### Token Management

* Access token: short-lived JWT
* Refresh token: securely hashed in the database
* Rotation strategy: each refresh invalidates previous token
* Reuse detection: blocks compromised tokens

### Product Management

* Full **CRUD operations** for products
* Admin-restricted endpoints
* Validation via Pydantic schemas
* Handles non-existent resources gracefully

### Email Notifications

* Password reset emails
* Email verification upon registration
* Integration with **Brevo (Sendinblue) SMTP API**
* Email sending is mocked during tests

### Logging & Security Auditing

* Centralized logging through `SecurityLog`
* Tracks login, logout, password reset, and token refresh events
* Facilitates auditing and monitoring

### Testing

* Full coverage tests using **pytest**
* **Fixtures** for users, admin, products, and login sessions
* Tests include authentication flows, token refresh, email service, CRUD for products, and security logs
* Rate limiter disabled during tests for speed
* Uses **in-memory SQLite** for isolated test runs

---

## 📚 Project Structure

```
auth_api/
│
├── app/
│ ├── core/
│ │ ├── bruteforce.py
│ │ ├── config.py
│ │ ├── exception_handlers.py
│ │ ├── permissions.py
│ │ ├── rate_limit.py
│ │ ├── rate_limit_custom.py
│ │ ├── security.py
│ │ ├── security_log.py
│ │ └── tokens.py
│ │
│ ├── models/
│ │ ├── login_attempt.py
│ │ ├── password_reset_log.py
│ │ ├── products.py
│ │ ├── refresh_token.py
│ │ ├── reset_token.py
│ │ ├── security_log.py
│ │ └── user.py
│ │
│ ├── repositories/
│ │ ├── reset_repository.py
│ │ ├── security_log_repository.py
│ │ ├── token_repository.py
│ │ └── user_repository.py
│ │
│ ├── routers/
│ │ ├── admin_users.py
│ │ ├── auth.py
│ │ └── products.py
│ │
│ ├── schemas/
│ │ ├── auth_schema.py
│ │ ├── message_schema.py
│ │ ├── password_reset_schema.py
│ │ ├── product_schema.py
│ │ ├── security_log_schema.py
│ │ ├── token_schema.py
│ │ └── user_schema.py
│ │
│ ├── services/
│ │ ├── auth_service.py
│ │ ├── email_client.py
│ │ ├── email_service.py
│ │ ├── reset_service.py
│ │ └── user_service.py
│ │
│ ├── tests/
| | ├── conftest.py
│ │ ├── test_auth_logout.py
│ │ ├── test_auth_password_reset.py
│ │ ├── test_auth_refresh.py
│ │ ├── test_auth_register.py
│ │ ├── test_auth_roles.py
│ │ ├── test_auth_security.py
│ │ ├── test_auto_crud.py
│ │ ├── test_email_service.py
│ │ ├── test_products.py
│ │ ├── test_refresh_tokens.py
│ │ └── test_security_log.py
│ │
│ ├── database.py
│ ├── main.py
│ └── __init__.py
│
├── docker-compose.yaml
├── Dockerfile
├── pytest.ini
├── .env.example
├── README.md
└── requirements.txt
```

---

## 💻 Installation

```bash
git clone https://github.com/CelmarPA/fastapi-auth-api.git
cd fastapi-auth-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## ⚡ Running Locally

```bash
uvicorn app.main:app --reload
```

Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Redoc UI: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🔧 Environment Variables

Create a `.env` file inside `app/`:

```
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
DATABASE_URL=sqlite:///./db.sqlite3
MAIL_SENDER=your-email@example.com
BREVO_API_KEY=your-brevo-api-key
FRONTEND_URL=http://localhost:3000
```

---

## 🤚 Testing

Run the full test suite with coverage:

```bash
pytest --cov=app tests/
```

* Tests cover:

  * Authentication flows (login, logout, refresh, registration)
  * Role-based access
  * Email sending (mocked)
  * Product CRUD operations
  * Security logging
* **Fixtures** provide reusable test users, admins, products, and login sessions
* Uses **in-memory SQLite** for isolated, fast tests

Generate **HTML test report**:

```bash
pytest --html=report.html --self-contained-html
```

Generate **coverage report**:

```bash
pytest --cov=app --cov-report=html
```

---

## 💣 Docker

Build and run with Docker Compose:

```bash
docker-compose up --build
```

* Automatically sets up the API with all dependencies
* Ready for development or production use

---

## 📜 License

MIT License

---

**Auth API** is designed for **security, scalability, and maintainability**, providing a solid foundation for production-ready authentication systems and product management backends.
