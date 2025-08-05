from app import app
from db_models import db, User, Habit, HabitLog
from datetime import date, datetime, timedelta
import random

with app.app_context():
    # ✅ Create users
    usernames = [
        ("testuser1", "1234"),
        ("sashreek", "ilovecoffee"),
        ("amy", "pass123"),
        ("john", "letmein"),
        ("zoe", "coffee123"),
    ]

    user_objs = {}
    for uname, pwd in usernames:
        user = User.query.filter_by(username=uname).first()
        if not user:
            user = User(username=uname, password=pwd)
            db.session.add(user)
        user_objs[uname] = user
    db.session.commit()
    print("✅ Users created")

    # ✅ Create habits for each user
    user_habits = {
        "testuser1": ["Workout", "Dance"],
        "sashreek": ["Read", "Code"],
        "amy": ["Run", "Yoga"],
        "john": ["Meditate", "Swim"],
        "zoe": ["Write", "Draw"],
    }

    for uname, habits in user_habits.items():
        for habit_name in habits:
            habit = Habit.query.filter_by(
                name=habit_name, user_id=user_objs[uname].id
            ).first()
            if not habit:
                created_at = datetime.utcnow() - timedelta(days=7)
                db.session.add(
                    Habit(
                        name=habit_name,
                        user_id=user_objs[uname].id,
                        created_at=created_at,
                    )
                )
    db.session.commit()
    print("✅ Habits created")

    # ✅ Add logs randomly for last 7 days
    all_habits = Habit.query.all()
    for habit in all_habits:
        for i in range(7):
            log_date = date.today() - timedelta(days=i)
            if random.random() < 0.5:
                exists = HabitLog.query.filter_by(
                    habit_id=habit.id, log_date=log_date
                ).first()
                if not exists:
                    db.session.add(HabitLog(habit_id=habit.id, log_date=log_date))
    db.session.commit()
    print("✅ Logs created")
