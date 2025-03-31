from flask import Blueprint, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import uuid

# Create a Blueprint for Page 1
index_bp = Blueprint('index_bp', __name__)

# Initialize a separate SQLAlchemy instance for Page 1
db = SQLAlchemy()

def generate_referral_code():
    # Generate a unique 8-character code
    return str(uuid.uuid4())[:8].upper()

class SurveyResponseIndex(db.Model):
    __tablename__ = 'survey_response_index'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    age = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    alarm_usage = db.Column(db.String(50), nullable=False)
    alarm_choice = db.Column(db.String(50), nullable=True)
    other_alarm = db.Column(db.String(255), nullable=True)
    referral_id = db.Column(db.String(50), nullable=True)
    referral_code = db.Column(db.String(8), unique=True, nullable=False)

@index_bp.route('/', methods=['GET', 'POST'])
def index():
    # Check for referral code in URL
    referral_code = request.args.get('ref')
    if referral_code:
        # Store the referral code in the session or pass it to the template
        return render_template('index.html', referral_code=referral_code)

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        age = request.form.get('age')
        gender = request.form.get('gender')
        alarm_usage = request.form.get('alarmUsage')
        alarm_choice = request.form.get('alarmChoice')
        other_alarm = request.form.get('otherAlarm')
        referral_id = request.form.get('referralId')
        referral_code = generate_referral_code()

        # Check required fields
        if not all([name, email, age, gender, alarm_usage]):
            return "Error: Name, Email, Age, Gender, and Alarm Usage are required!", 400

        new_response = SurveyResponseIndex(
            name=name,
            email=email,
            age=age,
            gender=gender,
            alarm_usage=alarm_usage,
            alarm_choice=alarm_choice,
            other_alarm=other_alarm,
            referral_id=referral_id,
            referral_code=referral_code
        )

        db.session.add(new_response)
        db.session.commit()
        print("Page 1 response saved!")
        return redirect(url_for('index_bp.responses'))
    return render_template('index.html')

@index_bp.route('/responses')
def responses():
    responses = SurveyResponseIndex.query.all()
    return render_template('response1.html', responses=responses) 