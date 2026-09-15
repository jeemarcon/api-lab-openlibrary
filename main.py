# Standard library
import json

# FastAPI itself
from fastapi import FastAPI

import os
from dotenv import load_dotenv

# Loads variables from .env into the environment
load_dotenv()

API_KEY = os.getenv("API_KEY")

# Create the application instance — this object is what uvicorn runs
app = FastAPI(title="Book Catalog API")


def load_books() -> list[dict]:
    """Load books from the JSON file produced by ingest.py."""
    with open("books.json", "r", encoding="utf-8") as f:
        return json.load(f)


# Loaded once when the server starts, kept in memory — no database for this practice project
books_db = load_books()

from fastapi import Query

@app.get("/books")
def list_books(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    """Return a paginated slice of the book catalog."""
    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total": len(books_db),
        "results": books_db[start:end],
    }

from fastapi import HTTPException

@app.get("/books/{book_id}")
def get_book(book_id: int):
    """Return a single book by its id, or 404 if it doesn't exist."""
    for book in books_db:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")

from pydantic import BaseModel

# Defines the shape and validation rules for a new book request
class BookCreate(BaseModel):
    title: str
    author: str
    first_publish_year: int | None = None


from fastapi import Header, Depends

# Dependency: FastAPI runs this BEFORE the route's own code
def verify_api_key(x_api_key: str = Header(...)):
    """Validate the API key sent in the 'x-api-key' request header."""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.post("/books", status_code=201)
def create_book(book: BookCreate, auth: None = Depends(verify_api_key)):
    """Create a new book and add it to the in-memory catalog."""
    new_id = max((b["id"] for b in books_db), default=0) + 1

    new_book = {
        "id": new_id,
        "openlibrary_key": None,
        "title": book.title,
        "author": book.author,
        "first_publish_year": book.first_publish_year,
    }

    books_db.append(new_book)
    return new_book

