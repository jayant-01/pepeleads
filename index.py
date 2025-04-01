from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import hashlib
from sqlalchemy import text

# Create a Blueprint for Page 1
index_bp = Blueprint('index_bp', __name__)

# Initialize a separate SQLAlchemy instance for Page 1
db = SQLAlchemy()

# Predefined referral links and their hashes
REFERRAL_LINKS = {
    'special-offer-1': 'LINK001',
    'vip-access': 'LINK002',
    'exclusive-deal': 'LINK003',
    'premium-survey': 'LINK004',
    'member-special': 'LINK005',
    'limited-time': 'LINK006',
    'early-access': 'LINK007',
    'priority-user': 'LINK008',
    'special-member': 'LINK009',
    'vip-member': 'LINK010'
}

def hash_referral_id(referral_id):
    if not referral_id:
        return None
    # Create a hash of the referral ID
    return hashlib.sha256(referral_id.encode()).hexdigest()[:10]

def add_day_experience_column():
    try:
        # Check if column exists
        with db.engine.connect() as conn:
            conn.execute(text("""
                ALTER TABLE survey_response_index 
                ADD COLUMN day_experience VARCHAR(50)
            """))
            conn.commit()
    except Exception as e:
        # Column might already exist
        print(f"Note: {e}")

class SurveyResponseIndex(db.Model):
    __tablename__ = 'survey_response_index'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    age = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    day_experience = db.Column(db.String(50), nullable=True)  # New field
    alarm_usage = db.Column(db.String(50), nullable=False)
    alarm_choice = db.Column(db.String(50), nullable=True)
    other_alarm = db.Column(db.String(255), nullable=True)
    referral_hash = db.Column(db.String(10), nullable=True)  # Store hashed referral ID

@index_bp.route('/<referral_link>', methods=['GET'])
def referral_redirect(referral_link):
    if referral_link in REFERRAL_LINKS:
        # Store the referral code in session
        session['referral_code'] = REFERRAL_LINKS[referral_link]
        return redirect(url_for('index_bp.index'))
    return "Invalid referral link", 404

@index_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        age = request.form.get('age')
        gender = request.form.get('gender')
        day_experience = request.form.get('dayExperience')  # New field
        alarm_usage = request.form.get('alarmUsage')
        alarm_choice = request.form.get('alarmChoice')
        other_alarm = request.form.get('otherAlarm')
        
        # Get referral code from session if it exists
        referral_code = session.pop('referral_code', None)
        referral_hash = hash_referral_id(referral_code) if referral_code else None

        if not all([name, email, age, gender, alarm_usage]):
            return "Error: Required fields are missing!", 400

        new_response = SurveyResponseIndex(
            name=name,
            email=email,
            age=age,
            gender=gender,
            day_experience=day_experience,  # New field
            alarm_usage=alarm_usage,
            alarm_choice=alarm_choice,
            other_alarm=other_alarm,
            referral_hash=referral_hash
        )

        db.session.add(new_response)
        db.session.commit()
        return redirect(url_for('index_bp.responses'))
    
    return render_template('index.html')

@index_bp.route('/responses')
def responses():
    responses = SurveyResponseIndex.query.all()
    return render_template('response1.html', responses=responses)
