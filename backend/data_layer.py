import json
from typing import Any

POSTS_FILE = "posts.json"


def load_posts() -> list[dict[str, Any]]:
    """Load posts from the JSON file and return them as a list."""
    try:
        with open(POSTS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        return []

    except json.JSONDecodeError:
        return []


def save_posts(posts: list[dict[str, Any]]) -> None:
    """Save the given list of posts to the JSON file."""
    with open(POSTS_FILE, "w", encoding="utf-8") as file:
        json.dump(posts, file, indent=2, ensure_ascii=False)
