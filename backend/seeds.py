from app import app
from db_models import db, User, Habit, HabitLog
from datetime import date, datetime

with app.app_context():
    # ✅ Create users
    user1 = User.query.filter_by(username="testuser1").first()
    if not user1:
        user1 = User(username="testuser1", password="1234")
        db.session.add(user1)

    user2 = User.query.filter_by(username="sashreek").first()
    if not user2:
        user2 = User(username="sashreek", password="ilovecoffee")
        db.session.add(user2)

    db.session.commit()
    print("✅ Users seeded successfully.")

    # ✅ Create habits with created_at
    habit1 = Habit.query.filter_by(name="Workout", user_id=user1.id).first()
    if not habit1:
        habit1 = Habit(name="Workout", user_id=user1.id, created_at=datetime.utcnow())
        db.session.add(habit1)

    habit2 = Habit.query.filter_by(name="Dance", user_id=user1.id).first()
    if not habit2:
        habit2 = Habit(name="Dance", user_id=user1.id, created_at=datetime.utcnow())
        db.session.add(habit2)

    db.session.commit()

    # ✅ Log today for Workout
    log1 = HabitLog.query.filter_by(habit_id=habit1.id, log_date=date.today()).first()
    if not log1:
        log1 = HabitLog(habit_id=habit1.id, log_date=date.today())
        db.session.add(log1)
        db.session.commit()

    print("✅ Habits and logs seeded.")
