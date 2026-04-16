from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from services.auth_service import AuthService
from models.database import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('news.feed'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        success, message, user = AuthService.login(email, password)
        
        if success:
            login_user(user, remember=True)
            flash(f"Dobrodošli, {user.username}!", 'success')
            return redirect(url_for('news.feed'))
        else:
            flash(message, 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('news.feed'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        if password != password_confirm:
            flash("Lozinke se ne poklapaju", 'danger')
            return render_template('auth/register.html')
        
        success, message, user = AuthService.register(username, email, password)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'danger')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Odjavljeni ste.", 'info')
    return redirect(url_for('news.feed'))
