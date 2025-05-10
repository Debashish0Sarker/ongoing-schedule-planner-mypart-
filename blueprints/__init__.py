# blueprints/__init__.py

from .auth.views    import auth_bp
from .student.views import student_bp
from .admin.views   import admin_bp

__all__ = ['auth_bp', 'student_bp', 'admin_bp']
