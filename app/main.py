from flask import Flask, jsonify, request, render_template, abort, make_response
from datetime import datetime
import json
import os

app = Flask(__name__)

users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com", "created_at": "2024-01-01"},
    {"id": 2, "name": "Bob", "email": "bob@example.com", "created_at": "2024-01-02"},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com", "created_at": "2024-01-03"}
]

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to Enhanced Flask API!",
        "version": "1.0.0",
        "time": datetime.now().isoformat(),
        "endpoints": {
            "GET /": "This information",
            "GET /health": "Health check",
            "GET /users": "List all users",
            "GET /users/<id>": "Get specific user",
            "POST /users": "Create new user",
            "PUT /users/<id>": "Update user",
            "DELETE /users/<id>": "Delete user",
            "GET /search?q=<query>": "Search users",
            "GET /about": "About page (HTML)",
            "GET /api/stats": "API statistics"
        }
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify({
        "users": users,
        "count": len(users),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if user:
        return jsonify(user)
    else:
        abort(404, description=f"User with ID {user_id} not found")

@app.route('/users', methods=['POST'])
def create_user():
    if not request.json:
        abort(400, description="Request must be JSON")
    
    if 'name' not in request.json or 'email' not in request.json:
        abort(400, description="Missing required fields: name, email")
    
    new_user = {
        "id": max([u["id"] for u in users]) + 1 if users else 1,
        "name": request.json['name'],
        "email": request.json['email'],
        "created_at": datetime.now().isoformat()
    }
    users.append(new_user)
    
    return jsonify({
        "message": "User created successfully",
        "user": new_user
    }), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        abort(404, description=f"User with ID {user_id} not found")
    
    if not request.json:
        abort(400, description="Request must be JSON")
    
    user['name'] = request.json.get('name', user['name'])
    user['email'] = request.json.get('email', user['email'])
    user['updated_at'] = datetime.now().isoformat()
    
    return jsonify({
        "message": "User updated successfully",
        "user": user
    })

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    global users
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        abort(404, description=f"User with ID {user_id} not found")
    
    users = [u for u in users if u["id"] != user_id]
    return jsonify({
        "message": f"User {user_id} deleted successfully",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/search', methods=['GET'])
def search_users():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({
            "error": "Please provide a search query parameter 'q'",
            "example": "/search?q=alice"
        }), 400
    
    results = [u for u in users if query in u['name'].lower() or query in u['email'].lower()]
    return jsonify({
        "query": query,
        "results": results,
        "count": len(results),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/about')
def about():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>About - Flask API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f4f4f4;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #333; }
            .feature { margin: 10px 0; }
            .timestamp { color: #666; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Enhanced Flask API</h1>
            <p>This is a fully featured Flask application with:</p>
            <div class="feature">✅ RESTful API endpoints</div>
            <div class="feature">✅ CRUD operations</div>
            <div class="feature">✅ Search functionality</div>
            <div class="feature">✅ Error handling</div>
            <div class="feature">✅ JSON responses</div>
            <div class="feature">✅ In-memory data storage</div>
            <hr>
            <p class="timestamp">Server Time: %s</p>
            <p><a href="/">View API Documentation</a></p>
        </div>
    </body>
    </html>
    """ % datetime.now().isoformat()
    return html

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Resource not found",
        "message": str(error.description) if hasattr(error, 'description') else "The requested resource does not exist",
        "timestamp": datetime.now().isoformat()
    }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "error": "Bad request",
        "message": str(error.description) if hasattr(error, 'description') else "Invalid request",
        "timestamp": datetime.now().isoformat()
    }), 400

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "error": "Method not allowed",
        "message": "The HTTP method used is not supported for this endpoint",
        "timestamp": datetime.now().isoformat()
    }), 405

@app.before_request
def log_request():
    print(f"[{datetime.now().isoformat()}] {request.method} {request.path} - {request.remote_addr}")

@app.after_request
def add_headers(response):
    response.headers['X-API-Version'] = '1.0.0'
    response.headers['X-Server-Time'] = datetime.now().isoformat()
    return response

@app.route('/api/stats')
def api_stats():
    return jsonify({
        "total_users": len(users),
        "timestamp": datetime.now().isoformat(),
        "api_version": "1.0.0",
        "status": "operational"
    })

@app.route('/api/time')
def get_time():
    now = datetime.now()
    return jsonify({
        "iso": now.isoformat(),
        "timestamp": now.timestamp(),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": "UTC"
    })

@app.route('/echo', methods=['GET', 'POST'])
def echo():
    return jsonify({
        "method": request.method,
        "headers": dict(request.headers),
        "args": request.args.to_dict(),
        "json": request.json if request.is_json else None,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/status/<int:code>')
def test_status(code):
    messages = {
        200: "OK",
        201: "Created",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        500: "Internal Server Error"
    }
    return jsonify({
        "status": code,
        "message": messages.get(code, "Unknown status"),
        "timestamp": datetime.now().isoformat()
    }), code

if __name__ == '__main__':
    print("=" * 50)
    print(" Enhanced Flask API Server")
    print("=" * 50)
    print(f" Running on: http://127.0.0.1:5001")
    print(f" API Documentation: http://127.0.0.1:5001/")
    print(f" Health Check: http://127.0.0.1:5001/health")
    print(f" Users: http://127.0.0.1:5001/users")
    print(f" Server Time: {datetime.now().isoformat()}")
    print("=" * 50)
    app.run(debug=True, host='127.0.0.1', port=5001)
