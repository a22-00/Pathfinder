from flask import Blueprint, request, jsonify
# from ..models import user as user_model # If you use models from one level up
# from flask_login import login_user, logout_user # If using Flask-Login

auth_bp = Blueprint('auth_routes', __name__) 

@auth_bp.route('/register', methods=['POST'])
def register_user_route():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    user_type = data.get('user_type', 'student')

    if not all([username, email, password]):
        return jsonify({"error": "Missing username, email, or password"}), 400
    
    print(f"ROUTE: Registering user {username}") 
    return jsonify({"message": "User registration placeholder", "username": username}), 201

@auth_bp.route('/login', methods=['POST'])
def login_user_route():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({"error": "Missing username or password"}), 400

    print(f"ROUTE: Logging in user {username}") 
    if username == "testuser" and password == "password123": 
         return jsonify({"message": "Login successful placeholder", "user_id": "user_test123"}), 200
    return jsonify({"error": "Invalid credentials placeholder"}), 401


@auth_bp.route('/logout', methods=['POST'])
def logout_user_route():
    print("ROUTE: Logging out user") 
    return jsonify({"message": "Logout successful"}), 200

