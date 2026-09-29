from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from flask_swagger_ui import get_swaggerui_blueprint
import json

app = Flask(__name__)
CORS(app)

SWAGGER_URL="/api/docs"  # (1) swagger endpoint e.g. HTTP://localhost:5002/api/docs
API_URL="/static/masterblog.json" # (2) ensure you create this dir and file

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API' # (3) You can change this if you like
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

POSTS_FILE = "posts.json"

def load_posts():
    try:
        with open(POSTS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        return []

    except json.JSONDecodeError:
        return []

def save_posts(posts):
    with open(POSTS_FILE, "w", encoding="utf-8") as file:
        json.dump(posts, file, indent=2, ensure_ascii=False)


@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort = request.args.get('sort')
    direction = request.args.get('direction')

    posts = load_posts()

    if sort is None and direction is None:
        return jsonify(posts)

    allowed_fields = ["title", "content", "author", "date"]

    if sort not in allowed_fields:
        return jsonify({"error": "Invalid sort field."}), 400
    if direction not in ["asc", "desc"]:
        return jsonify({"error": "Invalid direction."}), 400

    if sort == "date":
        sorted_posts = sorted(posts, key=lambda post: datetime.strptime(post["date"],"%Y-%m-%d"), reverse=(direction == "desc"))
    else:
        sorted_posts = sorted(posts, key=lambda post: post[sort].lower(), reverse=(direction == "desc"))

    return jsonify(sorted_posts), 200

@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is missing."}), 400

    required_fields = ["title", "content", "author", "date"]
    missing_fields = []

    for field in required_fields:
        if field not in data:
            missing_fields.append(field)

    if missing_fields:
        return jsonify({"error": "Missing required fields.", "missing": missing_fields}), 400

    try:
        datetime.strptime(data["date"], "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    posts = load_posts()
    new_id = max([post["id"] for post in posts], default=0) + 1

    new_post = {
        "id": new_id,
        "title": data["title"],
        "content": data["content"],
        "author": data["author"],
        "date": data["date"]
    }

    posts.append(new_post)
    save_posts(posts)

    return jsonify(new_post), 201

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    posts = load_posts()
    post = next((post for post in posts if post["id"] == post_id), None)

    if post is None:
        return jsonify({"message": f"Post with id {post_id} was not found."}), 404

    posts.remove(post)
    save_posts(posts)

    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    posts = load_posts()
    post = next((post for post in posts if post["id"] == post_id), None)

    if post is None:
        return jsonify({"message": f"Post with id {post_id} was not found."}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is missing."}), 400

    if "title" in data:
        post["title"] = data["title"]
    if "content" in data:
        post["content"] = data["content"]
    if "author" in data:
        post["author"] = data["author"]
    if "date" in data:
        try:
            datetime.strptime(data["date"], "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        post["date"] = data["date"]

    save_posts(posts)

    return jsonify(post), 200

@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    search_query = request.args.get('search')

    if not search_query:
        return jsonify([])

    search_query = search_query.lower()

    results = []

    posts = load_posts()

    for post in posts:
        if any(search_query in post[field].lower() for field in ["title", "content", "author", "date"]):
            results.append(post)

    return jsonify(results), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
