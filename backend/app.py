from flask import Flask, redirect, url_for
from db_models import db, User, Habit, HabitLog
from routes.habits import habit_bp

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////db/habit.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Create the tables
with app.app_context():
    db.create_all()

app.register_blueprint(habit_bp)


@app.route("/liggesh")
def home():
    return "Hello there!"


@app.route("/admin")
def admin():
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
