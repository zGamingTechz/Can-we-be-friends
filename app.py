from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import sqlite3 as sql
from models import User, db
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
    return render_template("home.html")

if __name__ == '__main__':
    app.run(debug=True)