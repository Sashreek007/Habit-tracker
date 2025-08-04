from flask import request, jsonify
from db_models import db, User, Habit, HabitLog
from flask import Blueprint

habit_bp = Blueprint("habit_bp", __name__)


@habit_bp.route("/habits/<int:user_id>", methods=["GET"])
def get_habits(user_id):
    habits = Habit.query.filter_by(user_id=user_id).all()
    result = []
    for h in habits:
        result.append({"id": h.id, "name": h.name})
    return jsonify(result)


@habit_bp.route("/habits", methods=["POST"])
def create_habit():
    data = request.get_json()

    name = data.get("name")
    user_id = data.get("user_id")

    if not name or not user_id:
        return jsonify({"error": "Missing name or user_id"}), 400
    new_habit = Habit(name=name, user_id=user_id)
    db.session.add(new_habit)
    db.session.commit()

    return jsonify({"message": "Habit created", "habit_id": new_habit.id}), 201
