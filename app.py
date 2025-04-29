from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import sqlite3 as sql
from models import User, db
from questions import questions
import keys

app = Flask(__name__)
app.config["SECRET_KEY"] = keys.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"

db.init_app(app)


@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']

        # Store the email in session
        session['email'] = email

        user = User.query.filter_by(email=email).first()
        if user:
            return render_template("login.html", message = "You already answered!", status = "error")

        new_user = User(
            username=username,
            email = email
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect("/home")

    return render_template("login.html", message = "Let's find out!", status = "success")


@app.route('/home', methods=["GET", "POST"])
def home():
    if 'qid' not in session:
        session['qid'] = 0

    qid = session['qid']
    user = User.query.filter_by(email=session['email']).first()

    if request.method == "POST":
        answer = request.form['answer']

        if answer.lower() == 'yes':
            answer_value = 1
            user.score += questions[qid]["points"]
        elif answer.lower() == 'no':
            answer_value = 0

        setattr(user, f'q{qid}', answer_value)
        db.session.commit()

        session['qid'] += 1
        if session['qid'] >= len(questions):
            session.pop('qid')
            return redirect()

        return redirect("/home")

    return render_template("home.html", question_text=questions[qid]["text"], qid = qid)


@app.route("/summary")
def summary():
    return render_template("summary.html")


@app.route("/clear")
def clear_session():
    session.pop("email", None)
    session.pop("qid", None)
    return "Session cleared!"


if __name__ == '__main__':
    app.run(debug=True)