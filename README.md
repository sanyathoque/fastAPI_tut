# FastAPI SQLAlchemy API

Backend-only FastAPI server intended for a React frontend. It supports common REST requests (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) and uses SQLAlchemy for database access.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

## Run

```powershell
python -m uvicorn app.main:app --reload
```

API docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Example Endpoints

- `GET /health`
- `GET /api/v1/users`
- `POST /api/v1/users`
- `GET /api/v1/users/{user_id}`
- `PUT /api/v1/users/{user_id}`
- `PATCH /api/v1/users/{user_id}`
- `DELETE /api/v1/users/{user_id}`
- `GET /api/v1/posts`
- `POST /api/v1/posts`
- `GET /api/v1/posts/{post_id}`
- `PUT /api/v1/posts/{post_id}`
- `PATCH /api/v1/posts/{post_id}`
- `DELETE /api/v1/posts/{post_id}`

SQLite is used by default. To switch databases, update `DATABASE_URL` in `.env`.
