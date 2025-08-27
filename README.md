# 🚀 Task Management API

A secure, modern REST API for personal task management — built with Django & Django REST Framework.

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/Django_REST_Framework-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

---

## 🌟 What is this?

**Task Management API** lets users securely register, log in, and manage their own to-do lists. Each user can create, update, complete, and delete their tasks. All actions are protected by token authentication (via HttpOnly cookies for safety).

**Perfect for:**

- Building a React/Vue/mobile frontend
- Learning modern Django REST API patterns
- Deploying as a backend for your productivity app

---

## ✨ Key Features

- **User Registration & Login** (token in HttpOnly cookie)
- **Profile Management** (view, update, delete)
- **Task CRUD** (create, list, update, delete)
- **Mark Tasks Complete/Incomplete**
- **Filtering, Search & Pagination** (by completion, text, date)
- **Ordering** (by creation or due date)
- **Rate Limiting** (prevents brute-force attacks)
- **Secure Password Hashing**
- **Token Rotation & Logout**
- **Per-user Data Isolation**
- **Comprehensive Validation** (e.g., no past due dates)
- **Production-ready Security** (cookie flags, throttling)
- **100% Automated Tests**

---

## 🖥️ Demo

### Register

```http
POST /api/register/
Content-Type: application/json

{
  "username": "alice",
  "email": "alice@example.com",
  "password": "StrongPass123"
}
```

_Response: 201 Created, sets `auth_token` cookie._

### Login (with username or email)

```http
POST /api/login/
Content-Type: application/json

{
  "username": "alice",
  "password": "StrongPass123"
}
```

_Response: 200 OK, sets `auth_token` cookie._

### Create Task

```http
POST /api/tasks/
Cookie: auth_token=<token>
Content-Type: application/json

{
  "title": "Finish project",
  "description": "Complete final features",
  "due_date": "2025-09-01T12:00:00Z"
}
```

### List Tasks (with filters, search, pagination)

```http
GET /api/tasks/?completed=false&search=project&page=1&page_size=5
Cookie: auth_token=<token>
```

### Mark Complete

```http
PATCH /api/tasks/1/complete/
Cookie: auth_token=<token>
```

### Logout

```http
POST /api/logout/
Cookie: auth_token=<token>
```

_Logs out and clears the token cookie._

---

## ⚡ Quick Start (Windows)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## ⚙️ Environment

Create a `.env` file or set environment variables:

```shell
DEBUG=True
SECRET_KEY=replace-me
```

---

## 🔒 Security Highlights

- Passwords hashed with Django's best practices
- Auth token stored in HttpOnly, SameSite cookie (set `secure=True` in production)
- Rate limiting on sensitive endpoints (5/min for auth endpoints)
- Token rotation on logout
- All endpoints require authentication except register/login
- Due date validation prevents past dates

---

## 🧪 Testing

Run all tests (unit & integration):

```bash
python manage.py test
```

---

## 📝 API Reference

| Method | Path                          | Auth | Description                     |
| ------ | ----------------------------- | ---- | ------------------------------- |
| POST   | `/api/register/`              | ❌   | Register new user               |
| POST   | `/api/login/`                 | ❌   | Login (username/email)          |
| POST   | `/api/logout/`                | ✅   | Logout (token rotate & clear)   |
| GET    | `/api/profile/`               | ✅   | Get user profile                |
| PUT    | `/api/profile/update/`        | ✅   | Update user profile             |
| DELETE | `/api/profile/delete/`        | ✅   | Delete user account             |
| GET    | `/api/tasks/`                 | ✅   | List tasks (filter/search/page) |
| POST   | `/api/tasks/`                 | ✅   | Create new task                 |
| GET    | `/api/tasks/<id>/`            | ✅   | Get specific task               |
| PUT    | `/api/tasks/<id>/`            | ✅   | Update task                     |
| DELETE | `/api/tasks/<id>/`            | ✅   | Delete task                     |
| PATCH  | `/api/tasks/<id>/complete/`   | ✅   | Mark task as complete           |
| PATCH  | `/api/tasks/<id>/incomplete/` | ✅   | Mark task as incomplete         |

---

## 📦 Models

### Task

```python
class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='tasks')
```

---

## 🐞 Troubleshooting

- **JSON parse error?**  
  Use double quotes, no trailing commas, and only one JSON object per request.
- **Auth errors?**  
  Make sure you're sending the `auth_token` cookie with your requests after login/register.
- **Getting 400 errors on task creation?**  
  Ensure due_date is in the future, not the past.

---

## 🛣️ Future Enhancements

- OpenAPI/Swagger documentation
- Docker containerization
- CI/CD pipeline
- Email notifications for upcoming tasks
- Task categories and tags
- User task statistics

---

## About

Built with ❤️ using Django REST Framework
