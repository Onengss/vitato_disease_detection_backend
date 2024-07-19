from numpy import False_
from extension.extension import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    predicts = db.relationship('Predict', backref='User')


class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    feedback = db.Column(db.Text, nullable=False)


class Predict(db.Model):
    __tablename__ = 'predicts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    img_path = db.Column(db.Text, nullable=False)
    disease_type = db.Column(db.String(30), nullable=False)
    confidence_accuracy = db.Column(db.Float, nullable=False)
