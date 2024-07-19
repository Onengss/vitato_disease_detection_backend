from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from model.model import db, User

bp = Blueprint('auth', __name__)


@bp.route("/signin", methods=["POST"])
def signin():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    # Validate the email and password with your database
    user = User.query.filter_by(email=email, password=password).first()

    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    user_details = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }

    access_token = create_access_token(user_details)
    refresh_token = create_refresh_token(user_details)

    if email == "admin@gmail.com":
        role = "admin"
    else:
        role = "user"

    return jsonify({
        "role": role,
        "token": {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    }), 200


@bp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    print(
        f"Received data: username={username}, email={email}, password={password}")

    if not username or not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    new_user = User(username=username, email=email, password=password)

    try:
        db.session.add(new_user)
        db.session.commit()
        print("User added to database")
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error adding user to database: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)
