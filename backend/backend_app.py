from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from data_layer import load_posts, save_posts

app = Flask(__name__)
CORS(app)

POST_FIELDS = ["title", "content", "author", "date"]
REQUIRED_FIELDS = POST_FIELDS

SWAGGER_URL = "/api/docs"
API_URL = "/static/masterblog.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


def validate_post_data(data, required_fields=None):
    """Validate post data and strip leading and trailing whitespace."""
    if not isinstance(data, dict) or not data:
        return None, {"error": "Request body is missing."}

    if required_fields is None:
        required_fields = []

    missing_fields = [
        field for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return None, {
            "error": "Missing required fields.",
            "missing": missing_fields
        }

    for field in data:
        if field not in POST_FIELDS:
            return None, {"error": f"Invalid field: {field}."}

        if not isinstance(data[field], str):
            return None, {
                "error": f"Field '{field}' must be a string."
            }

        data[field] = data[field].strip()

        if not data[field]:
            return None, {
                "error": f"Field '{field}' must not be empty."
            }

    if "date" in data:
        try:
            datetime.strptime(data["date"], "%Y-%m-%d")
        except ValueError:
            return None, {
                "error": "Invalid date format. Use YYYY-MM-DD."
            }

    return data, None


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Return all posts, optionally sorted by a specified field and direction."""
    sort = request.args.get('sort')
    direction = request.args.get('direction')

    posts = load_posts()

    if sort is None and direction is None:
        return jsonify(posts)

    if sort not in POST_FIELDS:
        return jsonify({"error": "Invalid sort field."}), 400
    if direction not in ["asc", "desc"]:
        return jsonify({"error": "Invalid direction."}), 400

    if sort == "date":
        sorted_posts = sorted(posts, key=lambda post: datetime.strptime(post["date"], "%Y-%m-%d"),
                              reverse=(direction == "desc"))
    else:
        sorted_posts = sorted(posts, key=lambda post: post[sort].lower(), reverse=(direction == "desc"))

    return jsonify(sorted_posts), 200


@app.route('/api/posts', methods=['POST'])
def add_post():
    """Validate the request data and create a new post."""
    data, error = validate_post_data(
        request.get_json(silent=True),
        required_fields=REQUIRED_FIELDS
    )

    if error:
        return jsonify(error), 400

    posts = load_posts()
    new_id = max([post["id"] for post in posts], default=0) + 1

    new_post = {
        "id": new_id,
        **data
    }

    posts.append(new_post)
    save_posts(posts)

    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Delete the post with the specified ID."""
    posts = load_posts()
    post = next((post for post in posts if post["id"] == post_id), None)

    if post is None:
        return jsonify({"message": f"Post with id {post_id} was not found."}), 404

    posts.remove(post)
    save_posts(posts)

    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """Validate and update an existing post."""
    posts = load_posts()
    post = next(
        (post for post in posts if post["id"] == post_id),
        None
    )

    if post is None:
        return jsonify({
            "message": f"Post with id {post_id} was not found."
        }), 404

    data, error = validate_post_data(request.get_json(silent=True))

    if error:
        return jsonify(error), 400

    post.update(data)
    save_posts(posts)

    return jsonify(post), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """Search posts by title and/or content."""
    title_query = request.args.get('title', '').strip().lower()
    content_query = request.args.get('content', '').strip().lower()

    if not title_query and not content_query:
        return jsonify([]), 200

    posts = load_posts()
    results = []

    for post in posts:
        title_matches = (
                title_query and title_query in post["title"].lower()
        )
        content_matches = (
                content_query and content_query in post["content"].lower()
        )

        if title_matches or content_matches:
            results.append(post)

    return jsonify(results), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
