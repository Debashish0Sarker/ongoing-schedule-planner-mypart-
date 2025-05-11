from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager, current_user, login_required
from flask_migrate import Migrate
from models import db, Assignment, User,Notification, Quiz
import notifications
from blueprints.auth.views import auth_bp
from blueprints.student.views import student_bp
from blueprints.notifications.views import notif_bp
from config import Config
from blueprints.admin.views import admin_bp
from blueprints.student.notifications import student_notif_bp
from blueprints.admin.notifications import admin_notif_bp

<<<<<<< HEAD

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

=======
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
>>>>>>> 9dca34be3757adf19bd5eab9accbbdfd9b5fc196
    
    # Initialize extensions
    db.init_app(app)
    
    # Setup login manager
    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Initialize migrate
    Migrate(app, db)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(notif_bp)
    app.register_blueprint(admin_bp)  # Add this with other blueprint registrations
    app.register_blueprint(student_notif_bp)
    app.register_blueprint(admin_notif_bp)
    
    # Routes
    @app.route('/')
    def home():
        return redirect(url_for('auth.login'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        assignments = Assignment.query.filter_by(user_id=current_user.id).all()
        quizzes = Quiz.query.filter_by(user_id=current_user.id).all()
        return render_template('dashboard.html', assignments=assignments, quizzes=quizzes)
    
    return app

app = create_app()



@app.route('/test-notification-system')
def test_notification():
    from datetime import datetime, timedelta
    
    # First clean up previous test assignments
    Assignment.query.filter(Assignment.title.like("TEST ASSIGNMENT%")).delete()
    
    # Create SINGLE test assignment
    test_assignment = Assignment(
        title="TEST ASSIGNMENT",
        deadline=datetime.utcnow() + timedelta(days=1),  # Due tomorrow
        user_id=current_user.id
    )
    db.session.add(test_assignment)
    db.session.commit()
    
    # Trigger notification check
    from notifications import check_upcoming
    check_upcoming()
    
    return "Clean test created and checked"
# Context processor
@app.context_processor
def inject_counts():
    from models import Notification  # Import here to avoid circular imports
    counts = {}
    if current_user.is_authenticated:
        counts['user_notifications'] = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).count()
        
        if current_user.role == 'admin':
            counts['admin_notifications'] = Notification.query.filter_by(
                notification_type='admin',
                is_read=False
            ).count()
    return counts

# Initialize scheduler after app is fully configured
scheduler = notifications.start_scheduler(app)  # Make sure notifications.py returns the scheduler

if __name__ == '__main__':
    # Only start scheduler when running directly, not during migrations
    if not scheduler.running:
        scheduler.start()
        app.logger.info("🔔 Notification scheduler started")
    app.run(debug=True)