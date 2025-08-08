from flask import request, jsonify
from db_models import db, User
from app import app


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return jsonify({"error": "Username already taker"}), 400
    new_user = User(username=username, password=password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully!", "user_id": new_user.id}), 201
