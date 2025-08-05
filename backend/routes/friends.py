from flask import Blueprint, request, jsonify
from db_models import db, User, FriendRequest, Friendship

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
