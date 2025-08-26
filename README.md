# Quiz-Master
Quiz Master-V1 is a full-featured Flask web application designed to streamline the management and analysis of academic quizzes. The system is powered by Python and SQLAlchemy ORM, ensuring robust, scalable, and maintainable code architecture.

### Features
User Management: Secure registration, login, and role-based access (Admin/Student).

Quiz Workflow: Create, edit, and delete subjects, chapters, quizzes, and questions from the admin dashboard.

Live Analytics: Automatic generation of performance charts per subject (top scorers, user attempts, average scores) using Matplotlib.

Student Dashboard: Individual reports for quiz attempts, scores, and progress.

Admin Controls: Enable/disable users, search users/quizzes, and manage academic records.

Database: Fully normalized schema using SQLAlchemy models for Users, Subjects, Chapters, Quizzes, Questions, Scores, and User Responses.

### Tech Stack: Flask 3, SQLAlchemy ORM, Python 3.2, Matplotlib.

#### Installation
Clone the repository.

#### Install dependencies:
pip install -r requirements.txt


#### Run the application:
python app.py

Usage
Access via localhost:5000.

Admin login with default credentials:
Username: admin@iitmbs
Password: 222

Customize subjects, chapters, and quizzes from the admin dashboard.

File Structure
app.py: Application entry point, route definitions, charts, and business logic.

model.py: SQLAlchemy database models for core entities.

requirements.txt: Dependency list.
