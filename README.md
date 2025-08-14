# Task Management API

A Django REST Framework (DRF) based API for managing personal tasks. Users can register, authenticate, and perform CRUD operations on their own tasks. Each task is private to its owner.

> NOTE: The README documents the full target design. At present, only the `Task` model and a basic user registration endpoint exist in code. Remaining endpoints (login, profile management, task CRUD, completion toggle, auth setup) still need implementation.

---

## 📋 Features (Planned)

- User registration & authentication (Token or JWT)
- Retrieve / update / delete own user profile
- Create, list, retrieve, update, delete tasks
- Mark tasks complete / incomplete
- Filter tasks by completion state
- Secure multi-user isolation (only owners can access their tasks)

## 🚀 Tech Stack

- Python 3.x
- Django 5.x
- Django REST Framework
- SQLite (dev) – swap for PostgreSQL/MySQL in production
- Token or JWT authentication (to be added)

---

## 🔐 Authentication

Two viable approaches (choose one during implementation):

1. DRF Token Auth (`rest_framework.authtoken`)
2. JWT (e.g. using `djangorestframework-simplejwt`)

Include in `INSTALLED_APPS`, run migrations, then issue tokens on login. All protected endpoints require `Authorization` header:

```text
Authorization: Token <token>
# or
Authorization: Bearer <jwt>
```

---

## 📡 API Endpoints

### Authentication & User

| Method | Endpoint       | Auth | Description                 | Request Body                             |
| ------ | -------------- | ---- | --------------------------- | ---------------------------------------- |
| POST   | /api/register/ | ❌   | Register a new user         | `{ "username", "email", "password" }`    |
| POST   | /api/login/    | ❌   | Login and get auth token    | `{ "username", "password" }`             |
| GET    | /api/user/     | ✅   | Get current user profile    | —                                        |
| PUT    | /api/user/     | ✅   | Update profile fields       | `{ "email", "first_name", "last_name" }` |
| DELETE | /api/user/     | ✅   | Delete (deactivate) account | —                                        |

### Tasks

| Method | Endpoint                      | Auth | Description                   | Request Body / Params                    |
| ------ | ----------------------------- | ---- | ----------------------------- | ---------------------------------------- |
| GET    | /api/tasks/                   | ✅   | List all own tasks            | Optional: `?completed=true`              |
| POST   | /api/tasks/                   | ✅   | Create a new task             | `{ "title", "description", "due_date" }` |
| GET    | /api/tasks/`{id}`/            | ✅   | Retrieve a task by ID         | —                                        |
| PUT    | /api/tasks/`{id}`/            | ✅   | Update title/description/date | `{ "title", "description", "due_date" }` |
| DELETE | /api/tasks/`{id}`/            | ✅   | Delete a task                 | —                                        |
| PATCH  | /api/tasks/`{id}`/complete/   | ✅   | Mark task complete            | —                                        |
| PATCH  | /api/tasks/`{id}`/incomplete/ | ✅   | Mark task incomplete          | —                                        |

Rules:

- All task endpoints require authentication.
- Users may only interact with their own tasks.

---

## 🗃️ Data Model

### User (Django built-in `auth.User`)

| Field       | Type     | Notes              |
| ----------- | -------- | ------------------ |
| id          | bigint   | Auto PK            |
| username    | varchar  | Unique             |
| password    | varchar  | Hashed             |
| email       | varchar  | Unique             |
| first_name  | varchar  | Optional           |
| last_name   | varchar  | Optional           |
| is_staff    | boolean  | Admin flag         |
| is_active   | boolean  | Soft delete flag   |
| date_joined | datetime | Creation timestamp |

### Task (`api.models.Task`)

| Field       | Type         | Notes                                                          |
| ----------- | ------------ | -------------------------------------------------------------- |
| id          | bigint       | Auto PK                                                        |
| user        | FK(User)     | Owner (CASCADE delete)                                         |
| title       | varchar(255) | Required                                                       |
| description | text         | Optional (consider `blank=True, null=True` if making optional) |
| due_date    | datetime     | Nullable                                                       |
| completed   | boolean      | Default `false`                                                |
| created_at  | datetime     | Auto now add                                                   |
| updated_at  | datetime     | Auto now                                                       |

### 🔗 Relationship

```text
User 1 ──── * Task
```

Each task belongs to exactly one user; a user can have many tasks.

---

## 🧪 Example Requests

Using `curl` (Token Auth example):

```bash
# Register
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"StrongPass123"}'

# Login (example response should include token/JWT once implemented)
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"StrongPass123"}'

# List tasks
curl -H "Authorization: Token <token>" http://localhost:8000/api/tasks/

# Create task
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Authorization: Token <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk","description":"2L whole","due_date":"2025-08-20T10:00:00Z"}'
```

---

## 🛠️ Local Development Setup

Assumes [Pipenv](https://pipenv.pypa.io/) based on existing `Pipfile`.

```bash
# Install deps
pipenv install --dev

# Activate shell
pipenv shell

# Apply migrations
python manage.py migrate

# (Optional) Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

Visit: <http://127.0.0.1:8000/>

### Add DRF Token Auth (if chosen)

```python
# settings.py
INSTALLED_APPS += ["rest_framework.authtoken"]
REST_FRAMEWORK = {
  "DEFAULT_AUTHENTICATION_CLASSES": [
    "rest_framework.authentication.TokenAuthentication",
  ],
  "DEFAULT_PERMISSION_CLASSES": [
    "rest_framework.permissions.IsAuthenticated",
  ],
}
```

Create token on login view and return it.

### Add JWT (alternative)

Install: `pip install djangorestframework-simplejwt`

```python
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# urls.py
path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair')
path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
```

---

## ✅ Implementation To-Do (Remaining)

- [ ] Add authentication mechanism (Token or JWT)
- [ ] Implement login view (issuing token/JWT)
- [ ] User profile retrieve/update/delete endpoint
- [ ] Task CRUD endpoints & queryset filtering by owner/completed
- [ ] Complete/incomplete PATCH endpoints
- [ ] Restrict serializers: exclude sensitive fields (e.g., password)
- [ ] Tests for all endpoints & permissions
- [ ] Optional: Pagination, ordering, search
- [ ] Optional: Swagger/OpenAPI schema (`drf-spectacular` or `drf-yasg`)

---

## 🧪 Testing

Add tests in `api/tests.py` or split into a `tests/` package.

Run:

```bash
python manage.py test
```

Recommended areas:

- Registration (duplicate username/email handling)
- Authentication (valid/invalid credentials)
- Task ownership enforcement
- Filtering by `completed`
- Completion toggle endpoints

---

## 🤝 Contributing

1. Fork & branch (`feature/<short-description>`)
2. Ensure tests pass & add coverage
3. Open a descriptive Pull Request

---

## 📄 License

Specify a license (e.g., MIT) here. (Add a `LICENSE` file.)

---

## 📚 Future Enhancements

- Task priority levels & ordering
- Reminders / notifications
- Soft delete & archival
- Tagging / categorization
- Bulk complete operations

---

## 🧾 Changelog

Maintain a `CHANGELOG.md` once multiple releases begin.

---

## 🛡️ Security

- Always hash passwords (Django does this automatically)
- Enforce strong password validation
- Use HTTPS in production
- Rotate and secure SECRET_KEY

---

## 📞 Support

Open an issue or discussion in the repository for questions / feature requests.

---

Happy building! 🎯
