from flask import Blueprint, render_template
from flask_login import login_required

fantasy_bp = Blueprint('fantasy', __name__, url_prefix='/fantasy')

@fantasy_bp.route('/my-team')
@login_required
def my_team():
    return render_template('fantasy/my_team.html')

@fantasy_bp.route('/pick-team')
@login_required
def pick_team():
    return render_template('fantasy/pick_team.html')

@fantasy_bp.route('/transfers')
@login_required
def transfers():
    return render_template('fantasy/transfers.html')

@fantasy_bp.route('/players')
@login_required
def players():
    return render_template('fantasy/players.html')

@fantasy_bp.route('/gameweek')
@login_required
def gameweek():
    return render_template('fantasy/gameweek.html')

@fantasy_bp.route('/leaderboard')
@login_required
def leaderboard():
    return render_template('fantasy/leaderboard.html')
