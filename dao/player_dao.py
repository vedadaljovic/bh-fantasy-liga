from models.database import db, Player, Team


# ─────────────────────────────────────────────
#  PLAYERS
# ─────────────────────────────────────────────

def get_all_players(position=None):
    query = (
        db.session.query(Player, Team)
        .join(Team, Player.team_id == Team.id)
        .filter(Player.is_available == True)
    )
    if position:
        query = query.filter(Player.position == position)
    return query.order_by(Player.position, Player.last_name).all()


def get_player_by_id(player_id):
    return (
        db.session.query(Player, Team)
        .join(Team, Player.team_id == Team.id)
        .filter(Player.id == player_id)
        .first()
    )


def get_players_by_position(position):
    return (
        db.session.query(Player, Team)
        .join(Team, Player.team_id == Team.id)
        .filter(Player.position == position, Player.is_available == True)
        .order_by(Player.total_points.desc())
        .all()
    )


def get_player_season_stats(player_id):
    from models.database import PlayerGameweekStats
    rows = PlayerGameweekStats.query.filter_by(player_id=player_id).all()
    return {
        'goals':        sum(r.goals         for r in rows),
        'assists':      sum(r.assists        for r in rows),
        'minutes':      sum(r.minutes_played for r in rows),
        'clean_sheets': sum(r.clean_sheet    for r in rows),
        'yellow_cards': sum(r.yellow_cards   for r in rows),
        'red_cards':    sum(r.red_cards      for r in rows),
    }