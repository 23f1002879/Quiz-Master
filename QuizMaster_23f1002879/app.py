from flask import Flask , render_template,request , redirect,url_for
from model import db , User , Subject , Chapters , Question ,Quiz ,Scores
from datetime import datetime
#-------------------------------------------------------------------------------
#===========================Initializing Flask & Database=======================
#-------------------------------------------------------------------------------

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

#----------------------------------------------------------------------------------------
#==========================App routes====================================================
#----------------------------------------------------------------------------------------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login' , methods = ['GET','POST'])
def login():
    user = None 
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()

        if user and user.password == password:
            user_name = user.fullname
            return render_template('user_dashboard.html', user_name=user_name)
        else:
            return render_template('home.html', message="Invalid Username or Password.")
    return render_template('home.html')

#--------------------------------------------------------------------------------------------------------------------------------------------------------
#============================================================ADMIN ROUTES================================================================================
#--------------------------------------------------------------------------------------------------------------------------------------------------------
def initialize_admin():
    admin_username = 'admin@iitmbs'
    admin_password = '222'
    admin_fullname = 'Admin User'
    existing_admin = User.query.filter_by(username=admin_username, role='admin').first()
    
    if not existing_admin:
        new_admin = User(
            username=admin_username,
            password=admin_password,
            fullname=admin_fullname,
            role='admin',
            achievement='Administrator',
            dob=datetime(1970, 1, 1) 
        )
        db.session.add(new_admin)
        db.session.commit()

@app.route('/admin' , methods=['GET' ,'POST'])
def admin():
    if request.method == 'POST':
        admin_username = request.form.get('username')
        admin_password = request.form.get('password')
        admin = User.query.filter_by(username=admin_username, password=admin_password, role='admin').first()

        if admin:
            return redirect('/admin/dashboard')
        else:
            return render_template('admin_login.html', message="Invalid Username or Password!")
    return render_template('admin_login.html')

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    admin_user = User.query.filter_by(username='admin@iitmbs', role='admin').first()
    if not admin_user:
        return render_template('home.html', message="Access Denied.")
    
    subjects = Subject.query.all()
    return render_template('admin_dashboard.html', subjects=subjects)

@app.route('/admin/subject', methods=['GET' ,'POST'])
def add_subject_and_chapter():
    subject = Subject.query.all()
    chapter = Chapters.query.all()
    number_of_quiz={chap.id: Quiz.query.filter_by(chapter_id=chap.id).count() for chap in chapter}
    if request.method == 'POST':
        if 'id' in request.form and 'name' in request.form and 'desc' in request.form :
            if 'subject_id' not in request.form:
                id = request.form.get('id')
                name = request.form.get('name')
                desc = request.form.get('desc')
                exist_subject = Subject.query.filter_by(id=id).first()
                if exist_subject:
                    return render_template('subject.html' , message='Subject already in database' ,user_name=' Admin007' )
                new_subject = Subject(id=id , name=name , desc=desc)
                db.session.add(new_subject)
                db.session.commit()
                return redirect('/admin/subject')
            else:
                id = request.form.get('id')
                name = request.form.get('name')
                desc = request.form.get('desc')
                subject_id = request.form.get('subject_id')
                exist_chapter = Chapters.query.filter_by(id=id).first()
                if exist_chapter:
                    return redirect('/admin/subject?message=Chapter already in database&category=error')
                new_chapter = Chapters(id=id , name=name , desc=desc , subject_id=subject_id)
                db.session.add(new_chapter)
                db.session.commit()
                return redirect('/admin/subject')
    else:
        return render_template('subject.html',subject=subject , chapter=chapter , number_of_quiz=number_of_quiz)

@app.route('/admin/edit_subject/<string:subject_id>', methods=['GET' , 'POST'])
def edit_subject(subject_id):
    subject=Subject.query.filter_by(id=subject_id).first()
    
    if request.method=='POST':
        subject.name = request.form.get('name')
        subject.desc = request.form.get('desc')
        db.session.commit()
        return redirect('/admin/subject')
    else:
        return render_template('edit_subject.html', subject=subject )

@app.route('/admin/delete_subject/<string:subject_id>')
def delete_subject(subject_id):
    subject_to_delete = Subject.query.get(subject_id)
    if not subject_to_delete:
        return redirect('/admin/subject?message=Subject not found&category=error')

    # Delete all related chapters and quizzes
    for chapter in subject_to_delete.chapters:
        for quiz in chapter.exams:
            db.session.delete(quiz)  # Delete quizzes related to the chapter
        db.session.delete(chapter)  # Delete the chapter itself
    db.session.delete(subject_to_delete)  # Delete the subject
    db.session.commit()
    
    return redirect('/admin/subject')

@app.route('/admin/edit_chapter/<string:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    chapter = Chapters.query.filter_by(id=chapter_id).first()
    if request.method == 'POST':
        chapter.name = request.form.get('name')
        chapter.desc = request.form.get('desc')
        db.session.commit()
        return redirect('/admin/subject')
    else:
        return render_template('edit_chapter.html' , chapter=chapter)

@app.route('/admin/delete_chapter/<string:chapter_id>')
def delete_chapter(chapter_id):
    chapter = Chapters.query.get(chapter_id)
    if not chapter:
        return redirect('/admin/subject?message=Chapter not found&category=error')

    # Delete all quizzes related to the chapter
    for quiz in chapter.exams:
        db.session.delete(quiz)  # Delete quizzes related to the chapter
    db.session.delete(chapter)  # Delete the chapter itself
    db.session.commit()
    
    return redirect(url_for('add_subject_and_chapter'))


@app.route('/admin/add_quiz/<string:chapter_id>', methods=['GET', 'POST'])
def add_quiz(chapter_id):
    chapter = Chapters.query.filter_by(id=chapter_id).first()
    if not chapter:
        return redirect(url_for('add_chapter_and_subject' , message='Chapter not in Database'))  
    if request.method == 'POST':
        quiz_id = request.form.get('id')
        quiz_date = request.form.get('quiz_date')
        duration = request.form.get('duration')
        remarks = request.form.get('remarks', '')
        existing_quiz = Quiz.query.filter_by(id=quiz_id).first()
        if existing_quiz:
            return f"Error: Quiz ID '{quiz_id}' already exists. Please use a unique ID."
        new_quiz = Quiz(
                id=quiz_id,
                chapter_id=chapter_id,
                quiz_date=datetime.strptime(quiz_date, '%Y-%m-%d'),
                duration=duration,
                remarks=remarks
            )
        db.session.add(new_quiz)
        db.session.commit()
        return redirect(url_for('add_subject_and_chapter'))
    return render_template('add_quiz.html', chapter=chapter)  

@app.route('/admin/quiz', methods=['GET', 'POST'])
def quiz_space():
    quiz_list = Quiz.query.all() 
    questions=Question.query.all()
    print("Fetched Questions:", questions)

    if request.method == 'POST':
        id = request.form.get('id')
        quiz_id = request.form.get('quiz_id')
        question_title = request.form.get('question_title')
        option_a = request.form.get('option_a')
        option_b = request.form.get('option_b')
        option_c = request.form.get('option_c')
        option_d = request.form.get('option_d')
        correct_response = request.form.get('correct_response')
        exist_question = Question.query.filter_by(id=id).first()
        if exist_question:
            return redirect(url_for('quiz_space', message='Question already exists'))

        new_question = Question(
            id=id,
            quiz_id=quiz_id,
            question_title=question_title,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_response=correct_response
        )
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for('quiz_space'))

    return render_template('admin_quiz.html', quiz=quiz_list , questions=questions)

@app.route('/admin/edit_quiz/<string:quiz_id>', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    quiz = Quiz.query.filter_by(id=quiz_id).first()
    if request.method == 'POST':
        quiz.name = quiz.form.get('name')
        quiz.desc = request.form.get('desc')
        db.session.commit()
        return redirect('/admin/quiz')
    else:
        return render_template('edit_quiz.html',quiz=quiz)


@app.route('/admin/delete_quiz/<string:quiz_id>')
def delete_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return redirect('/admin/quiz?message=Quiz not found&category=error')

    db.session.delete(quiz)
    db.session.commit()
    
    return redirect('/admin/quiz')





#----------------------------------------------------------------------------------------------------------
#=====================================USER ROUTES==========================================================
#----------------------------------------------------------------------------------------------------------

@app.route('/login/register' , methods = ['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        fullname = request.form.get('fullname')
        achievement = request.form.get('achievement')
        dob = request.form.get('dob')
        user = User.query.filter_by(username=username).first()
        if user :
            return render_template("new_user.html" , message = "Username already exists!")
        try:
            dob_python = datetime.strptime(dob, '%Y-%m-%d')
        except ValueError as e:
            return render_template("new_user.html", message="Invalid date format. Please use YYYY-MM-DD.")
        
        new_user = User(username=username , password=password , fullname=fullname
                         , achievement=achievement , dob=dob_python )
        db.session.add(new_user)
        db.session.commit()
        return render_template("new_user.html",message="User registered successfully")
    else:
        return render_template('new_user.html') 



@app.route('/login/dashboard')
def dashboard():
    return render_template('user_dashboard.html')


with app.app_context():
    db.create_all()
    initialize_admin()


if __name__ == '__main__':
    app.run(debug = True)



