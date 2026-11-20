from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from services.user_service import UserService

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/profile')
@login_required
def profile():
    data = UserService.get_profile_data(current_user.id)
    return render_template('user/profile.html', **data)


@user_bp.route('/update-team-name', methods=['POST'])
@login_required
def update_team_name():
    data     = request.get_json()
    new_name = data.get('team_name', '').strip() if data else ''
    success, message = UserService.update_team_name(current_user.id, new_name)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'message': message}), 400


@user_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Nisu poslani podaci'}), 400

    success, message = UserService.change_password(
        current_user.id,
        data.get('current_password', ''),
        data.get('new_password', ''),
        data.get('confirm_password', ''),
    )
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'message': message}), 400


@user_bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Nisu poslani podaci'}), 400

    success, message = UserService.delete_account(
        current_user.id,
        data.get('password', '')
    )
    if success:
        logout_user()
        return jsonify({'success': True, 'redirect': url_for('auth.login')})
    return jsonify({'success': False, 'message': message}), 400