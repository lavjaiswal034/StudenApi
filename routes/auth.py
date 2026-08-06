from flask import Blueprint, request
import os
from werkzeug.utils import secure_filename
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    get_jwt_identity,
    get_jwt
)
auth = Blueprint("auth", __name__)

UPLOAD_FOLDER = "uploads"
# ---------------- REGISTER ----------------

@auth.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:
        return {"error": "Request body is required"}, 400

    if not data.get("username"):
        return {"error": "Username is required"}, 400

    if not data.get("email"):
        return {"error": "Email is required"}, 400

    if not data.get("password"):
        return {"error": "Password is required"}, 400

    # Check if email already exists
    existing_user = User.query.filter_by(email=data["email"]).first()

    if existing_user:
        return {"error": "Email already registered"}, 409

    user = User(
        username=data["username"],
        email=data["email"],
        password=generate_password_hash(data["password"]),
        role=data.get("role", "student")
    )

    db.session.add(user)
    db.session.commit()

    return {
        "message": "User Registered Successfully",
        "id": user.id
    }, 201


# ---------------- LOGIN ----------------

@auth.route("/login", methods=["POST"])
def login():
    """
Login User
---
tags:
  - Authentication

parameters:
  - in: body
    name: body
    required: true
    schema:
      type: object
      properties:
        email:
          type: string
        password:
          type: string

responses:
  200:
    description: Login Successful
"""
    data = request.get_json()

    if not data:
        return {"error": "Request body is required"}, 400

    if not data.get("email"):
        return {"error": "Email is required"}, 400

    if not data.get("password"):
        return {"error": "Password is required"}, 400

    user = User.query.filter_by(email=data["email"]).first()

    if user is None:
        return {"error": "Invalid Email or Password"}, 401

    if not check_password_hash(user.password, data["password"]):
        return {"error": "Invalid Email or Password"}, 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role
        }
    )

    return {
        "message": "Login Successful",
        "access_token": token
    }

# ---------------- FILE UPLOAD ----------------
@auth.route("/upload", methods=["POST"])
def upload_file():

    # Check if file exists in request
    if "file" not in request.files:
        return {
            "error": "No file uploaded"
        }, 400

    file = request.files["file"]

    # Check if filename is empty
    if file.filename == "":
        return {
            "error": "No file selected"
        }, 400

    # Make filename safe
    filename = secure_filename(file.filename)

    # Create full path
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # Save file
    file.save(filepath)

    return {
        "message": "File uploaded successfully",
        "filename": filename
    }, 201
# ---------------- PROFILE ----------------

@auth.route("/profile", methods=["GET"])
@jwt_required()
def profile():

    user_id = get_jwt_identity()

    claims = get_jwt()

    return {
        "user_id": user_id,
        "role": claims["role"]
    }