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

class Membership_tier(db.Model):
    __tablename__ = "Membership_tier"
    ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50))
    Price = db.Column(db.Integer)
    Length = db.Column(db.Integer)
    benefit = db.relationship('Benefit_Tier', backref='membershiptier', lazy='dynamic')

class Benefit_Tier(db.Model):
    Tier_ID = db.Column(db.Integer, db.ForeignKey('Membership_tier.ID'), primary_key=True)
    Benefit_ID = db.Column(db.Integer, db.ForeignKey('benefit.Benefit_ID'), primary_key=True)

class Member(UserMixin, db.Model):
    __tablename__ = "member"
    Member_ID = db.Column(db.Integer, primary_key=True)
    Fname = db.Column(db.String(50))
    Lname = db.Column(db.String(50))
    DOB = db.Column(db.String(50))
    Email = db.Column(db.String(50))
    Password = db.Column(db.String(50))
    Tier_ID = db.Column(db.String(50), db.ForeignKey('Membership_tier.ID'))
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

        if user == None or Email != user.Email or Password != user.Password:
            uniqueName = False
            return render_template('login.html', uniqueName=uniqueName)

        login_user(user)
        Fname = user.Fname
        login = True
        return render_template('home.html', login=login, Fname=Fname)

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

@app.route('/createuser', methods=['POST', 'GET'])
def createsuer():
    trainers = Trainer.query.all()
    if request.method == 'POST':
        Email= request.form['email']
        Fname = request.form['Fname']
        Lname = request.form['Lname']
        Password = request.form['password']
        DOB = request.form['DOB']
        Membershiptier = request.form['membership_tier']
        trainer = request.form['trainers']

        if Email == '' or Fname == '' or Lname == '' or Password == '' or DOB == '' or Membershiptier == '' or trainer == '':
            test = False
            uniqueName = True
            return render_template('createuser.html', uniqueName=uniqueName, trainers=trainers, test=test)

        tier = db.session.query(Membership_tier.ID).filter_by(Name=Membershiptier).scalar()
        trainer = db.session.query(Trainer.Trainer_ID).filter_by(Trainer_ID=trainer).scalar()

        tempUser = Member(
            Fname=Fname,
            Lname=Lname,
            DOB=DOB,
            Email=Email,
            Password=Password,
            Tier_ID=tier,
            Trainer_ID=trainer
        )
        user = Member.query.filter_by(Email=request.form['email']).first()

        if user != None:
            uniqueName = False
            return render_template('createuser.html', uniqueName=uniqueName, trainers=trainers)

        db.session.add(tempUser)
        db.session.commit()
        user = Member.query.filter_by(Email=Email).first()
        login_user(user)
        login=True
        return render_template('home.html', login=login, Fname=Fname)

    elif request.method == 'GET':
        uniqueName = True
        return render_template('createuser.html',uniqueName=uniqueName ,trainers=trainers)

@login_required
@app.route("/classes", methods=['POST', 'GET'])
def classes():
    user = current_user
    user_classes = db.session.query(Class, ClassXMember).join(ClassXMember).filter(
        ClassXMember.Member_ID == user.Member_ID).all()

    class_info = [(class_.Type, class_.days_of_week) for class_, _ in user_classes]

    days = {}
    for class_type, days_of_week in class_info:
        days_of_week = days_of_week.strip()  # Remove any leading or trailing spaces
        if days_of_week == "MWF":
            days[class_type] = []
            for i in range(2, 32, 7):
                days[class_type].extend([i, i + 2, i + 4])
        elif days_of_week == "TR":
            days[class_type] = []
            for i in range(3, 32, 7):
                days[class_type].extend([i, i + 2])

    print(days)
    return render_template("classes.html", login=True, class_info=class_info, days=days)
@login_required
@app.route("/viewIndvClass", methods=['POST', 'GET'])
def viewIndvClass():
    return render_template("viewIndvClass.html")

if __name__ == '__main__':
    app.run()