# page2.py
from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

page2_bp = Blueprint('page2_bp', __name__, url_prefix='/page2')

# Set up the engine, session, and base for Page 2
engine_page2 = create_engine('sqlite:///survey_responses_page1.db', connect_args={'check_same_thread': False})
SessionPage2 = sessionmaker(bind=engine_page2)
BasePage2 = declarative_base()

class SurveyResponsePage2(BasePage2):
    __tablename__ = 'survey_response_page2'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    age = Column(String(20), nullable=False)
    gender = Column(String(20), nullable=False)
    alarm_usage = Column(String(50), nullable=False)

BasePage2.metadata.create_all(engine_page2)

@page2_bp.route('/', methods=['GET', 'POST'])
def page2():
    if request.method == 'POST':
        name = request.form.get('name1')
        email = request.form.get('email1')
        password = request.form.get('password1')
        age = request.form.get('age1')
        gender = request.form.get('gender1')
        alarm_usage = request.form.get('alarmUsage1')
        
        if not all([name, email, password, age, gender, alarm_usage]):
            return "Error: Missing required fields for Page 2!", 400
        
        session = SessionPage2()
        new_response = SurveyResponsePage2(
            name=name,
            email=email,
            password=password,
            age=age,
            gender=gender,
            alarm_usage=alarm_usage
        )
        session.add(new_response)
        session.commit()
        session.close()
        print("Page 2 response saved!")
        return redirect(url_for('page2_bp.responses'))
    return render_template('page2.html')

@page2_bp.route('/responses')
def responses():
    session = SessionPage2()
    responses = session.query(SurveyResponsePage2).all()
    session.close()
    return render_template('responses_page1.html', responses=responses)
