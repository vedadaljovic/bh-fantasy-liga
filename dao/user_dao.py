from models.database import db, User


def get_user_by_id(user_id):
    return User.query.get(user_id)


def update_team_name(fantasy_team, new_name):
    fantasy_team.team_name = new_name
    db.session.commit()


def update_password(user, new_password_hash):
    user.password_hash = new_password_hash
    db.session.commit()


def delete_user(user_id):
    from models.database import FantasyTeam, FantasyTeamPlayer, Transfer, FantasyTeamGameweek
    # Delete in dependency order
    ft = FantasyTeam.query.filter_by(user_id=user_id).first()
    if ft:
        FantasyTeamPlayer.query.filter_by(fantasy_team_id=ft.id).delete()
        Transfer.query.filter_by(fantasy_team_id=ft.id).delete()
        FantasyTeamGameweek.query.filter_by(fantasy_team_id=ft.id).delete()
        db.session.delete(ft)
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
    db.session.commit()