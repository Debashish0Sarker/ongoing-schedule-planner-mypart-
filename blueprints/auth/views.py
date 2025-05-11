from flask import (
    Blueprint, render_template,
    request, redirect, url_for, flash
)
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager
from models    import User,Notification

# no URL prefix → routes are /login, /register, /logout
auth_bp = Blueprint('auth', __name__)

# tell Flask-Login how to load a user from the session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            # send them to the right dashboard
            if user.role == 'student':
                return redirect(url_for('student.dashboard'))
            else:
                return redirect(url_for('admin.dashboard'))

        flash('Invalid email or password.', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        # guard against duplicate emails
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'warning')
            return redirect(url_for('auth.register'))

        # create & persist new student
        u = User(
            name     = name,
            email    = email,
            password = generate_password_hash(password),
            role     = 'student'
        )
        

    
        admin_notif = Notification(
        message=f"New registration request: {email}",  # Use email variable
        admin_notification=True,
        notification_type='admin',
        is_read=False
        )
        db.session.add(admin_notif)
        db.session.add(u)
        db.session.commit()

        flash('Registration submitted for approval', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
