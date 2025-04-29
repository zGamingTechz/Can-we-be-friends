from app import app
from models import db


def create_tables():
    with app.app_context():
        db.create_all()


create_tables()
