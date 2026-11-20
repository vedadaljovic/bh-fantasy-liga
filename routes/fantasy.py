from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from services.fantasy_service import FantasyService

fantasy_bp = Blueprint('fantasy', __name__, url_prefix='/fantasy')


# ─────────────────────────────────────────────
#  MY TEAM
# ─────────────────────────────────────────────

@fantasy_bp.route('/my-team')
@login_required
def my_team():
    success, message, data = FantasyService.get_my_team(current_user.id)

    if not success:
        flash(message, 'info')
        return redirect(url_for('fantasy.pick_team'))

    return render_template('fantasy/my_team.html', **data)


# ─────────────────────────────────────────────
#  PICK TEAM
# ─────────────────────────────────────────────

@fantasy_bp.route('/pick-team', methods=['GET', 'POST'])
@login_required
def pick_team():
    from dao import fantasy_dao

    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Nisu poslani podaci'}), 400

        team_name       = data.get('team_name', '').strip()
        player_ids      = data.get('player_ids', [])
        captain_id      = data.get('captain_id')
        vice_captain_id = data.get('vice_captain_id')

        fantasy_team = fantasy_dao.get_fantasy_team_by_user(current_user.id)
        if not fantasy_team:
            ok, msg, fantasy_team = FantasyService.create_team(current_user.id, team_name)
            if not ok:
                return jsonify({'success': False, 'message': msg}), 400

        success, message = FantasyService.save_squad(
            current_user.id, player_ids, captain_id, vice_captain_id
        )

        if success:
            return jsonify({'success': True, 'message': message,
                            'redirect': url_for('fantasy.my_team')})
        return jsonify({'success': False, 'message': message}), 400

    # GET
    fantasy_team = fantasy_dao.get_fantasy_team_by_user(current_user.id)
    if fantasy_team:
        rows = fantasy_dao.get_team_players(fantasy_team.id)
        if len(rows) == 15:
            flash('Vaš tim je već odabran. Koristite transfere za izmjene.', 'info')
            return redirect(url_for('fantasy.my_team'))

    players = FantasyService.get_all_players()
    return render_template('fantasy/pick_team.html', players=players)


# ─────────────────────────────────────────────
#  TRANSFERS
# ─────────────────────────────────────────────

@fantasy_bp.route('/transfers')
@login_required
def transfers():
    success, message, data = FantasyService.get_transfers_info(current_user.id)

    if not success:
        flash(message, 'warning')
        return redirect(url_for('fantasy.pick_team'))

    all_players_pool = FantasyService.get_all_players()
    data['available_players'] = all_players_pool

    return render_template('fantasy/transfers.html', **data)


@fantasy_bp.route('/transfers', methods=['POST'])
@login_required
def make_transfer():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Nisu poslani podaci'}), 400

    player_out_id = data.get('player_out_id')
    player_in_id  = data.get('player_in_id')

    if not player_out_id or not player_in_id:
        return jsonify({'success': False, 'message': 'Nedostaju podaci o igračima'}), 400

    success, message, penalty = FantasyService.make_transfer(
        current_user.id, player_out_id, player_in_id
    )

    if success:
        return jsonify({'success': True, 'message': message, 'penalty': penalty})
    return jsonify({'success': False, 'message': message}), 400


# ─────────────────────────────────────────────
#  CHIPS
# ─────────────────────────────────────────────

@fantasy_bp.route('/activate-chip', methods=['POST'])
@login_required
def activate_chip():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Nisu poslani podaci'}), 400

    chip = data.get('chip')
    if chip not in ('triple_captain', 'bench_boost', 'wildcard'):
        return jsonify({'success': False, 'message': 'Nepoznati čip'}), 400

    success, message = FantasyService.activate_chip(current_user.id, chip)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'message': message}), 400


@fantasy_bp.route('/deactivate-chip', methods=['POST'])
@login_required
def deactivate_chip():
    success, message = FantasyService.deactivate_chip(current_user.id)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'message': message}), 400


# ─────────────────────────────────────────────
#  PLAYERS LIST
# ─────────────────────────────────────────────

@fantasy_bp.route('/players')
@login_required
def players():
    from dao import fantasy_dao, team_dao
    position    = request.args.get('position')
    all_players = FantasyService.get_all_players(position=position)
    teams       = team_dao.get_all_teams()
    return render_template('fantasy/players.html', players=all_players, teams=teams)


# ─────────────────────────────────────────────
#  GAMEWEEK
# ─────────────────────────────────────────────

@fantasy_bp.route('/gameweek')
@login_required
def gameweek():
    from dao import fantasy_dao
    from models.database import Gameweek, Fixture

    gw_number = request.args.get('id', type=int)

    if gw_number:
        gw = Gameweek.query.filter_by(number=gw_number).first()
    else:
        gw = fantasy_dao.get_active_gameweek()
        if not gw:
            gw = Gameweek.query.filter_by(is_finished=True).order_by(Gameweek.number.desc()).first()

    total_gameweeks = Gameweek.query.count()
    fixtures        = []
    starting        = []
    bench           = []
    fantasy_team    = None
    gameweek_points = 0
    gw_history      = []

    if gw:
        fixtures = (
            Fixture.query
            .filter_by(gameweek_id=gw.id)
            .order_by(Fixture.match_date.asc())
            .all()
        )

        fantasy_team = fantasy_dao.get_fantasy_team_by_user(current_user.id)
        if fantasy_team:
            rows = fantasy_dao.get_team_players(fantasy_team.id)
            for ftp, player, team in rows:
                entry = {
                    'player_id':       player.id,
                    'first_name':      player.first_name,
                    'last_name':       player.last_name,
                    'position':        player.position,
                    'total_points':    player.total_points,
                    'team_short':      team.short_name,
                    'is_captain':      ftp.is_captain,
                    'is_vice_captain': ftp.is_vice_captain,
                    'bench_order':     ftp.bench_order,
                }
                if ftp.is_starting:
                    starting.append(entry)
                else:
                    bench.append(entry)

            gw_record = fantasy_dao.get_team_gameweek_record(fantasy_team.id, gw.id)
            gameweek_points = gw_record.points if gw_record else 0

            history_rows = fantasy_dao.get_team_gameweek_history(fantasy_team.id)
            gw_history = [
                {'gameweek_number': g.number, 'points': ftg.points}
                for ftg, g in history_rows
            ]

    return render_template(
        'fantasy/gameweek.html',
        gameweek=gw,
        fixtures=fixtures,
        fantasy_team=fantasy_team,
        starting=starting,
        bench=bench,
        gameweek_points=gameweek_points,
        gw_history=gw_history,
        total_gameweeks=total_gameweeks,
    )


# ─────────────────────────────────────────────
#  LEADERBOARD
# ─────────────────────────────────────────────

@fantasy_bp.route('/leaderboard')
@login_required
def leaderboard():
    from dao import fantasy_dao
    data = FantasyService.get_leaderboard(user_id=current_user.id, limit=50)
    active_gw = fantasy_dao.get_active_gameweek()
    return render_template('fantasy/leaderboard.html', **data, active_gameweek=active_gw)


# ─────────────────────────────────────────────
#  CAPTAIN (AJAX)
# ─────────────────────────────────────────────

@fantasy_bp.route('/set-captain', methods=['POST'])
@login_required
def set_captain():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Nisu poslani podaci'}), 400

    captain_id      = data.get('captain_id')
    vice_captain_id = data.get('vice_captain_id')

    if not captain_id or not vice_captain_id:
        return jsonify({'success': False, 'message': 'Nedostaju podaci'}), 400

    success, message = FantasyService.set_captain(
        current_user.id, captain_id, vice_captain_id
    )

    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'message': message}), 400


@fantasy_bp.route('/swap', methods=['POST'])
@login_required
def swap_players():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Nisu poslani podaci'}), 400

    player_a_id = data.get('player_a_id')
    player_b_id = data.get('player_b_id')

    if not player_a_id or not player_b_id:
        return jsonify({'success': False, 'message': 'Nedostaju podaci'}), 400

    success, message, new_formation = FantasyService.swap_players(
        current_user.id, player_a_id, player_b_id
    )

    if success:
        return jsonify({'success': True, 'message': message, 'formation': new_formation})
    return jsonify({'success': False, 'message': message}), 400


# ─────────────────────────────────────────────
#  MATCH DETAIL
# ─────────────────────────────────────────────

@fantasy_bp.route('/match/<int:fixture_id>')
@login_required
def match_detail(fixture_id):
    from models.database import Fixture, MatchEvent, MatchLineup
    from datetime import datetime

    fixture = Fixture.query.get_or_404(fixture_id)
    events  = MatchEvent.query.filter_by(fixture_id=fixture_id).all()
    lineups = MatchLineup.query.filter_by(fixture_id=fixture_id).all()

    now = datetime.now()
    is_live = (
        not fixture.is_finished and
        fixture.match_date is not None and
        fixture.match_date <= now
    )

    return jsonify({
        'fixture_id':   fixture.id,
        'home_team':    fixture.home_team.name,
        'away_team':    fixture.away_team.name,
        'home_short':   fixture.home_team.short_name,
        'away_short':   fixture.away_team.short_name,
        'home_score':   fixture.home_score,
        'away_score':   fixture.away_score,
        'is_finished':  fixture.is_finished,
        'is_live':      is_live,
        'match_date':   fixture.match_date.strftime('%d. %b %Y, %H:%M') if fixture.match_date else None,
        'events': [
            {
                'minute':     e.minute,
                'event_type': e.event_type,
                'player':     e.player_name,
                'player2':    e.player2_name,
                'team_side':  e.team_side,
                'score_home': e.score_home,
                'score_away': e.score_away,
            }
            for e in events
        ],
        'lineups': {
            'home': [
                {
                    'name':    p.player_name,
                    'number':  p.shirt_number,
                    'is_gk':   p.is_goalkeeper,
                    'is_cap':  p.is_captain,
                    'starting': p.is_starting,
                }
                for p in lineups if p.team_side == 'home'
            ],
            'away': [
                {
                    'name':    p.player_name,
                    'number':  p.shirt_number,
                    'is_gk':   p.is_goalkeeper,
                    'is_cap':  p.is_captain,
                    'starting': p.is_starting,
                }
                for p in lineups if p.team_side == 'away'
            ],
        },
    })