from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

#--------------------------------------------------------------------------------
#===================================DATABASES====================================
#--------------------------------------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    fullname = db.Column(db.String(200), nullable=False)
    achievement = db.Column(db.String(256), nullable=False)
    user_status=db.Column(db.String(50),nullable=False,default='Enabled')
    dob = db.Column(db.DateTime, nullable=False)
    role=db.Column(db.String,default='user',nullable=False)
    quiz_scores = db.relationship('Scores' , back_populates='user_details')
#----------------------------------------------------------------------------------
class Subject(db.Model):
    id = db.Column(db.String(50),primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    desc = db.Column(db.Text,unique=False ,nullable=False)
    chapters = db.relationship('Chapters', back_populates='subject_info')
#----------------------------------------------------------------------------------
class Chapters(db.Model):
    id = db.Column(db.String(50),primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    desc = db.Column(db.String(256),unique=False ,nullable=False)
    subject_id = db.Column(db.String, db.ForeignKey('subject.id'), nullable=False)
    subject_info = db.relationship('Subject' ,back_populates='chapters')
    exams = db.relationship('Quiz', back_populates='chapter')
#----------------------------------------------------------------------------------
class Question(db.Model):
    id = db.Column(db.String ,primary_key=True)
    quiz_id = db.Column(db.String(50), db.ForeignKey("quiz.id"), nullable=False)
    question_title = db.Column(db.String, nullable=False)
    option_a = db.Column(db.String(255), nullable=False) 
    option_b = db.Column(db.String(255), nullable=False) 
    option_c = db.Column(db.String(255), nullable=True)  
    option_d= db.Column(db.String(255), nullable=True)
    correct_response = db.Column(db.String(150), nullable=False)
    exam = db.relationship('Quiz', back_populates='questions')     
#------------------------------------------------------------------------------------
class Quiz(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    chapter_id = db.Column(db.String(50), db.ForeignKey("chapters.id"), nullable=False)
    quiz_date = db.Column(db.DateTime, nullable=False)  
    duration = db.Column(db.String(10), nullable=False)  
    remarks = db.Column(db.String(200), nullable=True)
    scores = db.relationship('Scores', back_populates='exam')
    questions = db.relationship('Question', back_populates='exam')
    chapter = db.relationship('Chapters', back_populates='exams')

#---------------------------------------------------------------------------------------   
class Scores(db.Model):
    id = db.Column(db.Integer, primary_key=True , autoincrement=True)  
    quiz_id = db.Column(db.String, db.ForeignKey('quiz.id'), nullable=False) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  
    attempt_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  
    total = db.Column(db.Float, nullable=False)      
    user_details = db.relationship('User', back_populates='quiz_scores')
    exam = db.relationship('Quiz', back_populates='scores')
