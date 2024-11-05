# Import necessary libraries
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# Initialize Flask app
app = Flask(__name__)

# Set up database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Finroy1121!@127.0.0.1/fitness_center_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy and Marshmallow
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)

    def __init__(self, name, email, age):
        self.name = name
        self.email = email
        self.age = age


class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  
    type = db.Column(db.String(50), nullable=False)

    member = db.relationship('Member', backref=db.backref('workout_sessions', lazy=True))

    def __init__(self, member_id, date, duration, type):
        self.member_id = member_id
        self.date = date
        self.duration = duration
        self.type = type


# Create all tables
with app.app_context():
    db.create_all()

# Schema for Member model
class MemberSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Member


member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

# Route to add a new member
@app.route('/member', methods=['POST'])
def add_member():
    name = request.json['name']
    email = request.json['email']
    age = request.json['age']

    new_member = Member(name, email, age)
    db.session.add(new_member)
    db.session.commit()

    return member_schema.jsonify(new_member)

# Route to get all members
@app.route('/members', methods=['GET'])
def get_members():
    all_members = Member.query.all()
    result = members_schema.dump(all_members)
    return jsonify(result)

# Route to get a single member by ID
@app.route('/member/<id>', methods=['GET'])
def get_member(id):
    member = Member.query.get(id)
    if member is None:
        return jsonify({'error': 'Member not found'}), 404
    return member_schema.jsonify(member)

# Route to update a member
@app.route('/member/<id>', methods=['PUT'])
def update_member(id):
    member = Member.query.get(id)
    if member is None:
        return jsonify({'error': 'Member not found'}), 404

    member.name = request.json['name']
    member.email = request.json['email']
    member.age = request.json['age']

    db.session.commit()
    return member_schema.jsonify(member)

# Route to delete a member
@app.route('/member/<id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get(id)
    if member is None:
        return jsonify({'error': 'Member not found'}), 404

    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Member deleted successfully'})

# Schema for WorkoutSession model
class WorkoutSessionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WorkoutSession
        include_fk = True


workout_session_schema = WorkoutSessionSchema()
workout_sessions_schema = WorkoutSessionSchema(many=True)

# Route to schedule a new workout session
@app.route('/workout', methods=['POST'])
def schedule_workout():
    member_id = request.json['member_id']
    date = request.json['date']
    duration = request.json['duration']
    type = request.json['type']

    new_workout = WorkoutSession(member_id, date, duration, type)
    db.session.add(new_workout)
    db.session.commit()

    return workout_session_schema.jsonify(new_workout)

# Route to update a workout session
@app.route('/workout/<id>', methods=['PUT'])
def update_workout(id):
    workout = WorkoutSession.query.get(id)
    if workout is None:
        return jsonify({'error': 'Workout session not found'}), 404

    workout.date = request.json['date']
    workout.duration = request.json['duration']
    workout.type = request.json['type']

    db.session.commit()
    return workout_session_schema.jsonify(workout)

# Route to view all workout sessions
@app.route('/workouts', methods=['GET'])
def get_workouts():
    all_workouts = WorkoutSession.query.all()
    result = workout_sessions_schema.dump(all_workouts)
    return jsonify(result)

# Route to retrieve all workout sessions for a specific member
@app.route('/member/<member_id>/workouts', methods=['GET'])
def get_member_workouts(member_id):
    workouts = WorkoutSession.query.filter_by(member_id=member_id).all()
    if not workouts:
        return jsonify({'error': 'No workouts found for this member'}), 404
    result = workout_sessions_schema.dump(workouts)
    return jsonify(result)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)