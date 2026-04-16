from flask import Blueprint, render_template
from flask_login import login_required, current_user
from functools import wraps
from flask import redirect, url_for, flash

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash("Samo administratori mogu pristupiti ovoj stranici.", 'danger')
            return redirect(url_for('news.feed'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/players')
@login_required
@admin_required
def players():
    return render_template('admin/players.html')

@admin_bp.route('/teams')
@login_required
@admin_required
def teams():
    return render_template('admin/teams.html')

@admin_bp.route('/gameweeks')
@login_required
@admin_required
def gameweeks():
    return render_template('admin/gameweeks.html')

@admin_bp.route('/news')
@login_required
@admin_required
def news():
    return render_template('admin/news.html')

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    return render_template('admin/users.html')
