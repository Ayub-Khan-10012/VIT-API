from app import db

class User(db.Model):
    __tablename__ = 'users'

    # Fields for the User model
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Hashed password
    role = db.Column(db.String(50), nullable=False)  # Roles: Student, Faculty, Contributor

    # Relationship with assignments (clarifying foreign_keys for both student_id and faculty_id)
    assignments = db.relationship('Assignment', foreign_keys='Assignment.student_id', backref='student', lazy=True)
    feedbacks = db.relationship('Assignment', foreign_keys='Assignment.faculty_id', backref='reviewer', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    file_url = db.Column(db.String(512), nullable=False)  # URL or path to the uploaded file
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Student who submitted
    feedback = db.Column(db.Text, nullable=True)  # Faculty's feedback
    faculty_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Faculty who reviewed it

    def __repr__(self):
        return f"<Assignment {self.title} by User {self.student_id}>"

class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)

    def __repr__(self):
        return f"<Feedback {self.content}>"
