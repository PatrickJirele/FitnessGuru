import flask
from flask import Flask, render_template, request, redirect, jsonify, flash, url_for
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
    __tablename__ = "Benefit_Tier"
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



class Exercise(db.Model):
    __tablename__ = 'exercise'
    Exercise_ID = db.Column(db.Integer, primary_key=True)
    exerciseXmembers = db.relationship('ExerciseXMember', backref='exercise', lazy='dynamic')
    Type = db.Column(db.String(50))
    Reps = db.Column(db.Integer)
    Weight = db.Column(db.Double)
    Sets = db.Column(db.Integer)
    days_of_week = db.Column(db.String(50))



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
    login = False
    return render_template('home.html', login=login)


@app.route('/createuser', methods=['POST', 'GET'])
def createsuer():
    trainers = Trainer.query.all()
    if request.method == 'POST':
        Email = request.form['email']
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
        login = True
        return render_template('home.html', login=login, Fname=Fname)

    elif request.method == 'GET':
        uniqueName = True
        return render_template('createuser.html', uniqueName=uniqueName, trainers=trainers)


@app.route("/signUp", methods=["POST", "GET"])
@login_required
def signUp():
    if request.method == "GET":
        user = current_user
        user_signed_up_classes = ClassXMember.query.filter_by(Member_ID=user.Member_ID).with_entities(
            ClassXMember.Class_ID).subquery()

        classes_not_signed_up = Class.query.filter(Class.Class_ID.notin_(user_signed_up_classes)).all()
        print(classes_not_signed_up)

        return render_template("signUp.html", login=True, classes=classes_not_signed_up)
    elif request.method == "POST":
        user = current_user
        class_id = request.form["class_id"]  # Retrieve the class ID from the form submission
        class_to_add = Class.query.filter_by(Class_ID=class_id).first()
        newClass = ClassXMember(
            Member_ID=user.Member_ID,
            Class_ID=class_to_add.Class_ID,
        )
        db.session.add(newClass)
        db.session.commit()
        login = True
        return render_template('home.html', login=login, Fname=user.Fname)



@app.route("/classes", methods=['POST', 'GET'])
@login_required
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

    return render_template("classes.html", login=True, class_info=class_info, days=days)



@app.route("/viewIndvClass", methods=['POST', 'GET'])
@login_required
def viewIndvClass():
    class_info = []
    if request.method == 'GET':
        if 'class_types' in request.args:
            class_types = request.args.get('class_types')
            print('class types1:', class_types)
            class_types = class_types.split(",")
            print('class types2:', class_types)
            for class_name in class_types:
                print("class_name:", class_name)
                class_name = class_name.strip()
                classes = Class.query.filter_by(Type=class_name).all()  # Retrieve all classes with the given class name
                print("classes:", classes)
                class_info.extend(classes)
                print('class_info:', class_info)
            return render_template("viewIndvClass.html", login=True, class_info=class_info)
    elif request.method == "POST":
        class_id = request.form["class_id"]  # Retrieve the class ID from the form submission

        deleted_row = ClassXMember.query.filter_by(Member_ID=current_user.Member_ID, Class_ID=class_id).delete()
        if deleted_row:
            db.session.commit()
            flash('You have successfully unenrolled from the class.', 'success')
        else:
            flash('You were not enrolled in this class.', 'error')

        return redirect(url_for('classes'))


@app.route("/viewIndvExercise", methods=['POST', 'GET'])
@login_required
def viewIndvExercise():
    exercise_info = []
    if request.method == 'GET':
        if 'exercise_types' in request.args:
            exercise_types = request.args.get('exercise_types')
            print('exercise types1:', exercise_types)
            exercise_types = exercise_types.split(",")
            print('exercise types2:', exercise_types)
            for exercise_name in exercise_types:
                print("exercise_name:", exercise_name)
                exercise_name = exercise_name.strip()
                exercises = Exercise.query.filter_by(Type=exercise_name).all()
                print("exercises:", exercises)
                exercise_info.extend(exercises)
                print('exercise_info:', exercise_info)
            return render_template("viewIndvExercise.html", login=True, exercise_info=exercise_info)
    elif request.method == "POST":
        exercise_id = request.form["exercise_id"]

        deleted_row = ExerciseXMember.query.filter_by(Member_ID=current_user.Member_ID, Exercise_ID=exercise_id).delete()
        if deleted_row:
            db.session.commit()
        else:
            flash('You were not doing in this exercise.', 'error')

        return redirect(url_for('program'))


@app.route("/editProfile", methods=['POST', 'GET'])
@login_required
def editProfile():
    if request.method == "POST":
        # update the membership
        user = current_user
        new_tier_name = request.form.get("membership_tier")  # Retrieve the selected membership tier from the form

        new_tier = Membership_tier.query.filter_by(Name=new_tier_name).first()

        if new_tier:
            user.Tier_ID = new_tier.ID

            db.session.commit()

            flash("Membership tier updated successfully", "success")
        else:
            flash("Invalid membership tier selected", "error")
        return render_template('home.html', login=login, Fname=user.Fname)
    else:
        user = current_user
        tier = Membership_tier.query.filter_by(ID=user.Tier_ID).first()

        if tier:
            benefitsxtier = Benefit_Tier.query.filter_by(Tier_ID=tier.ID).all()
            benefit_ids = [benefit_tier.Benefit_ID for benefit_tier in benefitsxtier]
            benefits = Benefit.query.filter(Benefit.Benefit_ID.in_(benefit_ids)).all()
        else:
            benefits = []

        tier_name = tier.Name

        return render_template("editProfile.html", login=True, user=user, tier=tier_name, benefits=benefits)


@app.route("/program")
@login_required
def program():
    user = current_user
    user_exercise = db.session.query(Exercise, ExerciseXMember).join(ExerciseXMember).filter(
        ExerciseXMember.Member_ID == user.Member_ID).all()

    exercise_info = [(exercise.Type, exercise.days_of_week) for exercise, _ in user_exercise]
    print(exercise_info)
    days = {}
    for exercise_type, days_of_week in exercise_info:
        days_of_week = days_of_week.strip()  # Remove any leading or trailing spaces
        if days_of_week == "MWF":
            days[exercise_type] = []
            for i in range(2, 32, 7):
                days[exercise_type].extend([i, i + 2, i + 4])
        elif days_of_week == "TR":
            days[exercise_type] = []
            for i in range(3, 32, 7):
                days[exercise_type].extend([i, i + 2])

    return render_template('program.html', login=True, exercise_info=exercise_info, days=days)


@app.errorhandler(404)
def err404(err):
    return render_template("err.html", errNum = 404, typeErr = err, login = False)

@app.errorhandler(403)
def err404(err):
    return render_template("err.html", errNum = 403, typeErr = err, login = False)

@app.errorhandler(502)
def err404(err):
    return render_template("err.html", errNum = 502, typeErr = err, login = False)

@app.errorhandler(401)
def err404(err):
    return render_template("err.html", errNum = 401, typeErr = err, login = False)

if __name__ == '__main__':
    app.run()
