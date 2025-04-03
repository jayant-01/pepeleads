from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import hashlib
from sqlalchemy import text
import requests
import json

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

def add_device_type_column():
    try:
        # Check if column exists
        with db.engine.connect() as conn:
            conn.execute(text("""
                ALTER TABLE survey_response_index 
                ADD COLUMN device_type VARCHAR(20)
            """))
            conn.commit()
    except Exception as e:
        # Column might already exist
        print(f"Note: {e}")

def add_location_tracking_columns():
    try:
        # Check if columns exist
        with db.engine.connect() as conn:
            conn.execute(text("""
                ALTER TABLE survey_response_index 
                ADD COLUMN ip_address VARCHAR(45),
                ADD COLUMN country VARCHAR(100),
                ADD COLUMN city VARCHAR(100),
                ADD COLUMN region VARCHAR(100),
                ADD COLUMN latitude FLOAT,
                ADD COLUMN longitude FLOAT
            """))
            conn.commit()
    except Exception as e:
        # Columns might already exist
        print(f"Note: {e}")

def get_ip_info():
    try:
        # Get IP address
        ip_response = requests.get('https://api.ipify.org?format=json')
        ip_address = ip_response.json()['ip']
        
        # Get location information using IP
        location_response = requests.get(f'http://ip-api.com/json/{ip_address}')
        location_data = location_response.json()
        
        if location_data['status'] == 'success':
            return {
                'ip_address': ip_address,
                'country': location_data.get('country'),
                'city': location_data.get('city'),
                'region': location_data.get('regionName'),
                'latitude': location_data.get('lat'),
                'longitude': location_data.get('lon')
            }
    except Exception as e:
        print(f"Error getting IP info: {e}")
    
    # Return None if we couldn't get the information
    return None

def migrate_table_with_new_columns():
    try:
        with db.engine.connect() as conn:
            # Create a temporary table with all columns
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS survey_response_index_new (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    age VARCHAR(20) NOT NULL,
                    gender VARCHAR(20) NOT NULL,
                    day_experience VARCHAR(50),
                    alarm_usage VARCHAR(50) NOT NULL,
                    alarm_choice VARCHAR(50),
                    other_alarm VARCHAR(255),
                    referral_hash VARCHAR(10),
                    device_type VARCHAR(20),
                    ip_address VARCHAR(45),
                    country VARCHAR(100),
                    city VARCHAR(100),
                    region VARCHAR(100),
                    latitude FLOAT,
                    longitude FLOAT
                )
            """))
            
            # Copy data from old table to new table
            conn.execute(text("""
                INSERT INTO survey_response_index_new 
                SELECT id, name, email, age, gender, day_experience, 
                       alarm_usage, alarm_choice, other_alarm, referral_hash, 
                       device_type, NULL, NULL, NULL, NULL, NULL, NULL
                FROM survey_response_index
            """))
            
            # Drop the old table
            conn.execute(text("DROP TABLE survey_response_index"))
            
            # Rename the new table to the original name
            conn.execute(text("ALTER TABLE survey_response_index_new RENAME TO survey_response_index"))
            
            conn.commit()
            print("Table migrated successfully with new columns")
    except Exception as e:
        print(f"Error migrating table: {e}")
        # Try to rollback changes
        try:
            with db.engine.connect() as conn:
                conn.execute(text("DROP TABLE IF EXISTS survey_response_index_new"))
                conn.commit()
        except:
            pass

# Update the app initialization to use the new function
def init_db(app):
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        # Migrate the table with new columns
        migrate_table_with_new_columns()

class SurveyResponseIndex(db.Model):
    __tablename__ = 'survey_response_index'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    age = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    day_experience = db.Column(db.String(50), nullable=True)
    alarm_usage = db.Column(db.String(50), nullable=False)
    alarm_choice = db.Column(db.String(50), nullable=True)
    other_alarm = db.Column(db.String(255), nullable=True)
    referral_hash = db.Column(db.String(10), nullable=True)
    device_type = db.Column(db.String(20), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 addresses can be up to 45 characters
    country = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    region = db.Column(db.String(100), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

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
        day_experience = request.form.get('dayExperience')
        alarm_usage = request.form.get('alarmUsage')
        alarm_choice = request.form.get('alarmChoice')
        other_alarm = request.form.get('otherAlarm')
        device_type = request.form.get('deviceType')
        
        # Get IP and location information
        ip_info = get_ip_info()
        
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
            day_experience=day_experience,
            alarm_usage=alarm_usage,
            alarm_choice=alarm_choice,
            other_alarm=other_alarm,
            referral_hash=referral_hash,
            device_type=device_type,
            ip_address=ip_info['ip_address'] if ip_info else None,
            country=ip_info['country'] if ip_info else None,
            city=ip_info['city'] if ip_info else None,
            region=ip_info['region'] if ip_info else None,
            latitude=ip_info['latitude'] if ip_info else None,
            longitude=ip_info['longitude'] if ip_info else None
        )

        db.session.add(new_response)
        db.session.commit()
        return redirect(url_for('index_bp.responses'))
    
    return render_template('index.html')

@index_bp.route('/responses')
def responses():
    responses = SurveyResponseIndex.query.all()
    return render_template('response1.html', responses=responses)
