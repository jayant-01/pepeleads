from flask import Blueprint, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from index import SurveyResponseIndex
from page2 import SurveyResponsePage2
from page3 import SurveyResponsePage3

referral_bp = Blueprint('referral_bp', __name__, url_prefix='/referral')

# Set up database connections
engine_page1 = create_engine('sqlite:///survey_response.db', connect_args={'check_same_thread': False})
engine_page2 = create_engine('sqlite:///survey_responses_page1.db', connect_args={'check_same_thread': False})
engine_page3 = create_engine('sqlite:///survey_responses_page2.db', connect_args={'check_same_thread': False})

SessionPage1 = sessionmaker(bind=engine_page1)
SessionPage2 = sessionmaker(bind=engine_page2)
SessionPage3 = sessionmaker(bind=engine_page3)

@referral_bp.route('/', methods=['GET'])
def index():
    return render_template('referral.html')

@referral_bp.route('/search', methods=['POST'])
def search():
    search_id = request.form.get('search_id')
    if not search_id:
        return render_template('referral.html', error="Please enter an ID to search")

    try:
        search_id = int(search_id)
    except ValueError:
        return render_template('referral.html', error="Please enter a valid numeric ID")

    # Search in all three databases
    session1 = SessionPage1()
    session2 = SessionPage2()
    session3 = SessionPage3()

    try:
        # Search in Page 1 database
        response1 = session1.query(SurveyResponseIndex).filter_by(id=search_id).first()
        if response1:
            result = {
                'ID': response1.id,
                'Name': response1.name,
                'Email': response1.email,
                'Age': response1.age,
                'Gender': response1.gender,
                'Alarm Usage': response1.alarm_usage,
                'Alarm Choice': response1.alarm_choice,
                'Other Alarm': response1.other_alarm,
                'Database': 'Page 1'
            }
            return render_template('referral.html', response=result)

        # Search in Page 2 database
        response2 = session2.query(SurveyResponsePage2).filter_by(id=search_id).first()
        if response2:
            result = {
                'ID': response2.id,
                'Name': response2.name,
                'Email': response2.email,
                'Password': response2.password,
                'Age': response2.age,
                'Gender': response2.gender,
                'Alarm Usage': response2.alarm_usage,
                'Database': 'Page 2'
            }
            return render_template('referral.html', response=result)

        # Search in Page 3 database
        response3 = session3.query(SurveyResponsePage3).filter_by(id=search_id).first()
        if response3:
            result = {
                'ID': response3.id,
                'Alarm Choice': response3.alarm_choice,
                'Features': response3.features,
                'Number of Alarms': response3.num_alarms,
                'Purchase Date': response3.purchase_date.strftime('%Y-%m-%d') if response3.purchase_date else None,
                'Alarm URL': response3.alarm_url,
                'Comments': response3.comments,
                'Database': 'Page 3'
            }
            return render_template('referral.html', response=result)

        return render_template('referral.html', error=f"No entry found with ID {search_id} in any database")

    finally:
        session1.close()
        session2.close()
        session3.close() 