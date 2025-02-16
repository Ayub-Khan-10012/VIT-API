from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, get_jwt
)
from werkzeug.utils import secure_filename
import os
from app import app, db
from app.models import User, Assignment, Feedback
from werkzeug.security import generate_password_hash, check_password_hash

# Allowed roles
ALLOWED_ROLES = ["Student", "Faculty", "Contributor"]

# Store revoked tokens (for simplicity, use a set; in production, use a database)
revoked_tokens = set()

# ✅ Register Route
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not all(k in data for k in ("username", "password", "role")):
        return jsonify({"message": "Missing required fields"}), 400

    if data["role"] not in ALLOWED_ROLES:
        return jsonify({"message": "Invalid role. Allowed roles: Student, Faculty, Contributor"}), 400

    hashed_password = generate_password_hash(data["password"])
    new_user = User(username=data["username"], password=hashed_password, role=data["role"])

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": f"User {data['username']} registered successfully as {data['role']}!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ✅ Login Route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not all(k in data for k in ("username", "password")):
        return jsonify({"message": "Missing required fields"}), 400

    user = User.query.filter_by(username=data["username"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"message": "Invalid username or password"}), 401

    access_token = create_access_token(identity=user.username, additional_claims={"role": user.role})
    
    return jsonify({"message": "Login successful!", "token": access_token}), 200

# ✅ Logout Route (Blacklist Token)
@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  # JWT unique identifier
    revoked_tokens.add(jti)  # Add token to blacklist
    return jsonify({"message": "Logout successful!"}), 200

# ✅ Protected Route (Requires Authentication)
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    jti = get_jwt()["jti"]
    if jti in revoked_tokens:
        return jsonify({"message": "Token has been revoked. Please log in again."}), 401

    current_user = get_jwt_identity()
    claims = get_jwt()

    if claims["role"] not in ALLOWED_ROLES:
        return jsonify({"message": "Access denied! Your role is not allowed."}), 403

    return jsonify({"message": f"Welcome {current_user} to the protected route!", "role": claims["role"]}), 200

# ✅ Dashboard Route
@app.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    jti = get_jwt()["jti"]
    if jti in revoked_tokens:
        return jsonify({"message": "Token has been revoked. Please log in again."}), 401

    current_user = get_jwt_identity()
    claims = get_jwt()

    return jsonify({"message": f"Welcome {current_user}!", "role": claims["role"]}), 200

# ✅ Retrieve All Users (GET)
@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    jti = get_jwt()["jti"]
    if jti in revoked_tokens:
        return jsonify({"message": "Token has been revoked. Please log in again."}), 401

    users = User.query.all()
    users_data = [{"id": user.id, "username": user.username, "role": user.role} for user in users]
    return jsonify({"users": users_data}), 200

# ✅ Retrieve Specific User (GET)
@app.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    jti = get_jwt()["jti"]
    if jti in revoked_tokens:
        return jsonify({"message": "Token has been revoked. Please log in again."}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify({"id": user.id, "username": user.username, "role": user.role}), 200

# ✅ Add User (POST) - Only Faculty Can Add Users
@app.route('/users', methods=['POST'])
@jwt_required()
def add_user():
    jti = get_jwt()["jti"]
    if jti in revoked_tokens:
        return jsonify({"message": "Token has been revoked. Please log in again."}), 401

    claims = get_jwt()
    if claims["role"] != "Faculty":
        return jsonify({"message": "Only Faculty can add users"}), 403

    data = request.get_json()
    if not data or not all(k in data for k in ("username", "password", "role")):
        return jsonify({"message": "Missing required fields"}), 400

    if data["role"] not in ALLOWED_ROLES:
        return jsonify({"message": "Invalid role"}), 400

    hashed_password = generate_password_hash(data["password"])
    new_user = User(username=data["username"], password=hashed_password, role=data["role"])

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ✅ Update User (PUT) - Only Faculty Can Update Users
@app.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    jti = get_jwt()["jti"]
    if jti in revoked_tokens:
        return jsonify({"message": "Token has been revoked. Please log in again."}), 401

    claims = get_jwt()
    if claims["role"] != "Faculty":
        return jsonify({"message": "Only Faculty can update users"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    if "username" in data:
        user.username = data["username"]
    if "role" in data and data["role"] in ALLOWED_ROLES:
        user.role = data["role"]

    try:
        db.session.commit()
        return jsonify({"message": "User updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ✅ Delete User (DELETE) - Only Faculty Can Delete Users
@app.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    jti = get_jwt()["jti"]
    if jti in revoked_tokens:
        return jsonify({"message": "Token has been revoked. Please log in again."}), 401

    claims = get_jwt()
    if claims["role"] != "Faculty":
        return jsonify({"message": "Only Faculty can delete users"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ✅ Assignment Submission Route (Only Students Can Submit)
UPLOAD_FOLDER = r"C:\24MCS1047\Sem - 2\Application Architecture and Deployment\vit-api\app\Assignments"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/assignments', methods=['POST'])
@jwt_required()
def submit_assignment():
    jti = get_jwt()["jti"]
    if jti in revoked_tokens:
        return jsonify({"message": "Token has been revoked. Please log in again."}), 401

    # Fetch the full user object
    current_user = User.query.filter_by(username=get_jwt_identity()).first()

    if not current_user or current_user.role != "Student":
        return jsonify({"message": "Only students can submit assignments"}), 403

    # Get the file from the request
    if 'assignment_file' not in request.files:
        return jsonify({"message": "No file part"}), 400
    file = request.files['assignment_file']
    
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Create a new assignment record in the database
        new_assignment = Assignment(
            student_id=current_user.id,  # Use student_id from the current user
            title="Assignment Title",  # Add title as per your requirement
            description="Assignment Description",  # Add description as per your requirement
            file_url=filepath
        )
        db.session.add(new_assignment)
        db.session.commit()

        return jsonify({"message": "Assignment submitted successfully!"}), 201

# ✅ Faculty Feedback Route (Only Faculty Can Provide Feedback)
@app.route('/assignments/<int:assignment_id>/feedback', methods=['POST'])
@jwt_required()
def provide_feedback(assignment_id):
    jti = get_jwt()["jti"]
    if jti in revoked_tokens:
        return jsonify({"message": "Token has been revoked. Please log in again."}), 401

    claims = get_jwt()
    if claims["role"] != "Faculty":
        return jsonify({"message": "Only faculty can provide feedback"}), 403

    # Retrieve the assignment from the database
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({"message": "Assignment not found"}), 404

    data = request.get_json()
    if "feedback" not in data:
        return jsonify({"message": "Feedback is required"}), 400

    # Add the feedback to the assignment
    assignment.feedback = data["feedback"]  # Update the feedback field of the assignment
    db.session.commit()

    return jsonify({"message": "Feedback provided successfully!"}), 200

# ✅ Home Route
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Flask API is running successfully!"}), 200

# ✅ Test DB Route
@app.route('/test-db', methods=['GET'])
def test_db():
    try:
        db.session.execute("SELECT 1")
        return jsonify({"message": "Database connection successful!"}), 200
    except Exception as e:
        return jsonify({"error": f"Database connection failed: {str(e)}"}), 500