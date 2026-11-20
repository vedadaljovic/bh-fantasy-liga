from models.database import Team

def get_all_teams():
    return Team.query.order_by(Team.name.asc()).all()