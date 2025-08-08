from flask import Blueprint, request, jsonify
from db_models import (
    db,
    User,
    FriendRequest,
    Friendship,
    Habit,
    HabitLog,
    DailySuccessLog,
)
import datetime
from datetime import timedelta

friend_bp = Blueprint("friend", __name__)

# Add your routes here (send, accept, decline, list, view)


@friend_bp.route(
    "/users/<int:from_user_id>/send-request/<int:to_user_id>", methods=["POST"]
)
def send_friend_request(from_user_id, to_user_id):
    if from_user_id == to_user_id:
        return jsonify({"error": "You cannot send a friend request to yourself"}), 400

    # Check if both users exist
    from_user = User.query.get(from_user_id)
    to_user = User.query.get(to_user_id)
    if not from_user or not to_user:
        return jsonify({"error": "User not found"}), 404

    # Check if a friend request already exists
    existing = FriendRequest.query.filter_by(
        from_user_id=from_user_id, to_user_id=to_user_id
    ).first()
    if existing:
        return jsonify({"message": f"Request already {existing.status}"}), 400

    # Check if they are already friends
    already_friends = Friendship.query.filter(
        ((Friendship.user1_id == from_user_id) & (Friendship.user2_id == to_user_id))
        | ((Friendship.user1_id == to_user_id) & (Friendship.user2_id == from_user_id))
    ).first()
    if already_friends:
        return jsonify({"message": "You are already friends"}), 400

    # Create and save new friend request
    new_request = FriendRequest(from_user_id=from_user_id, to_user_id=to_user_id)
    db.session.add(new_request)
    db.session.commit()

    return jsonify({"message": "Friend request sent successfully"}), 201


@friend_bp.route(
    "/users/<int:user_id>/accept-request/<int:request_id>", methods=["POST"]
)
def accept_friend_request(user_id, request_id):
    friend_request = FriendRequest.query.get(request_id)

    if not friend_request:
        return jsonify({"error": "Friend request not found"}), 404

    if friend_request.to_user_id != user_id:
        return jsonify({"error": "You are not authorized to accept this request"}), 403

    if friend_request.status == "accepted":
        return jsonify({"message": "Friend request already accepted"}), 400

    # Update request status
    friend_request.status = "accepted"

    # Add friendship one way (we query both directions when checking)
    friendship = Friendship(
        user1_id=min(friend_request.from_user_id, friend_request.to_user_id),
        user2_id=max(friend_request.from_user_id, friend_request.to_user_id),
    )
    db.session.add(friendship)
    db.session.commit()

    return jsonify({"message": "Friend request accepted"}), 200


@friend_bp.route(
    "/users/<int:user_id>/decline-request/<int:request_id>", methods=["POST"]
)
def decline_friend_request(user_id, request_id):
    friend_request = FriendRequest.query.get(request_id)

    if not friend_request:
        return jsonify({"error": "Friend request not found"}), 404

    if friend_request.to_user_id != user_id:
        return jsonify({"error": "You are not authorized to decline this request"}), 403

    if friend_request.status == "declined":
        return jsonify({"message": "Friend request already declined"}), 400

    # Update request status
    friend_request.status = "declined"
    db.session.commit()

    return jsonify({"message": "Friend request declined"}), 200


@friend_bp.route("/users/<int:user_id>/friend-requests", methods=["GET"])
def all_friend_requests(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Received Requests
    received_requests = FriendRequest.query.filter_by(
        to_user_id=user_id, status="pending"
    ).all()

    received = [
        {
            "request_id": r.id,
            "from_user_id": r.from_user_id,
            "from_username": User.query.get(r.from_user_id).username,
            "status": r.status,
        }
        for r in received_requests
    ]

    # Sent Requests
    sent_requests = FriendRequest.query.filter_by(
        from_user_id=user_id, status="pending"
    ).all()

    sent = [
        {
            "request_id": r.id,
            "to_user_id": r.to_user_id,
            "to_username": User.query.get(r.to_user_id).username,
            "status": r.status,
        }
        for r in sent_requests
    ]

    return jsonify({"received_requests": received, "sent_requests": sent}), 200


@friend_bp.route("/friends/<int:user_id>/profile/<int:friend_id>", methods=["GET"])
def view_friend_profile(user_id, friend_id):
    # Check if they are friends
    is_friend = Friendship.query.filter(
        ((Friendship.user1_id == user_id) & (Friendship.user2_id == friend_id))
        | ((Friendship.user1_id == friend_id) & (Friendship.user2_id == user_id))
    ).first()
    if not is_friend:
        return jsonify({"error": "Not friends"}), 403

    friend = User.query.get(friend_id)
    if not friend:
        return jsonify({"error": "User not found"}), 404

    today = datetime.date.today()
    habits = Habit.query.filter_by(user_id=friend_id).all()
    habits_info = []

    for habit in habits:
        log_dates = [
            log.log_date
            for log in HabitLog.query.filter_by(habit_id=habit.id)
            .order_by(HabitLog.log_date)
            .all()
        ]

        total_days = (today - habit.created_at).days + 1
        checked_days = len(set(log_dates))
        success_rate = (
            round((checked_days / total_days) * 100, 2) if total_days > 0 else 0
        )

        # Calculate streak
        cur_streak = 0
        for i in range((today - habit.created_at).days + 1):
            day = today - timedelta(days=i)
            if day in log_dates:
                cur_streak += 1
            else:
                break

        # Calculate max streak
        max_streak = 0
        temp_streak = 0
        for i in range((today - habit.created_at).days + 1):
            day = habit.created_at + timedelta(days=i)
            if day in log_dates:
                temp_streak += 1
                max_streak = max(max_streak, temp_streak)
            else:
                temp_streak = 0

        habits_info.append(
            {
                "habit_id": habit.id,
                "name": habit.name,
                "created_at": habit.created_at.strftime("%Y-%m-%d"),
                "total_days": total_days,
                "checked_days": checked_days,
                "success_rate": success_rate,
                "streak": cur_streak,
                "max_streak": max_streak,
            }
        )

    # Daily success log (heatmap view)
    daily_logs = (
        DailySuccessLog.query.filter_by(user_id=friend_id)
        .order_by(DailySuccessLog.date)
        .all()
    )
    success_log = [
        {"date": log.date.isoformat(), "success_rate": log.success_rate}
        for log in daily_logs
    ]

    return jsonify(
        {
            "friend_id": friend.id,
            "friend_username": friend.username,
            "habits": habits_info,
            "daily_success_log": success_log,
        }
    ), 200
