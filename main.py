import flask
from flask import Flask, render_template, request, redirect, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import not_
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///FitnessGuruDB.db'
app.config['SECRET_KEY'] = 'secretKey'
login_manager = LoginManager(app)
db = SQLAlchemy(app)

class Benefit(db.Model):
    __tablename__ = "benefit"
    Benefit_ID = db.Column(db.Integer, primary_key=True)
    Area = db.Column(db.String(50))
    Type = db.Column(db.String(50))
    memberTier = db.relationship('Benefit_Tier', backref='Benefit', lazy='dynamic')

class Membership_Tier(db.Model):
    __tablename__ = "membershiptier"
    ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50))
    Price = db.Column(db.Integer)
    Duration = db.Column(db.Integer)
    benefit = db.relationship('Benefit_Tier', backref='membershiptier', lazy='dynamic')

class Benefit_Tier(db.Model):
    Tier_ID = db.Column(db.Integer, db.ForeignKey('membershiptier.ID'), primary_key=True)
    Benefit_ID = db.Column(db.Integer, db.ForeignKey('benefit.Benefit_ID'), primary_key=True)

class Member(UserMixin, db.Model):
    __tablename__ = "member"
    Member_ID = db.Column(db.Integer, primary_key=True)
    Fname = db.Column(db.String(50))
    Lname = db.Column(db.String(50))
    DOB = db.Column(db.String(50))
    Email = db.Column(db.String(50))
    Password = db.Column(db.String(50))
    Tier_ID = db.Column(db.String(50), db.ForeignKey('membershiptier.ID'))
    Trainer_ID = db.Column(db.Integer, db.ForeignKey('trainer.Trainer_ID'))

    def get_id(self):
        return str(self.Member_ID)


class Trainer(db.Model):
    __tablename__ = "trainer"
    Trainer_ID = db.Column(db.Integer, primary_key=True)
    Fname = db.Column(db.String(50))
    Lname = db.Column(db.String(50))
    members = db.relationship('Member', backref='trainer', lazy='dynamic')


class ClassXMember(db.Model):
    __tablename__ = 'classxmember'
    Member_ID = db.Column(db.Integer, db.ForeignKey('member.Member_ID'), primary_key=True)
    Class_ID = db.Column(db.Integer, db.ForeignKey('class.Class_ID'), primary_key=True)
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))

class Class(db.Model):
    __tablename__ = 'class'
    Class_ID = db.Column(db.Integer, primary_key=True)
    classXmembers = db.relationship('ClassXMember', backref='class', lazy='dynamic')
    Instructor = db.Column(db.String(50))
    days_of_week = db.Column(db.String(50))
    Time = db.Column(db.String(50))
    Type = db.Column(db.String(50))
    Max_capacity = db.Column(db.Integer)
    Enrollment = db.Column(db.Integer)


class ExerciseXMember(db.Model):
    __tablename__ = 'exercisexmember'
    Member_ID = db.Column(db.Integer, db.ForeignKey('member.Member_ID'), primary_key=True)
    Exercise_ID = db.Column(db.Integer, db.ForeignKey('exercise.Exercise_ID'), primary_key=True)
    days_of_week = db.Column(db.String(50))
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))

class Exercise(db.Model):
    __tablename__ = 'exercise'
    Exercise_ID = db.Column(db.Integer, primary_key=True)
    exerciseXmembers = db.relationship('ExerciseXMember', backref='exercise', lazy='dynamic')
    Type = db.Column(db.String(50))
    Reps = db.Column(db.Integer)
    Weight = db.Column(db.Double)
    Sets = db.Column(db.Integer)

@app.route('/')
def home():
    login = False
    return render_template('home.html', login=login)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        Email = request.form['username']
        Password = request.form['password']

        user = Member.query.filter_by(Email=Email).first()

        if Email != user.Email or Password != user.Password:
            uniqueName = False
            return render_template('login.html', uniqueName=uniqueName)

        login_user(user)
        login = True
        return render_template('home.html', login=login)

    elif request.method == 'GET':
        uniqueName = True
        return render_template('login.html')

app.app_context().push()

@login_manager.user_loader
def load_user(user_id):
    return Member.query.get(int(user_id))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    login=False
    return render_template('home.html', login=login)



if __name__ == '__main__':
    app.run()