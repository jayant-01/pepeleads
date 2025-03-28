# page3.py
from flask import Flask,Blueprint, render_template, request, redirect, url_for
from sqlalchemy import create_engine, Column, Integer, String, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

page3_bp = Blueprint('page3_bp', __name__, url_prefix='/page3')
app = Flask(__name__, template_folder='templates')


# Set up the engine, session, and base for Page 3
engine_page3 = create_engine('sqlite:///survey_responses_page2.db', connect_args={'check_same_thread': False})
SessionPage3 = sessionmaker(bind=engine_page3)
BasePage3 = declarative_base()

class SurveyResponsePage3(BasePage3):
    __tablename__ = 'survey_response_page3'
    id = Column(Integer, primary_key=True)
    alarm_choice = Column(String(50), nullable=False)
    features = Column(String(200), nullable=True)  # Comma-separated values from checkboxes
    num_alarms = Column(Integer, nullable=True)
    purchase_date = Column(Date, nullable=True)
    alarm_url = Column(String(200), nullable=True)
    comments = Column(Text, nullable=True)

BasePage3.metadata.create_all(engine_page3)

@page3_bp.route('/', methods=['GET', 'POST'])
def page3():
    if request.method == 'POST':
        alarm_choice = request.form.get('alarmChoice2')
        features_list = request.form.getlist('features2[]')  # Expecting an array
        features = ",".join(features_list) if features_list else None
        num_alarms = request.form.get('numAlarms2')
        purchase_date_str = request.form.get('purchaseDate2')
        alarm_url = request.form.get('alarmURL2')
        comments = request.form.get('comments2')
        
        num_alarms = int(num_alarms) if num_alarms and num_alarms.isdigit() else None
        purchase_date = None
        if purchase_date_str:
            try:
                purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        if not alarm_choice:
            return "Error: Missing required field for Page 3 (Alarm Clock Choice)!", 400
        
        session = SessionPage3()
        new_response = SurveyResponsePage3(
            alarm_choice=alarm_choice,
            features=features,
            num_alarms=num_alarms,
            purchase_date=purchase_date,
            alarm_url=alarm_url,
            comments=comments
        )
        session.add(new_response)
        session.commit()
        session.close()
        print("Page 3 response saved!")
        return redirect(url_for('page3_bp.responses'))
    return render_template('page3.html')

@page3_bp.route('/responses')
def responses():
    session = SessionPage3()
    responses = session.query(SurveyResponsePage3).all()
    session.close()
    return render_template('responses_page2.html', responses=responses)
