# FastAPI Photo/Video Sharing API

Backend-only FastAPI server based on `techwithtim/FastAPIPhotoVideoSharing`.

The frontend file from that repo was intentionally not included.

## Features

- User registration and JWT login with `fastapi-users`
- SQLite database with async SQLAlchemy
- Image/video upload endpoint using ImageKit
- Authenticated feed endpoint
- Delete-post endpoint that only allows the owner to delete

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Fill in your ImageKit values in `.env`:

```env
IMAGEKIT_PRIVATE_KEY=
IMAGEKIT_PUBLIC_KEY=
IMAGEKIT_URL=
```

## Run

```powershell
python main.py
```

API docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Example Endpoints

- `POST /auth/register`
- `POST /auth/jwt/login`
- `GET /users/me`
- `PATCH /users/me`
- `POST /upload`
- `GET /feed`
- `DELETE /posts/{post_id}`
