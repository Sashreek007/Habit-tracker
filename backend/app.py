from flask import Flask, redirect, url_for
from db_models import db, User, Habit, HabitLog
from routes.habits import habit_bp
import os
import time
import psycopg2
from sqlalchemy.exc import OperationalError
from routes.friends import friend_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
for _ in range(10):
    try:
        with app.app_context():
            db.create_all()
        break
    except OperationalError:
        print("Waiting for DB to be ready...")
        time.sleep(2)

app.register_blueprint(habit_bp)
app.register_blueprint(friend_bp)


@app.route("/liggesh")
def home():
    return "Hello there!"


@app.route("/admin")
def admin():
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
