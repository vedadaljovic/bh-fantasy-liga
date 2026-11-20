from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash("Samo administratori mogu pristupiti ovoj stranici.", 'danger')
            return redirect(url_for('news.feed'))
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    from models.database import User, Player, Gameweek, News, FantasyTeam
    from datetime import datetime

    user_count    = User.query.filter(User.role != 'admin').count()
    player_count  = Player.query.count()
    news_count    = News.query.count()
    team_count    = FantasyTeam.query.count()
    active_gw     = Gameweek.query.filter_by(is_active=True).first()

    recent_users = (
        User.query
        .filter(User.role != 'admin')
        .order_by(User.created_at.desc())
        .limit(10)
        .all()
    )

    now = datetime.now()
    transfers_open = active_gw and active_gw.deadline > now if active_gw else False

    return render_template('admin/dashboard.html',
        user_count=user_count,
        player_count=player_count,
        news_count=news_count,
        team_count=team_count,
        active_gw=active_gw,
        recent_users=recent_users,
        transfers_open=transfers_open,
    )


# ─────────────────────────────────────────────
#  PLAYERS
# ─────────────────────────────────────────────

@admin_bp.route('/players')
@login_required
@admin_required
def players():
    from models.database import Player, Team
    all_players = (
        Player.query
        .join(Team, Player.team_id == Team.id)
        .order_by(Player.last_name.asc())
        .all()
    )
    teams = Team.query.order_by(Team.name.asc()).all()
    return render_template('admin/players.html', players=all_players, teams=teams)


@admin_bp.route('/players/add', methods=['POST'])
@login_required
@admin_required
def add_player():
    from models.database import db, Player
    data = request.get_json()
    try:
        player = Player(
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip(),
            team_id=int(data['team_id']),
            position=data['position'],
            price=float(data['price']),
            is_available=data.get('is_available', True),
        )
        db.session.add(player)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Igrač uspješno dodan'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@admin_bp.route('/players/<int:player_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_player(player_id):
    from models.database import db, Player
    player = Player.query.get_or_404(player_id)
    data = request.get_json()
    try:
        if 'first_name'   in data: player.first_name   = data['first_name'].strip()
        if 'last_name'    in data: player.last_name     = data['last_name'].strip()
        if 'team_id'      in data: player.team_id       = int(data['team_id'])
        if 'position'     in data: player.position      = data['position']
        if 'price'        in data: player.price         = float(data['price'])
        if 'is_available' in data: player.is_available  = data['is_available']
        db.session.commit()
        return jsonify({'success': True, 'message': 'Igrač uspješno ažuriran'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@admin_bp.route('/players/<int:player_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_player(player_id):
    from models.database import db, Player
    player = Player.query.get_or_404(player_id)
    try:
        db.session.delete(player)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Igrač obrisan'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


# ─────────────────────────────────────────────
#  TEAMS
# ─────────────────────────────────────────────

@admin_bp.route('/teams')
@login_required
@admin_required
def teams():
    from models.database import Team, Player
    from sqlalchemy import func
    teams_with_count = (
        Team.query
        .outerjoin(Player, Player.team_id == Team.id)
        .add_columns(func.count(Player.id).label('player_count'))
        .group_by(Team.id)
        .order_by(Team.name.asc())
        .all()
    )
    return render_template('admin/teams.html', teams=teams_with_count)


@admin_bp.route('/teams/<int:team_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_team(team_id):
    from models.database import db, Team
    team = Team.query.get_or_404(team_id)
    data = request.get_json()
    try:
        if 'name'       in data: team.name       = data['name'].strip()
        if 'short_name' in data: team.short_name = data['short_name'].strip().upper()
        if 'logo_url'   in data: team.logo_url   = data['logo_url'].strip()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Klub uspješno ažuriran'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


# ─────────────────────────────────────────────
#  GAMEWEEKS
# ─────────────────────────────────────────────

@admin_bp.route('/gameweeks')
@login_required
@admin_required
def gameweeks():
    from models.database import Gameweek, FantasyTeam
    from datetime import datetime
    all_gws    = Gameweek.query.order_by(Gameweek.number.asc()).all()
    active_gw  = Gameweek.query.filter_by(is_active=True).first()
    team_count = FantasyTeam.query.count()
    now        = datetime.now()
    return render_template('admin/gameweeks.html',
        gameweeks=all_gws,
        active_gw=active_gw,
        team_count=team_count,
        now=now,
    )


@admin_bp.route('/gameweeks/<int:gw_id>/set-active', methods=['POST'])
@login_required
@admin_required
def set_active_gameweek(gw_id):
    from models.database import db, Gameweek
    try:
        Gameweek.query.update({'is_active': False})
        gw = Gameweek.query.get_or_404(gw_id)
        gw.is_active = True
        db.session.commit()
        return jsonify({'success': True, 'message': f'Kolo {gw.number} je sada aktivno'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@admin_bp.route('/gameweeks/<int:gw_id>/finish', methods=['POST'])
@login_required
@admin_required
def finish_gameweek(gw_id):
    from models.database import db, Gameweek, FantasyTeam, FantasyTeamPlayer, \
                                  PlayerGameweekStats, Player, FantasyTeamGameweek
    from services.points_service import calculate_fantasy_team_points

    try:
        gw = Gameweek.query.get_or_404(gw_id)

        stat_rows = PlayerGameweekStats.query.filter_by(gameweek_id=gw.id).all()
        gameweek_stats = {
            s.player_id: {
                'minutes_played': s.minutes_played,
                'goals':          s.goals,
                'assists':        s.assists,
                'clean_sheet':    s.clean_sheet,
                'saves':          s.saves if hasattr(s, 'saves') else 0,
                'yellow_cards':   s.yellow_cards,
                'red_cards':      s.red_cards,
            }
            for s in stat_rows
        }

        fantasy_teams = FantasyTeam.query.all()
        for ft in fantasy_teams:
            squad_rows = (
                db.session.query(FantasyTeamPlayer, Player)
                .join(Player, FantasyTeamPlayer.player_id == Player.id)
                .filter(FantasyTeamPlayer.fantasy_team_id == ft.id)
                .all()
            )

            fantasy_players = [
                {
                    'player_id':      ftp.player_id,
                    'position':       player.position,
                    'is_starting':    ftp.is_starting,
                    'is_captain':     ftp.is_captain,
                    'is_vice_captain': ftp.is_vice_captain,
                }
                for ftp, player in squad_rows
            ]

            chip = ft.chip_used
            gw_points = calculate_fantasy_team_points(fantasy_players, gameweek_stats, chip=chip)

            # Mark chip as permanently used and clear active chip
            if chip == 'triple_captain':
                ft.triple_captain_used = True
            elif chip == 'bench_boost':
                ft.bench_boost_used = True
            elif chip == 'wildcard':
                ft.wildcard_used = True
            ft.chip_used = None

            record = FantasyTeamGameweek.query.filter_by(
                fantasy_team_id=ft.id,
                gameweek_id=gw.id
            ).first()
            if record:
                record.points = gw_points
            else:
                db.session.add(FantasyTeamGameweek(
                    fantasy_team_id=ft.id,
                    gameweek_id=gw.id,
                    points=gw_points,
                ))

            ft.gameweek_points = gw_points
            ft.total_points    = (ft.total_points or 0) + gw_points

        gw.is_active   = False
        gw.is_finished = True
        db.session.commit()

        return jsonify({'success': True, 'message': f'Kolo {gw.number} je završeno i poeni su izračunati'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400


# ─────────────────────────────────────────────
#  NEWS
# ─────────────────────────────────────────────

@admin_bp.route('/news')
@login_required
@admin_required
def news():
    from models.database import News
    articles = News.query.order_by(News.created_at.desc()).all()
    return render_template('admin/news.html', articles=articles)


@admin_bp.route('/news/add', methods=['POST'])
@login_required
@admin_required
def add_news():
    from models.database import db, News
    from datetime import datetime
    data = request.get_json()
    try:
        article = News(
            admin_id=current_user.id,
            title=data['title'].strip(),
            content=data['content'].strip(),
            excerpt=data.get('excerpt', data['content'][:200]).strip(),
            image_url=data.get('image_url', '').strip() or None,
            category=data.get('category', 'Vijesti'),
            created_at=datetime.utcnow(),
        )
        db.session.add(article)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Vijest uspješno objavljena'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@admin_bp.route('/news/<int:news_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_news(news_id):
    from models.database import db, News
    article = News.query.get_or_404(news_id)
    try:
        db.session.delete(article)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Vijest obrisana'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


# ─────────────────────────────────────────────
#  USERS
# ─────────────────────────────────────────────

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    from models.database import User
    all_users = (
        User.query
        .filter(User.role != 'admin')
        .order_by(User.created_at.desc())
        .all()
    )
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    from models.database import User, FantasyTeam
    user = User.query.get_or_404(user_id)
    fantasy_team = FantasyTeam.query.filter_by(user_id=user_id).first()
    return jsonify({
        'id':           user.id,
        'username':     user.username,
        'email':        user.email,
        'is_active':    user.is_active,
        'created_at':   user.created_at.strftime('%d. %b %Y') if user.created_at else '—',
        'fantasy_team': fantasy_team.team_name if fantasy_team else None,
        'total_points': fantasy_team.total_points if fantasy_team else 0,
        'gw_points':    fantasy_team.gameweek_points if fantasy_team else 0,
    })


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    from models.database import db, User
    user = User.query.get_or_404(user_id)
    try:
        user.is_active = not user.is_active
        db.session.commit()
        status = 'aktiviran' if user.is_active else 'deaktiviran'
        return jsonify({'success': True, 'message': f'Korisnik {status}', 'is_active': user.is_active})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    from models.database import db, User, FantasyTeam, FantasyTeamPlayer, Transfer, FantasyTeamGameweek
    user = User.query.get_or_404(user_id)
    try:
        ft = FantasyTeam.query.filter_by(user_id=user_id).first()
        if ft:
            FantasyTeamPlayer.query.filter_by(fantasy_team_id=ft.id).delete()
            Transfer.query.filter_by(fantasy_team_id=ft.id).delete()
            FantasyTeamGameweek.query.filter_by(fantasy_team_id=ft.id).delete()
            db.session.delete(ft)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Korisnik obrisan'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# ─────────────────────────────────────────────
#  MATCHDAY RUNNERS
# ─────────────────────────────────────────────

@admin_bp.route('/run/scrape-news', methods=['POST'])
@login_required
@admin_required
def run_scrape_news():
    try:
        import subprocess, sys
        result = subprocess.run(
            [sys.executable, 'scraper/news_scraper.py'],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            return jsonify({'success': True, 'message': 'Scraper vijesti završio uspješno'})
        return jsonify({'success': False, 'message': result.stderr or 'Greška u scraperu'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/run/scrape-fixtures', methods=['POST'])
@login_required
@admin_required
def run_scrape_fixtures():
    try:
        import subprocess, sys
        result = subprocess.run(
            [sys.executable, 'scraper/fixtures_scraper.py'],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            return jsonify({'success': True, 'message': 'Scraper rasporeda završio uspješno'})
        return jsonify({'success': False, 'message': result.stderr or 'Greška u scraperu'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/run/scrape-live', methods=['POST'])
@login_required
@admin_required
def run_scrape_live():
    try:
        import subprocess, sys
        subprocess.Popen(
            [sys.executable, 'scraper/live_scraper.py'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return jsonify({'success': True, 'message': 'Live scraper pokrenut u pozadini'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500