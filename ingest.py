# Standard library imports
import json
import time

# Third-party library for making HTTP requests
import httpx

# Configuration constants — change values here, not inside the logic below
BASE_URL = "https://openlibrary.org/search.json"
QUERY = "data engineering"
LIMIT_PER_PAGE = 20
MAX_BOOKS = 60
OUTPUT_FILE = "books.json"

def fetch_page(page: int) -> dict:
    """Fetch one page of results, retrying on rate limit (429)."""
    params = {"q": QUERY, "page": page, "limit": LIMIT_PER_PAGE}

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        response = httpx.get(BASE_URL, params=params, timeout=10)

        if response.status_code == 429:
            # Respect Retry-After if the server sends it, otherwise use exponential backoff
            wait_seconds = int(response.headers.get("Retry-After", 2 ** attempt))
            print(f"  Rate limited. Waiting {wait_seconds}s before retrying...")
            time.sleep(wait_seconds)
            continue

        # Raises an exception for other 4xx/5xx errors (not 429, already handled above)
        response.raise_for_status()
        return response.json()

    raise RuntimeError(f"Failed after {max_retries} retries (page {page})")

def main():
    books = []
    page = 1

    while len(books) < MAX_BOOKS:
        print(f"Fetching page {page}...")
        data = fetch_page(page)
        docs = data.get("docs", [])

        # No more results from the source — stop instead of looping forever
        if not docs:
            print("No more results, stopping.")
            break

        for doc in docs:
            books.append(
                {
                    "id": len(books) + 1,  # our own API's id, not Open Library's
                    "openlibrary_key": doc.get("key"),
                    "title": doc.get("title"),
                    "author": (doc.get("author_name") or ["unknown"])[0],
                    "first_publish_year": doc.get("first_publish_year"),
                }
            )
            if len(books) >= MAX_BOOKS:
                break

        page += 1
        time.sleep(0.2)  # small pause between pages, polite to the API

    # Save everything collected to a local JSON file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

    print(f"\n{len(books)} books saved to {OUTPUT_FILE}")


# Only runs main() when this file is executed directly, not when imported
if __name__ == "__main__":
    main()