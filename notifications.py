from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app
from datetime import datetime, timedelta
from extensions import db
from models import User, Assignment, Notification, NotificationSetting, Quiz
from blueprints.notifications.views import notif_bp
from flask_login import current_user, login_required

def check_upcoming():
    with current_app.app_context():
        now = datetime.utcnow()
        
        # Get all students with notifications enabled
        students = User.query.join(NotificationSetting).filter(
            User.role == 'student',
            NotificationSetting.student_enabled == True
        ).all()

        for student in students:
            settings = student.settings
            if not settings:
                continue

            # Handle None values safely
            reminder_days = settings.reminder_days if settings.reminder_days is not None else 1
            reminder_hours = settings.reminder_hours if settings.reminder_hours is not None else 0
            quiz_reminder_days = settings.quiz_reminder_days if settings.quiz_reminder_days is not None else 1
            quiz_reminder_hours = settings.quiz_reminder_hours if settings.quiz_reminder_hours is not None else 0

            # Calculate reminder times
            assignment_reminder_time = now + timedelta(
                days=reminder_days,
                hours=reminder_hours
            )
            
            quiz_reminder_time = now + timedelta(
                days=quiz_reminder_days,
                hours=quiz_reminder_hours
            )

            # Check assignments
            assignments = Assignment.query.filter(
                Assignment.user_id == student.id,
                Assignment.deadline <= assignment_reminder_time,
                Assignment.deadline >= now
            ).all()

            for assignment in assignments:
                if not Notification.query.filter(
                    Notification.user_id == student.id,
                    Notification.message.like(f"%{assignment.title}%"),
                    Notification.timestamp >= now - timedelta(hours=1)
                ).first():
                    db.session.add(Notification(
                        user_id=student.id,
                        message=f"Reminder: '{assignment.title}' is due soon!",
                        is_read=False,
                        notification_type='user'
                    ))

            # Check quizzes
            quizzes = Quiz.query.filter(
                Quiz.user_id == student.id,
                Quiz.deadline <= quiz_reminder_time,
                Quiz.deadline >= now
            ).all()

            for quiz in quizzes:
                if not Notification.query.filter(
                    Notification.user_id == student.id,
                    Notification.message.like(f"%{quiz.title}%"),
                    Notification.timestamp >= now - timedelta(hours=1)
                ).first():
                    topics = f" on {quiz.topics}" if quiz.topics else ""
                    db.session.add(Notification(
                        user_id=student.id,
                        message=f"Study reminder: '{quiz.title}' quiz{topics} coming up!",
                        is_read=False,
                        notification_type='user'
                    ))

        db.session.commit()

def start_scheduler(app):
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        check_upcoming,
        'interval',
        minutes=15,
        id='deadline_check',
        misfire_grace_time=60
    )
    
    if not scheduler.running:
        scheduler.start()
        app.logger.info("Notification scheduler started")  # Use app.logger instead
    
    return scheduler

@notif_bp.route('/test-notif')
@login_required
def test_user_notif():
    notif = Notification(
        message="TEST USER NOTIFICATION",
        user_id=current_user.id,
        notification_type='user',
        is_read=False
    )
    db.session.add(notif)
    db.session.commit()
<<<<<<< HEAD
    return "User test notification created"
=======
    return "User test notification created"
>>>>>>> 9dca34be3757adf19bd5eab9accbbdfd9b5fc196
