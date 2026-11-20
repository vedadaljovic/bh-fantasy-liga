from models.database import (
    db, FantasyTeam, FantasyTeamPlayer, FantasyTeamGameweek,
    Transfer, Player, Team, Gameweek
)


# ─────────────────────────────────────────────
#  FANTASY TEAM
# ─────────────────────────────────────────────

def get_fantasy_team_by_user(user_id):
    return FantasyTeam.query.filter_by(user_id=user_id).first()


def create_fantasy_team(user_id, team_name, budget_remaining=100.0):
    team = FantasyTeam(
        user_id=user_id,
        team_name=team_name,
        budget_remaining=budget_remaining
    )
    db.session.add(team)
    db.session.commit()
    return team


def update_fantasy_team_budget(fantasy_team_id, budget_remaining):
    FantasyTeam.query.filter_by(id=fantasy_team_id).update(
        {'budget_remaining': budget_remaining}
    )
    db.session.commit()


def update_fantasy_team_points(fantasy_team_id, total_points, gameweek_points):
    FantasyTeam.query.filter_by(id=fantasy_team_id).update({
        'total_points': total_points,
        'gameweek_points': gameweek_points
    })
    db.session.commit()


# ─────────────────────────────────────────────
#  FANTASY TEAM PLAYERS
# ─────────────────────────────────────────────

def get_team_players(fantasy_team_id):
    """
    Return all squad members with player + club info joined.
    Starting XI first, then bench ordered by bench_order.
    """
    return (
        db.session.query(FantasyTeamPlayer, Player, Team)
        .join(Player, FantasyTeamPlayer.player_id == Player.id)
        .join(Team, Player.team_id == Team.id)
        .filter(FantasyTeamPlayer.fantasy_team_id == fantasy_team_id)
        .order_by(FantasyTeamPlayer.is_starting.desc(), FantasyTeamPlayer.bench_order.asc())
        .all()
    )


def add_player_to_team(fantasy_team_id, player_id, is_starting=True,
                       is_captain=False, is_vice_captain=False, bench_order=None):
    entry = FantasyTeamPlayer(
        fantasy_team_id=fantasy_team_id,
        player_id=player_id,
        is_starting=is_starting,
        is_captain=is_captain,
        is_vice_captain=is_vice_captain,
        bench_order=bench_order
    )
    db.session.add(entry)
    db.session.commit()
    return entry


def remove_player_from_team(fantasy_team_id, player_id):
    FantasyTeamPlayer.query.filter_by(
        fantasy_team_id=fantasy_team_id,
        player_id=player_id
    ).delete()
    db.session.commit()


def player_already_in_team(fantasy_team_id, player_id):
    return FantasyTeamPlayer.query.filter_by(
        fantasy_team_id=fantasy_team_id,
        player_id=player_id
    ).first() is not None


def count_players_from_same_club(fantasy_team_id, team_id):
    return (
        db.session.query(FantasyTeamPlayer)
        .join(Player, FantasyTeamPlayer.player_id == Player.id)
        .filter(
            FantasyTeamPlayer.fantasy_team_id == fantasy_team_id,
            Player.team_id == team_id
        )
        .count()
    )


def get_player_count_by_position(fantasy_team_id):
    rows = (
        db.session.query(Player.position, db.func.count().label('cnt'))
        .join(FantasyTeamPlayer, FantasyTeamPlayer.player_id == Player.id)
        .filter(FantasyTeamPlayer.fantasy_team_id == fantasy_team_id)
        .group_by(Player.position)
        .all()
    )
    return {row.position: row.cnt for row in rows}


def clear_captain_flags(fantasy_team_id):
    FantasyTeamPlayer.query.filter_by(fantasy_team_id=fantasy_team_id).update({
        'is_captain': False,
        'is_vice_captain': False
    })
    db.session.commit()


def set_captain(fantasy_team_id, captain_player_id, vice_captain_player_id):
    clear_captain_flags(fantasy_team_id)
    FantasyTeamPlayer.query.filter_by(
        fantasy_team_id=fantasy_team_id,
        player_id=captain_player_id
    ).update({'is_captain': True})
    FantasyTeamPlayer.query.filter_by(
        fantasy_team_id=fantasy_team_id,
        player_id=vice_captain_player_id
    ).update({'is_vice_captain': True})
    db.session.commit()


def update_player_role(fantasy_team_id, player_id, **kwargs):
    """Pass any of: is_starting, is_captain, is_vice_captain, bench_order."""
    allowed = {'is_starting', 'is_captain', 'is_vice_captain', 'bench_order'}
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if updates:
        FantasyTeamPlayer.query.filter_by(
            fantasy_team_id=fantasy_team_id,
            player_id=player_id
        ).update(updates)
        db.session.commit()


# ─────────────────────────────────────────────
#  GAMEWEEKS
# ─────────────────────────────────────────────

def get_active_gameweek():
    return Gameweek.query.filter_by(is_active=True).first()


def get_gameweek_by_id(gameweek_id):
    return Gameweek.query.get(gameweek_id)


def get_all_gameweeks():
    return Gameweek.query.order_by(Gameweek.number.asc()).all()


# ─────────────────────────────────────────────
#  FANTASY TEAM GAMEWEEK
# ─────────────────────────────────────────────

def get_team_gameweek_record(fantasy_team_id, gameweek_id):
    return FantasyTeamGameweek.query.filter_by(
        fantasy_team_id=fantasy_team_id,
        gameweek_id=gameweek_id
    ).first()


def upsert_team_gameweek_points(fantasy_team_id, gameweek_id, points):
    record = get_team_gameweek_record(fantasy_team_id, gameweek_id)
    if record:
        record.points = points
    else:
        record = FantasyTeamGameweek(
            fantasy_team_id=fantasy_team_id,
            gameweek_id=gameweek_id,
            points=points
        )
        db.session.add(record)
    db.session.commit()
    return record


def get_team_gameweek_history(fantasy_team_id):
    return (
        db.session.query(FantasyTeamGameweek, Gameweek)
        .join(Gameweek, FantasyTeamGameweek.gameweek_id == Gameweek.id)
        .filter(FantasyTeamGameweek.fantasy_team_id == fantasy_team_id)
        .order_by(Gameweek.number.asc())
        .all()
    )


# ─────────────────────────────────────────────
#  TRANSFERS
# ─────────────────────────────────────────────

def count_transfers_this_gameweek(fantasy_team_id, gameweek_id):
    return Transfer.query.filter_by(
        fantasy_team_id=fantasy_team_id,
        gameweek_id=gameweek_id
    ).count()


def record_transfer(fantasy_team_id, gameweek_id, player_out_id, player_in_id):
    transfer = Transfer(
        fantasy_team_id=fantasy_team_id,
        gameweek_id=gameweek_id,
        player_out_id=player_out_id,
        player_in_id=player_in_id
    )
    db.session.add(transfer)
    db.session.commit()
    return transfer


def get_transfers_this_gameweek(fantasy_team_id, gameweek_id):
    player_out = db.aliased(Player, name='player_out')
    player_in  = db.aliased(Player, name='player_in')
    return (
        db.session.query(Transfer, player_out, player_in)
        .join(player_out, Transfer.player_out_id == player_out.id)
        .join(player_in,  Transfer.player_in_id  == player_in.id)
        .filter(
            Transfer.fantasy_team_id == fantasy_team_id,
            Transfer.gameweek_id == gameweek_id
        )
        .order_by(Transfer.transferred_at.asc())
        .all()
    )


# ─────────────────────────────────────────────
#  LEADERBOARD
# ─────────────────────────────────────────────

def get_leaderboard(limit=50):
    from models.database import User
    return (
        db.session.query(FantasyTeam, User)
        .join(User, FantasyTeam.user_id == User.id)
        .order_by(FantasyTeam.total_points.desc(), FantasyTeam.gameweek_points.desc())
        .limit(limit)
        .all()
    )


def get_team_rank(fantasy_team_id):
    team = FantasyTeam.query.get(fantasy_team_id)
    if not team:
        return None
    rank = FantasyTeam.query.filter(
        FantasyTeam.total_points > team.total_points
    ).count()
    return rank + 1