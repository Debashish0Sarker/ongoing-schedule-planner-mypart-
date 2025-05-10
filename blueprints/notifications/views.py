from flask import (
    Blueprint, render_template, request,
    flash, redirect, url_for, jsonify
)
from flask_login import login_required, current_user
from extensions import db
from models import Notification, NotificationSetting

notif_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@notif_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    # Get or create settings for current user
    settings = current_user.settings
    if not settings:
        settings = NotificationSetting(user_id=current_user.id)
        db.session.add(settings)
        db.session.commit()

    if request.method == 'POST':
        # Update settings from form data
        settings.enabled = 'enabled' in request.form
        settings.admin_notifications = 'admin_notifications' in request.form
        settings.user_notifications = 'user_notifications' in request.form
        settings.days_before = int(request.form.get('days_before', 1))
        settings.hours_before = int(request.form.get('hours_before', 0))
        
        db.session.commit()
        flash('Notification settings updated!', 'success')
        return redirect(url_for('notifications.settings'))

    return render_template('notifications/settings.html', settings=settings)

@notif_bp.route('/history')
@login_required
def history():  # Function name should be unique
    items = Notification.query.filter_by(
        user_id=current_user.id,
        notification_type='user'
    ).order_by(Notification.timestamp.desc()).all()
    return render_template('notifications/history.html', notifications=items)

@notif_bp.route('/mark_all')
@login_required
def mark_all():
    """Mark all unread notifications as read."""
    Notification.query.filter_by(
        user_id=current_user.id, is_read=False  # Changed from read to is_read
    ).update({'is_read': True})  # Changed from read to is_read
    db.session.commit()
    flash('All notifications marked as read.', 'info')
    return redirect(request.referrer or url_for('notifications.history'))

@notif_bp.route('/mark_read/<int:nid>')
@login_required
def mark_read(nid):
    # Find the notification by ID or return 404 if not found
    notification = Notification.query.get_or_404(nid)
    
    # Mark the notification as read
    notification.is_read = True  # Keep this as is
    
    # Commit the change to the database
    db.session.commit()
    
    # Redirect back to the notification history page
    return redirect(url_for('notifications.history'))

@notif_bp.route('/unread_json')
@login_required
def unread_json():
    """
    Return any *new* unread notifications since last poll,
    in JSON form for the toast pop-up script.
    """
    unread = Notification.query.filter_by(
        user_id=current_user.id, is_read=False  # Changed from read to is_read
    ).order_by(Notification.timestamp).all()

    out = [{'id': n.id, 'message': n.message} for n in unread]

    # now mark them as read so they won't reappear
    for n in unread:
        n.is_read = True  # Changed from read to is_read
    db.session.commit()

    return jsonify(out)