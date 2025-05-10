from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models import NotificationSetting

student_notif_bp = Blueprint('student_notif', __name__, url_prefix='/student/notifications')

@student_notif_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if current_user.role != 'student':
        return redirect(url_for('auth.login'))
    
    settings = current_user.settings or NotificationSetting(user_id=current_user.id)

    if request.method == 'POST':
        settings.student_enabled = 'enabled' in request.form
        settings.reminder_days = int(request.form.get('days', 1))
        settings.reminder_hours = int(request.form.get('hours', 0))
        db.session.commit()
        flash('Student notification settings updated!', 'success')
        return redirect(url_for('student_notif.settings'))

    return render_template('student/notification_settings.html', settings=settings)