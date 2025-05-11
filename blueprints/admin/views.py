from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from extensions import db
from models import Notification, NotificationSetting

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
admin_notif_bp = Blueprint('admin_notif', __name__, url_prefix='/admin/notifications')

@admin_bp.route('/')
def panel():
    notifications = Notification.query.filter(
        (Notification.notification_type == 'admin') |
        (Notification.admin_notification == True)
    ).order_by(Notification.timestamp.desc()).all()
    
    return render_template('admin/panel.html', notifications=notifications)

@admin_bp.route('/mark_read/<int:nid>')
def mark_read(nid):
    notification = Notification.query.get_or_404(nid)
    notification.is_read = True
    db.session.commit()
    return redirect(url_for('admin.panel'))

@admin_bp.route('/mark_all_read')
def mark_all_read():
    Notification.query.filter(
        (Notification.notification_type == 'admin') |
        (Notification.admin_notification == True)
    ).update({'is_read': True})
    db.session.commit()
    return redirect(url_for('admin.panel'))

@admin_notif_bp.route('/settings')
def settings():
    if not hasattr(current_user, 'settings') or not current_user.settings:
        current_user.settings = NotificationSetting(
            user_id=current_user.id,
            admin_enabled=True
        )
        db.session.commit()
    
    return render_template('admin/notification_settings.html',
                         settings=current_user.settings)

@admin_bp.route('/test-notif')
def test_admin_notif():
    notif = Notification(
        message="TEST ADMIN NOTIFICATION",
        notification_type='admin',
        is_read=False,
        user_id=current_user.id
    )
    db.session.add(notif)
    db.session.commit()
    return "Admin test notification created"

@admin_bp.route('/test-registration')
def test_registration():
    notif = Notification(
        message="TEST: Registration request (student@test.com)",
        notification_type='admin',
        is_read=False,
        user_id=current_user.id
    )
    db.session.add(notif)
    db.session.commit()
    return "Test registration notification created"