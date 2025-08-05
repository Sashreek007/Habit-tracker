from flask import request, jsonify
from db_models import db, User, Habit, HabitLog
from flask import Blueprint
import datetime
from datetime import timedelta

habit_bp = Blueprint("habit_bp", __name__)


@habit_bp.route("/users/<int:user_id>/habits", methods=["GET"])
def get_habits(user_id):
    habits = Habit.query.filter_by(user_id=user_id).all()
    result = []
    for h in habits:
        result.append({"id": h.id, "name": h.name})
    return jsonify(result)


@habit_bp.route("/users/<int:user_id>/habits", methods=["POST"])
def create_habit(user_id):
    data = request.get_json()

    name = data.get("name")
    if not name:
        return jsonify({"error": "Missing habit name"}), 400

    existing = Habit.query.filter_by(name=name, user_id=user_id).first()
    if existing:
        return jsonify({"error": "Habit already exists"}), 400
    new_habit = Habit(name=name, user_id=user_id)
    db.session.add(new_habit)
    db.session.commit()

    return jsonify({"message": "Habit created", "habit_id": new_habit.id}), 201


@habit_bp.route("/users/<int:user_id>/habits/<int:habit_id>/checked", methods=["POST"])
def check_habit(user_id, habit_id):
    data = request.get_json()
    checked = data.get("checked", False)
    today = datetime.datetime.utcnow().date()
    habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
    if not habit:
        return jsonify({"error": "Habit not found"}), 404

    existing_log = HabitLog.query.filter_by(habit_id=habit.id, log_date=today).first()

    if checked:
        if existing_log:
            return jsonify({"message": "Already checked today"})
        new_log = HabitLog(habit_id=habit.id, log_date=today)
        db.session.add(new_log)
        db.session.commit()
        return jsonify({"message": "Checked and logged for today"})
    else:
        if existing_log:
            db.session.delete(existing_log)
            db.session.commit()
            return jsonify({"message": "Unchecked successfully"})
        else:
            return jsonify({"message": "Unchecked — no action taken"})


@habit_bp.route("/users/<int:user_id>/logs", methods=["GET"])
def get_user_logs(user_id):
    # First, get all habit IDs for the user
    user_habits = Habit.query.filter_by(user_id=user_id).all()
    if not user_habits:
        return jsonify([])

    habit_ids = [habit.id for habit in user_habits]

    # Get all logs that match those habit IDs
    logs = HabitLog.query.filter(HabitLog.habit_id.in_(habit_ids)).all()

    # Format them into JSON
    result = []
    for log in logs:
        result.append(
            {
                "log_id": log.id,
                "habit_id": log.habit_id,
                "log_date": log.log_date.isoformat(),
            }
        )

    return jsonify(result)


@habit_bp.route("/users/<int:user_id>/habits/<int:habit_id>", methods=["DELETE"])
def delete_habit(user_id, habit_id):
    habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
    if not habit:
        return jsonify({"error": "Habit not found for this user"}), 404
    db.session.delete(habit)
    db.session.commit()

    return jsonify({"message": "Habit deleted"}), 200


@habit_bp.route("/users/<int:user_id>/habits/<int:habit_id>", methods=["PUT"])
def rename_habit(user_id, habit_id):
    data = request.get_json()
    new_name = data.get("name")
    if not new_name:
        return jsonify({"error": "New name is required"}), 400

    habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
    if not habit:
        return jsonify({"error": "Habit not found for this user"}), 404

    habit.name = new_name
    db.session.commit()

    return jsonify({"message": "Habit renamed successfully"}), 200


@habit_bp.route("/users/<int:user_id>/habits/status/today", methods=["GET"])
def get_daily_status(user_id):
    today = datetime.date.today()

    habits = Habit.query.filter_by(user_id=user_id).all()
    result = []

    for habit in habits:
        log_exists = HabitLog.query.filter_by(habit_id=habit.id, log_date=today).first()
        result.append(
            {"habit_id": habit.id, "name": habit.name, "checked": bool(log_exists)}
        )

    return jsonify(result)


@habit_bp.route("/users/<int:user_id>/habits/status/weekly", methods=["GET"])
def weekly_status(user_id):
    today = datetime.date.today()
    last_7_days = []
    for i in range(6, -1, -1):
        last_7_days.append(today - timedelta(days=i))

    # Get all habits for the user
    habits = Habit.query.filter_by(user_id=user_id).all()
    if not habits:
        return jsonify([])

    habit_ids = []
    for h in habits:
        habit_ids.append(h.id)
    logs = HabitLog.query.filter(
        HabitLog.habit_id.in_(habit_ids), HabitLog.log_date.in_(last_7_days)
    ).all()

    # Build lookup for fast access
    log_lookup = {(log.habit_id, log.log_date): True for log in logs}

    response = []
    for habit in habits:
        week_log = {}
        for day in last_7_days:
            week_log[day.isoformat()] = log_lookup.get((habit.id, day), False)

        response.append(
            {"habit_id": habit.id, "name": habit.name, "week_log": week_log}
        )

    return jsonify(response)


@habit_bp.route("/users/<int:user_id>/habits/<int:habit_id>/streak", methods=["GET"])
def habit_streak(user_id, habit_id):
    habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
    if not habit:
        return jsonify({"error": "Habit not found"}), 404

    today = datetime.date.today()
    created_at = habit.created_at
    curstreak = 0
    maxstreak = 0
    streak = 0

    # Calculate current streak
    for i in range((today - created_at).days + 1):
        day = today - datetime.timedelta(days=i)
        log = HabitLog.query.filter_by(habit_id=habit.id, log_date=day).first()
        if log:
            curstreak += 1
        else:
            break

    # Calculate max streak
    for i in range((today - created_at).days + 1):
        day = created_at + datetime.timedelta(days=i)
        log = HabitLog.query.filter_by(habit_id=habit.id, log_date=day).first()
        if log:
            streak += 1
        else:
            maxstreak = max(maxstreak, streak)
            streak = 0

    maxstreak = max(maxstreak, streak)

    return jsonify(
        {
            "habit_id": habit.id,
            "habit_name": habit.name,
            "streak": curstreak,
            "maxstreak": maxstreak,
        }
    )


@habit_bp.route("/users/<int:user_id>/habits/success", methods=["GET"])
def habit_success_rate(user_id):
    habits = Habit.query.filter_by(user_id=user_id)
    today = datetime.datetime.utcnow().date()
    response = []

    for habit in habits:
        if not habit.created_at:
            continue
        total_days = (today - habit.created_at).days + 1
        logs = HabitLog.query.filter(HabitLog.habit_id == habit.id).all()
        successful_days = len(set(log.log_date for log in logs))

        success_rate = (successful_days / total_days) * 100 if total_days > 0 else 0

        response.append(
            {
                "habit_id": habit.id,
                "name": habit.name,
                "created_at": habit.created_at.strftime("%Y-%m-%d"),
                "success_rate": round(success_rate, 2),
                "checked_days": successful_days,
                "total_days": total_days,
            }
        )

    return jsonify(response)
