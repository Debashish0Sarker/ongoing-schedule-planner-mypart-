from flask import (
    Blueprint, render_template,
    request, redirect, url_for, flash, current_app
)
from flask_login import login_required, current_user
from datetime import datetime, timezone
from extensions import db
from models import Assignment, Notification, NotificationSetting,Quiz
from sqlalchemy import text

student_bp = Blueprint('student', __name__)
student_notif_bp = Blueprint('student_notif', __name__, url_prefix='/student/notifications')

@student_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    assignments = Assignment.query.filter_by(
        user_id=current_user.id
    ).order_by(Assignment.deadline.asc()).all()
    quizzes = Quiz.query.filter_by(user_id=current_user.id).all()
    
    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        notification_type='user'
    ).order_by(text('timestamp desc')).limit(10).all()
    
    return render_template('student/dashboard.html', 
                        assignments=assignments,
                        notifications=notifications,quizzes=quizzes)

@student_bp.route('/deadlines/new', methods=['GET','POST'])
@login_required
def new_deadline():
    if current_user.role != 'student':
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        try:
            # Parse datetime without timezone first
            naive_datetime = datetime.strptime(
                request.form['due_date'], 
                '%Y-%m-%dT%H:%M'
            )
            # Make it timezone-aware (UTC)
            deadline = naive_datetime.replace(tzinfo=timezone.utc)
            
            a = Assignment(
                user_id=current_user.id,
                title=request.form['title'],
                deadline=deadline
            )
            db.session.add(a)
            db.session.commit()
            flash('Assignment added successfully!', 'success')
            return redirect(url_for('student.dashboard'))
            
        except ValueError as e:
            current_app.logger.error(f"Date error: {str(e)}")
            flash('Invalid date format. Please use the date picker.', 'error')
        except KeyError as e:
            current_app.logger.error(f"Missing field: {str(e)}")
            flash('Please fill all required fields.', 'error')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating assignment: {str(e)}")
            flash('Failed to create assignment', 'danger')
            
    return render_template('student/new_deadline.html')

@student_notif_bp.route('/settings')
@login_required
def settings():
    if current_user.role != 'student':
        return redirect(url_for('auth.login'))
    
    if not hasattr(current_user, 'settings') or not current_user.settings:
        current_user.settings = NotificationSetting(
            user_id=current_user.id,
            student_enabled=True,
            reminder_days=1,
            reminder_hours=0
        )
        db.session.commit()
    
    return render_template('student/notification_settings.html', 
                         settings=current_user.settings)
@student_bp.route('/quizzes/new', methods=['GET', 'POST'])
@login_required
def new_quiz():
    if request.method == 'POST':
        try:
            deadline = datetime.strptime(
                request.form['due_date'], 
                '%Y-%m-%dT%H:%M'
            ).replace(tzinfo=timezone.utc)
            
            q = Quiz(
                user_id=current_user.id,
                title=request.form['title'],
                deadline=deadline,
                topics=request.form.get('topics', '')
            )
            db.session.add(q)
            db.session.commit()
            flash('Quiz added successfully!', 'success')
            return redirect(url_for('student.dashboard'))
            
        except ValueError:
            flash('Invalid date format', 'error')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating quiz: {str(e)}")
            flash('Failed to create quiz', 'danger')
            
    return render_template('student/new_quiz.html')