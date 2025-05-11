from datetime import datetime
from flask_login import UserMixin
from extensions import db


# -- User model --
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id           = db.Column(db.Integer, primary_key=True)  # User ID (primary key)
    name         = db.Column(db.String(128), nullable=False)  # User's name
    email        = db.Column(db.String(128), unique=True, nullable=False)  # Email (unique)
    password     = db.Column(db.String(256), nullable=False)  # Password
    role         = db.Column(db.Enum('student', 'admin', name='user_roles'), nullable=False)  # User role
    
    # relationships
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')  # Relationship with Notification model

    settings = db.relationship(
        'NotificationSetting', 
        backref='user', 
        uselist=False,  # One-to-one relationship
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<User {self.email}>'



class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Foreign key linking to the User model
    message = db.Column(db.String(200))
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    admin_notification = db.Column(db.Boolean, default=False)  # Used in auth/views.py
    notification_type = db.Column(db.Enum('user', 'admin'))  # Used in admin/views.py
    notification_type = db.Column(db.Enum('user', 'admin', name='notification_types'), default='user')
    
    def __repr__(self):
        return f'<Notification {self.message}>'


class NotificationSetting(db.Model):
    __tablename__ = 'notification_settings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
<<<<<<< HEAD
    # Set default values here to avoid NULL values
    student_enabled = db.Column(db.Boolean, default=True)
    reminder_days = db.Column(db.Integer, default=1)  # Default value
    reminder_hours = db.Column(db.Integer, default=0)  # Default value
    quiz_reminder_days = db.Column(db.Integer, default=1, nullable=False)  # Default value
    quiz_reminder_hours = db.Column(db.Integer, default=0, nullable=False)  # Default value
=======
    # Student Settings
    student_enabled = db.Column(db.Boolean, default=True)
    reminder_days = db.Column(db.Integer, default=1)
    reminder_hours = db.Column(db.Integer, default=0)
    quiz_reminder_days = db.Column(db.Integer, default=1, nullable=False)
    quiz_reminder_hours = db.Column(db.Integer, default=0, nullable=False)
>>>>>>> 9dca34be3757adf19bd5eab9accbbdfd9b5fc196
    
    # Admin Settings
    admin_enabled = db.Column(db.Boolean, default=True)

<<<<<<< HEAD

=======
>>>>>>> 9dca34be3757adf19bd5eab9accbbdfd9b5fc196
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    topics = db.Column(db.String(200))  # Optional field for quiz topics

    def __repr__(self):
        return f'<Quiz {self.title}>'
# -- Course & Enrollment models --
class Course(db.Model):
    __tablename__ = 'courses'
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)

class StudentCourse(db.Model):
    __tablename__ = 'student_courses'
    student_id  = db.Column(
        db.Integer, db.ForeignKey('users.id'), primary_key=True
    )
    course_id   = db.Column(
        db.Integer, db.ForeignKey('courses.id'), primary_key=True
    )
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow)

# -- Assignment model --
class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Assignment {self.title}>'
