# API Lab — Open Library

A small study project to practice both sides of working with APIs: **consuming** an external API (Open Library) and **building** one (FastAPI).

## What it does

1. `ingest.py` fetches book data from the [Open Library Search API](https://openlibrary.org/dev/docs/api/search) and saves it to `books.json`.
2. `main.py` serves that data through a local FastAPI app, with endpoints to list, retrieve, and create books.

## Tech stack

- Python 3
- [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/)
- [httpx](https://www.python-httpx.org/) for HTTP requests
- [python-dotenv](https://pypi.org/project/python-dotenv/) for environment variables

## Setup

```bash
# create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS/Linux

# install dependencies
pip install -r requirements.txt
```

Create a `.env` file in the project root with an API key (used to authorize `POST /books`):

```
API_KEY=your-secret-key
```

## Usage

### 1. Ingest data from Open Library

```bash
python ingest.py
```

This fetches books matching the query defined in `ingest.py` and writes them to `books.json`.

### 2. Run the API

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Interactive docs at `http://127.0.0.1:8000/docs`.

## Endpoints

| Method | Path            | Auth | Description                          |
|--------|-----------------|------|---------------------------------------|
| GET    | `/books`        | No   | List books, paginated (`page`, `limit`) |
| GET    | `/books/{id}`   | No   | Get a single book by id               |
| POST   | `/books`        | Yes  | Create a new book                     |

### Examples

List books:
```bash
curl "http://127.0.0.1:8000/books?page=1&limit=10"
```

Get a single book:
```bash
curl "http://127.0.0.1:8000/books/1"
```

Create a book (requires `x-api-key` header matching `API_KEY` in `.env`):
```bash
curl -X POST "http://127.0.0.1:8000/books" \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-secret-key" \
  -d '{"title": "Clean Code", "author": "Robert C. Martin", "first_publish_year": 2008}'
```

## Notes

- Data is kept in memory (loaded from `books.json` on startup) — there's no database, and new books added via `POST` are lost on restart.
- This is a learning project, not intended for production use.
