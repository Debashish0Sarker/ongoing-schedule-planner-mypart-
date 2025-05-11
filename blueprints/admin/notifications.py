from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models import NotificationSetting

admin_notif_bp = Blueprint('admin_notif', __name__, url_prefix='/admin/notifications')

@admin_notif_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    
    settings = current_user.settings or NotificationSetting(user_id=current_user.id)

    if request.method == 'POST':
        settings.admin_enabled = 'enabled' in request.form
        db.session.commit()
        flash('Admin notification settings updated!', 'success')
        return redirect(url_for('admin_notif.settings'))

    return render_template('admin/notification_settings.html', settings=settings)