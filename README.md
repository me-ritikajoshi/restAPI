# Voting REST API

A Django REST Framework project for sharing posts and voting on them.

## Features

- Token-based authentication (`signup` and `login`)
- Create and list posts
- Vote/unvote posts
- Owner-only post deletion
- Paginated post list responses

## Tech Stack

- Python 3.11+
- Django
- Django REST Framework
- `rest_framework.authtoken`
- `django-cors-headers`
- SQLite (default)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Server runs at `http://127.0.0.1:8000/`.

## Environment Variables

- `DJANGO_SECRET_KEY`: secret key value
- `DJANGO_DEBUG`: `True`/`False` (default `True`)
- `DJANGO_ALLOWED_HOSTS`: comma-separated hosts (default `localhost,127.0.0.1`)
- `CORS_ALLOWED_ORIGINS`: comma-separated origins
- `DJANGO_TIME_ZONE`: timezone string (default `UTC`)

## API Endpoints

- `POST /api/signup/`
- `POST /api/login/`
- `GET /api/posts/`
- `POST /api/posts/` (auth required)
- `GET /api/posts/<post_id>/`
- `DELETE /api/posts/<post_id>/` (owner only)
- `POST /api/posts/<post_id>/vote/` (auth required)
- `DELETE /api/posts/<post_id>/vote/` (auth required)

### Example: Signup

```bash
curl -X POST http://127.0.0.1:8000/api/signup/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"strong-pass-123"}'
```

### Example: Create a Post

```bash
curl -X POST http://127.0.0.1:8000/api/posts/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token <your_token>" \
  -d '{"title":"Django Docs","url":"https://docs.djangoproject.com/"}'
```

## Run Tests

```bash
python manage.py test -v 2
```
