import flask
from flask import Flask, render_template, request, redirect, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import not_
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///FitnessGuruDB.db'
app.config['SECRET_KEY'] = 'secretKey'
db = SQLAlchemy(app)

class Benefit(db.Model):
    Benefit_ID = db.Column(db.Integer, primary_key=True)
    Area = db.Column(db.String(50))
    Type = db.Column(db.String(50))
    memberTier = db.relationship('Benefit_Tier', backref='Benefit')

class Membership_Tier(db.Model):
    Tier_ID = db.Column(db.String(50), primary_key=True)
    Price = db.Column(db.Integer)
    Duration = db.Column(db.Integer)
    benefit = db.relationship('Benefit_Tier', backref='Membership_Tier')

class Benefit_Tier(db.Model):
    Tier_ID = db.Column(db.Integer, db.ForeignKey('Membership_Tier.Tier_ID'), primary_key=True)
    Benefit_ID = db.Column(db.Integer, db.ForeignKey('Benefit.Benefit_ID'), primary_key=True)

class Member(db.Model):
    Member_ID = db.Column(db.Integer, primary_key=True)
    Fname = db.Column(db.String(50))
    Lname = db.Column(db.String(50))
    Email = db.Column(db.String(50))
    DOB = db.Column(db.String(50))
    Tier_ID = db.Column(db.String(50), db.ForeignKey('Membership_Tier.Tier_ID'))
    Trainer_ID = db.Column(db.Integer, db.ForeignKey('Trainer.Trainer_ID'))

class Trainer(db.Model):
    Trainer_ID = db.Column(db.Integer, primary_key=True)
    Fname = db.Column(db.String(50))
    Lname = db.Column(db.String(50))
    Member_ID = db.relationship('Member', backref='Trainer')

class ClassXMember(db.Model):
    Member_ID = db.Column(db.Integer, db.ForeignKey('Member.Member_ID'), primary_key=True)
    Class_ID = db.Column(db.Integer, db.ForeignKey('Class.Class_ID'), primary_key=True)
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))

class Class(db.Model):
    Class_ID = db.Column(db.Integer, primary_key=True)
    classXmember_ID = db.relationship('ClassXMember', backref='Class')
    Instructor = db.Column(db.String(50))
    days_of_week = db.Column(db.String(50))
    Time = db.Column(db.String(50))
    Type = db.Column(db.String(50))
    Max_capacity = db.Column(db.Integer)
    Enrollment = db.Column(db.Integer)

class ExerciseXMember(db.Model):
    Member_ID = db.Column(db.Integer, db.ForeignKey('Member.Member_ID'), primary_key=True)
    Exercise_ID = db.Column(db.Integer, db.ForeignKey('Exercise.Exercise_ID'), primary_key=True)
    days_of_week = db.Column(db.String(50))
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))

class Exercise(db.Model):
    Exercise_ID = db.Column(db.Integer, primary_key=True)
    exerciseXmember_ID = db.relationship('ExerciseXMember', backref='Exercise')
    Type = db.Column(db.String(50))
    Reps = db.Column(db.Integer)
    Weight = db.Column(db.Double)
    Sets = db.Column(db.Integer)