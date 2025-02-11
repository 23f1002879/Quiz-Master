from flask import Flask , render_template,request , redirect,url_for
from model import db , User , Subject , Chapters , Question , Quiz , Scores , UserResponse
from sqlalchemy.sql import func
import os
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt

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
            return redirect(url_for('dashboard' , user_id=user.id))
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
    subject = Subject.query.all()
    quiz = Quiz.query.all()
    user=User.query.all()
    chart_dir = "static/image"
    if not os.path.exists(chart_dir):
        os.makedirs(chart_dir)
    # Subject-wise Top Scorer Data
    top_scorers = db.session.query(
        Subject.name, 
        func.max(Scores.total).label("max_score")
    ).join(Chapters, Chapters.subject_id == Subject.id) \
     .join(Quiz, Quiz.chapter_id == Chapters.id) \
     .join(Scores, Scores.quiz_id == Quiz.id) \
     .group_by(Subject.name).all()
    
    subjects = [row[0] for row in top_scorers]
    top_scores = [row[1] for row in top_scorers]

    # Plot Subject-wise Top Scorer Chart
    plt.figure(figsize=(10, 5))
    plt.bar(subjects, top_scores, color='skyblue')
    plt.xlabel('Subjects')
    plt.ylabel('Top Score')
    plt.title('Top Scorers by Subject')
    plt.xticks(rotation=45)
    plt.tight_layout()
    top_scorer_chart = os.path.join(chart_dir, "top_scorers.png")
    plt.savefig(top_scorer_chart)
    plt.close()

    # Number of Users Attempted Quiz Data
    user_attempts = db.session.query(
        Subject.name,
        func.count(Scores.user_id.distinct()).label("user_count")
    ).join(Chapters, Chapters.subject_id == Subject.id) \
     .join(Quiz, Quiz.chapter_id == Chapters.id) \
     .join(Scores, Scores.quiz_id == Quiz.id) \
     .group_by(Subject.name).all()

    subjects_attempted = [row[0] for row in user_attempts]
    user_counts = [row[1] for row in user_attempts]

    # Plot Number of Users Attempted Quiz Chart
    plt.figure(figsize=(10, 5))
    plt.bar(subjects_attempted, user_counts, color='lightcoral')
    plt.xlabel('Subjects')
    plt.ylabel('Number of Users Attempted')
    plt.title('Number of Users Attempted Quiz per Subject')
    plt.xticks(rotation=45)
    plt.tight_layout()
    user_attempts_chart = os.path.join(chart_dir, "user_attempts.png")
    plt.savefig(user_attempts_chart)
    plt.close()

    
    return render_template('admin_dashboard.html', subject=subject , user=user , quiz=quiz , top_scorer_chart=top_scorer_chart, 
                           user_attempts_chart=user_attempts_chart) 

@app.route('/admin/disable_user/<int:user_id>', methods=['POST'])
def disable_user(user_id):
    user = User.query.get(user_id)  
    if user:
        user.user_status = 'Disabled' 
        db.session.commit()  
        return redirect('/admin/dashboard')  
    return "User not found", 404

@app.route('/admin/enable_user/<int:user_id>', methods=['POST'])
def enable_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.user_status = 'Enabled'
        db.session.commit()
        return redirect('/admin/dashboard')
    return "User not found", 404


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
                    return redirect('/admin/subject?message=Subject already in database&category=error')
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

@app.route('/admin/delete_subject/<string:subject_id>', methods=['GET'])
def delete_subject(subject_id):
    subject_to_delete = Subject.query.get(subject_id)
    if not subject_to_delete:
        return redirect('/admin/subject?message=Subject not found&category=error')
    for chapter in subject_to_delete.chapters:
        for quiz in chapter.exams:
            for score in quiz.scores:
                db.session.delete(score)
            for question in quiz.questions:
                db.session.delete(question)
            db.session.delete(quiz)
        db.session.delete(chapter)
    db.session.delete(subject_to_delete)
    db.session.commit()
    return redirect(url_for('add_subject_and_chapter'))

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
    for quiz in chapter.exams:
        for score in quiz.scores:
            db.session.delete(score)
        for question in quiz.questions:
            db.session.delete(question)
        db.session.delete(quiz)
    db.session.delete(chapter)
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
    quiz = Quiz.query.filter_by(id=quiz_id).first_or_404()
    if request.method == 'POST':
        quiz.quiz_date = datetime.strptime(request.form.get('quiz_date'), '%Y-%m-%d')
        quiz.duration = request.form.get('duration')
        quiz.remarks = request.form.get('remarks', '')
        db.session.commit()
        return redirect(url_for('quiz_space', message='Quiz updated successfully'))
    return render_template('edit_quiz.html', quiz=quiz)


@app.route('/admin/delete_quiz/<string:quiz_id>', methods=['GET'])
def delete_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return redirect('/admin/quiz?message=Quiz not found&category=error')
    for score in quiz.scores:
        db.session.delete(score)
    for question in quiz.questions:
        db.session.delete(question)
    db.session.delete(quiz)
    db.session.commit()
    return redirect('/admin/quiz')

@app.route('/admin/quiz/edit/<string:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        question.quiz_id = request.form.get('quiz_id')
        question.question_title = request.form.get('question_title')
        question.option_a = request.form.get('option_a')
        question.option_b = request.form.get('option_b')
        question.option_c = request.form.get('option_c')
        question.option_d = request.form.get('option_d')
        question.correct_response = request.form.get('correct_response')

        db.session.commit()
        return redirect(url_for('quiz_space', message='Question updated successfully'))

    return render_template('edit_question.html', question=question)


@app.route('/admin/quiz/delete/<string:question_id>', methods=['GET'])
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('quiz_space', message='Question deleted successfully'))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    users = User.query.filter(
        (User.username.ilike(f"%{query}%")) |
        (User.fullname.ilike(f"%{query}%")) |
        (User.achievement.ilike(f"%{query}%"))
    ).all()
    subjects = Subject.query.filter(
        (Subject.name.ilike(f"%{query}%")) |
        (Subject.desc.ilike(f"%{query}%"))
    ).all()
    quizzes = Quiz.query.filter(
        (Quiz.remarks.ilike(f"%{query}%"))
    ).all()

    return render_template("search_results.html", users=users, subjects=subjects, quizzes=quizzes, query=query)




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

chart_dirc = "static/image"
if not os.path.exists(chart_dirc):
    os.makedirs(chart_dirc)

@app.route('/dashboard/<int:user_id>', methods=['GET'])
def dashboard(user_id):
    user = User.query.get(user_id)
    current_date = datetime.now().strftime('%d-%m-%Y')
    if not user:
        return "User not found", 404
    
    if user.user_status == 'Disabled':
        return redirect(url_for('home', message="Your account has been disabled. Please contact the administrator."))
    
    quizzes = db.session.query(
        Quiz.id,
        Quiz.duration,
        Quiz.quiz_date,
        Subject.name.label('subject_name'),
        Chapters.name.label('chapter_name')
    ).join(Chapters, Quiz.chapter_id == Chapters.id) \
     .join(Subject, Chapters.subject_id == Subject.id).all()

    quiz_data = [
        {
            'id': quiz.id,
            'duration': quiz.duration,
            'quiz_date': quiz.quiz_date,
            'subject_name': quiz.subject_name,
            'chapter_name': quiz.chapter_name
        }
        for quiz in quizzes
    ]

    user_scores = Scores.query.filter_by(user_id=user_id).order_by(Scores.attempt_time.desc()).all()
    user_attempts = db.session.query(
        Subject.name,
        func.count(Scores.id).label("attempt_count")
    ).join(Chapters, Chapters.subject_id == Subject.id) \
     .join(Quiz, Quiz.chapter_id == Chapters.id) \
     .join(Scores, Scores.quiz_id == Quiz.id) \
     .filter(Scores.user_id == user_id) \
     .group_by(Subject.name).all()

    subjects_attempted = [row[0] for row in user_attempts]
    attempts_count = [row[1] for row in user_attempts]

    if not subjects_attempted:  
        subjects_attempted = ["No Data"]
        attempts_count = [0]

    plt.figure(figsize=(10, 5))
    plt.bar(subjects_attempted, attempts_count, color='mediumseagreen')
    plt.xlabel('Subjects')
    plt.ylabel('Number of Attempts')
    plt.title('Your Subject-Wise Quiz Attempts')
    plt.xticks(rotation=45)
    plt.tight_layout()

    attempts_chart_path = f"{chart_dirc}/user_{user_id}_attempts.png"
    plt.savefig(attempts_chart_path)  
    plt.close()

    #   Average Scores Per Subject Chart
    avg_scores = db.session.query(
        Subject.name,
        func.avg(Scores.total).label("avg_score")
    ).join(Chapters, Chapters.subject_id == Subject.id) \
     .join(Quiz, Quiz.chapter_id == Chapters.id) \
     .join(Scores, Scores.quiz_id == Quiz.id) \
     .filter(Scores.user_id == user_id) \
     .group_by(Subject.name).all()

    subjects_scored = [row[0] for row in avg_scores]
    avg_score_values = [row[1] for row in avg_scores]

    if not subjects_scored: 
        subjects_scored = ["No Data"]
        avg_score_values = [0]

    plt.figure(figsize=(10, 5))
    plt.bar(subjects_scored, avg_score_values, color='royalblue')
    plt.xlabel('Subjects')
    plt.ylabel('Average Score')
    plt.title('Your Average Score in Each Subject')
    plt.xticks(rotation=45)
    plt.ylim(0, 100)  # Assuming max score is 100
    plt.tight_layout()

    avg_scores_chart_path = f"{chart_dirc}/user_{user_id}_avg_scores.png"
    plt.savefig(avg_scores_chart_path)  # Save chart as PNG
    plt.close()

    return render_template('user_dashboard.html', user=user, quizzes=quiz_data,   
                           user_scores=user_scores, current_date=current_date)

@app.route('/view_quiz/<string:quiz_id>/<int:user_id>', methods=['GET', 'POST'])
def view_quiz(quiz_id, user_id):
    quiz = Quiz.query.get(quiz_id)
    user = User.query.get(user_id)
    questions=Question.query.filter_by(quiz_id=quiz_id).all()
    if not quiz or not user:
        return "Quiz or User not found", 404

    if request.method == 'POST':
        return redirect(url_for('exam', quiz_id=quiz_id, user_id=user_id))

    return render_template('quiz_display.html', quiz=quiz, user=user ,questions=questions)    

@app.route('/exam/<string:quiz_id>/<int:user_id>', methods=['GET', 'POST'])
def exam(quiz_id, user_id):
    quiz = Quiz.query.get(quiz_id)
    user = User.query.get(user_id)
    current_date = datetime.now().strftime('%d-%m-%Y')
    if not quiz or not user:
        return "Quiz or User not found", 404

    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    if request.method == 'POST':
        total_questions = len(questions)
        correct_answers = 0

        for question in questions:
            selected_option = request.form.get(f"option_{question.id}")
            is_correct = (selected_option == question.correct_response)

            response = UserResponse(
                user_id=user_id,
                quiz_id=quiz_id,
                question_id=question.id,
                selected_option=selected_option,
                is_correct=is_correct
            )
            db.session.add(response)

            if is_correct:
                correct_answers += 1

        score_percentage = (correct_answers / total_questions) * 100

        new_score = Scores(
            quiz_id=quiz_id,
            user_id=user_id,
            total=score_percentage,
            attempt_time=datetime.utcnow()
        )
        db.session.add(new_score)
        db.session.commit()

        return redirect(url_for('score_summary', score_id=new_score.id))

    return render_template('exam.html', quiz=quiz, user=user, questions=questions , current_date=current_date)

@app.route('/score_summary/<int:score_id>', methods=['GET'])
def score_summary(score_id):
    score = Scores.query.get(score_id)
    if not score:
        return "Score not found", 404
    
    quiz = Quiz.query.get(score.quiz_id)
    user = User.query.get(score.user_id)
    return render_template('score_summary.html', score=score, quiz=quiz, user=user)

@app.route('/user_scores/<int:user_id>', methods=['GET'])
def UserScores(user_id):
    user = User.query.get(user_id)
    if not user:
        return "User not found", 404
    
    scores = Scores.query.filter_by(user_id=user_id).all()
    responses = UserResponse.query.filter_by(user_id=user_id).all()
    return render_template('user_scores.html', user=user, scores=scores , responses=responses)











with app.app_context():
    db.create_all()
    initialize_admin()


if __name__ == '__main__':
    app.run(debug = True)


