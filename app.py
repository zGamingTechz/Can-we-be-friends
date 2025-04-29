from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import sqlite3 as sql
from models import User, db
import keys

app = Flask(__name__)
app.config["SECRET_KEY"] = keys.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"

db.init_app(app)


@app.route('/')
def index():
    return 'Hello world'


if __name__ == '__main__':
    app.run(debug=True)