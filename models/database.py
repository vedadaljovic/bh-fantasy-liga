from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)  # 'user' or 'admin'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'


class Team(db.Model):
    __tablename__ = 'teams'
 
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10), nullable=False)
    logo_url   = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
 
    def __repr__(self):
        return f'<Team {self.short_name}>'
 
 
class Player(db.Model):
    __tablename__ = 'players'
 
    id           = db.Column(db.Integer, primary_key=True)
    team_id      = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    first_name   = db.Column(db.String(100), nullable=False)
    last_name    = db.Column(db.String(100), nullable=False)
    position     = db.Column(db.Enum('GK', 'DEF', 'MID', 'FWD'), nullable=False)
    price        = db.Column(db.Numeric(4, 1), nullable=False)
    total_points = db.Column(db.Integer, default=0)
    photo_url    = db.Column(db.String(255))
    is_available = db.Column(db.Boolean, default=True)
    created_at   = db.Column(db.DateTime, server_default=db.func.now())
 
    team = db.relationship('Team', backref='players')
 
    def __repr__(self):
        return f'<Player {self.first_name} {self.last_name}>'
 
 
class Gameweek(db.Model):
    __tablename__ = 'gameweeks'
 
    id          = db.Column(db.Integer, primary_key=True)
    number      = db.Column(db.Integer, nullable=False)
    name        = db.Column(db.String(50), nullable=False)
    deadline    = db.Column(db.DateTime, nullable=False)
    is_active   = db.Column(db.Boolean, default=False)
    is_finished = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, server_default=db.func.now())
 
    def __repr__(self):
        return f'<Gameweek {self.number}>'
 
 
class FantasyTeam(db.Model):
    __tablename__ = 'fantasy_teams'
 
    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    team_name        = db.Column(db.String(100), nullable=False)
    total_points     = db.Column(db.Integer, default=0)
    gameweek_points  = db.Column(db.Integer, default=0)
    budget_remaining = db.Column(db.Numeric(5, 1), default=100.0)
    formation        = db.Column(db.String(10), default='4-4-2')
    chip_used        = db.Column(db.String(20), default=None)  # 'triple_captain', 'bench_boost', 'wildcard'
    triple_captain_used = db.Column(db.Boolean, default=False)
    bench_boost_used    = db.Column(db.Boolean, default=False)
    wildcard_used       = db.Column(db.Boolean, default=False)
    created_at       = db.Column(db.DateTime, server_default=db.func.now())
 
    user = db.relationship('User', backref=db.backref('fantasy_team', uselist=False))
 
    def __repr__(self):
        return f'<FantasyTeam {self.team_name}>'
 
 
class FantasyTeamPlayer(db.Model):
    __tablename__ = 'fantasy_team_players'
 
    id               = db.Column(db.Integer, primary_key=True)
    fantasy_team_id  = db.Column(db.Integer, db.ForeignKey('fantasy_teams.id'), nullable=False)
    player_id        = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    is_starting      = db.Column(db.Boolean, default=True)
    is_captain       = db.Column(db.Boolean, default=False)
    is_vice_captain  = db.Column(db.Boolean, default=False)
    bench_order      = db.Column(db.Integer)
 
    fantasy_team = db.relationship('FantasyTeam', backref='squad')
    player       = db.relationship('Player')
 
    def __repr__(self):
        return f'<FantasyTeamPlayer ft={self.fantasy_team_id} p={self.player_id}>'
 
 
class FantasyTeamGameweek(db.Model):
    __tablename__ = 'fantasy_team_gameweek'
 
    id              = db.Column(db.Integer, primary_key=True)
    fantasy_team_id = db.Column(db.Integer, db.ForeignKey('fantasy_teams.id'), nullable=False)
    gameweek_id     = db.Column(db.Integer, db.ForeignKey('gameweeks.id'), nullable=False)
    points          = db.Column(db.Integer, default=0)
 
    fantasy_team = db.relationship('FantasyTeam', backref='gameweek_records')
    gameweek     = db.relationship('Gameweek')
 
    def __repr__(self):
        return f'<FantasyTeamGameweek ft={self.fantasy_team_id} gw={self.gameweek_id}>'
 
 
class Transfer(db.Model):
    __tablename__ = 'transfers'
 
    id              = db.Column(db.Integer, primary_key=True)
    fantasy_team_id = db.Column(db.Integer, db.ForeignKey('fantasy_teams.id'), nullable=False)
    gameweek_id     = db.Column(db.Integer, db.ForeignKey('gameweeks.id'), nullable=False)
    player_out_id   = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    player_in_id    = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    transferred_at  = db.Column(db.DateTime, server_default=db.func.now())
 
    fantasy_team = db.relationship('FantasyTeam', backref='transfers')
    gameweek     = db.relationship('Gameweek')
    player_out   = db.relationship('Player', foreign_keys=[player_out_id])
    player_in    = db.relationship('Player', foreign_keys=[player_in_id])
 
    def __repr__(self):
        return f'<Transfer out={self.player_out_id} in={self.player_in_id}>'

class PlayerGameweekStats(db.Model):
    __tablename__ = 'player_gameweek_stats'

    id             = db.Column(db.Integer, primary_key=True)
    player_id      = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    gameweek_id    = db.Column(db.Integer, db.ForeignKey('gameweeks.id'), nullable=False)
    fixture_id     = db.Column(db.Integer, nullable=False)
    minutes_played = db.Column(db.Integer, default=0)
    goals          = db.Column(db.Integer, default=0)
    assists        = db.Column(db.Integer, default=0)
    clean_sheet    = db.Column(db.Boolean, default=False)
    yellow_cards   = db.Column(db.Integer, default=0)
    red_cards      = db.Column(db.Integer, default=0)
    saves          = db.Column(db.Integer, default=0)
    bonus_points   = db.Column(db.Integer, default=0)
    points_scored  = db.Column(db.Integer, default=0)

    player   = db.relationship('Player', backref='gameweek_stats')
    gameweek = db.relationship('Gameweek')

    def __repr__(self):
        return f'<PlayerGameweekStats player={self.player_id} gw={self.gameweek_id}>'


class News(db.Model):
    __tablename__ = 'news'

    id          = db.Column(db.Integer, primary_key=True)
    admin_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title       = db.Column(db.String(255), nullable=False)
    content     = db.Column(db.Text, nullable=False)
    excerpt     = db.Column(db.Text)
    image_url   = db.Column(db.String(255))
    category    = db.Column(db.String(100), default='Vijesti')
    source_url  = db.Column(db.String(500))
    scraped_at  = db.Column(db.DateTime)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = db.relationship('User', backref='articles')

    def __repr__(self):
        return f'<News {self.title[:40]}>'


class Fixture(db.Model):
    __tablename__ = 'fixtures'

    id           = db.Column(db.Integer, primary_key=True)
    gameweek_id  = db.Column(db.Integer, db.ForeignKey('gameweeks.id'), nullable=False)
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    home_score   = db.Column(db.Integer, default=None)
    away_score   = db.Column(db.Integer, default=None)
    is_finished  = db.Column(db.Boolean, default=False)
    match_date   = db.Column(db.DateTime)

    gameweek  = db.relationship('Gameweek', backref='fixtures')
    home_team = db.relationship('Team', foreign_keys=[home_team_id])
    away_team = db.relationship('Team', foreign_keys=[away_team_id])

    def __repr__(self):
        return f'<Fixture gw={self.gameweek_id} {self.home_team_id}v{self.away_team_id}>'


class MatchEvent(db.Model):
    __tablename__ = 'match_events'

    id           = db.Column(db.Integer, primary_key=True)
    fixture_id   = db.Column(db.Integer, db.ForeignKey('fixtures.id'), nullable=False)
    minute       = db.Column(db.String(10))
    event_type   = db.Column(db.String(20), nullable=False)  #goal, yellow, red, sub
    player_name  = db.Column(db.String(100))
    player2_name = db.Column(db.String(100))  #assist or subbed in player
    team_side    = db.Column(db.String(10))   #home or away
    score_home   = db.Column(db.Integer)
    score_away   = db.Column(db.Integer)

    fixture = db.relationship('Fixture', backref='events')

    def __repr__(self):
        return f'<MatchEvent {self.event_type} {self.minute}>'


class MatchLineup(db.Model):
    __tablename__ = 'match_lineups'

    id            = db.Column(db.Integer, primary_key=True)
    fixture_id    = db.Column(db.Integer, db.ForeignKey('fixtures.id'), nullable=False)
    team_side     = db.Column(db.String(10), nullable=False)
    player_name   = db.Column(db.String(100), nullable=False)
    shirt_number  = db.Column(db.String(10))
    is_starting   = db.Column(db.Boolean, default=True)
    is_goalkeeper = db.Column(db.Boolean, default=False)
    is_captain    = db.Column(db.Boolean, default=False)

    fixture = db.relationship('Fixture', backref='lineups')

    def __repr__(self):
        return f'<MatchLineup {self.player_name} ({self.team_side})>'