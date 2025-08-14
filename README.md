# Task Management API

Current scope: ONLY user registration and login (token issued + stored in HttpOnly cookie). Task CRUD and profile endpoints are not yet active.

## Stack

- Python 3 / Django / Django REST Framework
- DRF Token Authentication (rest_framework.authtoken)
- SQLite (dev)

## Quick Start (Windows)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Environment (local)

Create `.env` or set vars:

```
DEBUG=True
SECRET_KEY=replace-me
```

## Auth Flow

1. Register user => token created.
2. Token returned via HttpOnly cookie: auth_token
3. Subsequent authenticated requests (future endpoints) will read cookie automatically (no manual header needed).
   Optional manual header format (if extracting token yourself):

```
Authorization: Token <token>
```

## Implemented Endpoints

| Method | Path           | Auth | Description        | Body JSON (required fields) |
| ------ | -------------- | ---- | ------------------ | --------------------------- |
| POST   | /api/register/ | No   | Create new account | username, email, password   |
| POST   | /api/login/    | No   | Login (user/email) | username OR email, password |

## Examples

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

Response 201:

```json
{
  "user": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "first_name": "",
    "last_name": ""
  }
}
```

(Set-Cookie: auth_token=<token>)

### Login (username)

```http
POST /api/login/
Content-Type: application/json

{
  "username": "alice",
  "password": "StrongPass123"
}
```

### Login (email)

```http
POST /api/login/
Content-Type: application/json

{
  "email": "alice@example.com",
  "password": "StrongPass123"
}
```

### curl

```bash
curl -i -X POST http://127.0.0.1:8000/api/register/ ^
  -H "Content-Type: application/json" ^
  -d "{ \"username\":\"alice\",\"email\":\"alice@example.com\",\"password\":\"StrongPass123\" }"

curl -i -X POST http://127.0.0.1:8000/api/login/ ^
  -H "Content-Type: application/json\" ^
  -d \"{ \\\"username\\\":\\\"alice\\\",\\\"password\\\":\\\"StrongPass123\\\" }"
```

## JSON Parse Error Tip

Error: JSON parse error - Extra data usually means:

- Trailing commas
- Multiple JSON objects in one body
- Single quotes instead of double quotes
  Correct format:

```json
{ "username": "alice", "password": "StrongPass123" }
```

## Security Notes

- Passwords hashed by Django.
- Set secure=True on auth cookie in production (HTTPS).
- Do not expose SECRET_KEY.

## Planned (Not Yet Implemented)

- Profile: GET/PUT/DELETE /api/user/
- Task CRUD: /api/tasks/...
- Complete / incomplete toggle
- Filtering & pagination
- Optional JWT alternative
- Logout (token rotate/delete)
- Tests & OpenAPI
