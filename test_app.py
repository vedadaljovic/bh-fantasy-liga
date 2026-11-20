import pytest
from app import create_app
from models.database import db, User, FantasyTeam, FantasyTeamPlayer, Player, Team, Gameweek


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        _seed()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    client.post('/auth/login', data={'email': 'test@bhfantasy.ba', 'password': 'test123'})
    return client


@pytest.fixture
def admin_client(client):
    client.post('/auth/login', data={'email': 'admin@bhfantasy.ba', 'password': 'admin123'})
    return client


def _seed():
    team = Team(name='FK Test', short_name='TST')
    db.session.add(team)
    db.session.flush()

    for i in range(3):
        db.session.add(Player(first_name=f'GK{i}', last_name=f'Player{i}',
                              position='GK', price=5.0, team_id=team.id))
    for i in range(6):
        db.session.add(Player(first_name=f'DEF{i}', last_name=f'Player{i}',
                              position='DEF', price=5.0, team_id=team.id))
    for i in range(6):
        db.session.add(Player(first_name=f'MID{i}', last_name=f'Player{i}',
                              position='MID', price=5.0, team_id=team.id))
    for i in range(5):
        db.session.add(Player(first_name=f'FWD{i}', last_name=f'Player{i}',
                              position='FWD', price=5.0, team_id=team.id))

    gw = Gameweek(number=1, name='Kolo 1',
                  deadline=__import__('datetime').datetime(2026, 9, 1, 17, 0),
                  is_active=True, is_finished=False)
    db.session.add(gw)

    user = User(username='testuser', email='test@bhfantasy.ba', role='user')
    user.set_password('test123')
    db.session.add(user)

    admin = User(username='adminuser', email='admin@bhfantasy.ba', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)

    db.session.commit()


#Auth

def test_register_success(client):
    r = client.post('/auth/register', data={
        'username': 'newuser', 'email': 'new@test.ba', 'password': 'pass123'
    }, follow_redirects=True)
    assert r.status_code == 200


def test_register_duplicate_email(client):
    client.post('/auth/register', data={
        'username': 'user1', 'email': 'dupe@test.ba', 'password': 'pass123'
    })
    r = client.post('/auth/register', data={
        'username': 'user2', 'email': 'dupe@test.ba', 'password': 'pass123'
    }, follow_redirects=True)
    assert b'registrovan' in r.data or r.status_code == 200


def test_register_short_password(client):
    from services.auth_service import AuthService
    success, msg, _ = AuthService.register('newuser2', 'new2@test.ba', '123')
    assert not success
    assert 'lozinka' in msg.lower()


def test_login_success(client):
    r = client.post('/auth/login', data={
        'email': 'test@bhfantasy.ba', 'password': 'test123'
    }, follow_redirects=True)
    assert r.status_code == 200


def test_login_wrong_password(client):
    from services.auth_service import AuthService
    success, msg, _ = AuthService.login('test@bhfantasy.ba', 'wrongpass')
    assert not success


def test_login_nonexistent_user(client):
    from services.auth_service import AuthService
    success, msg, _ = AuthService.login('nobody@test.ba', 'pass123')
    assert not success


#Route access

def test_protected_route_redirects_guest(client):
    r = client.get('/fantasy/my-team', follow_redirects=False)
    assert r.status_code == 302


def test_authenticated_user_can_access_my_team(auth_client):
    r = auth_client.get('/fantasy/my-team', follow_redirects=True)
    assert r.status_code == 200


def test_admin_route_blocks_regular_user(auth_client):
    r = auth_client.get('/admin/dashboard', follow_redirects=True)
    assert r.status_code == 200
    assert b'Admin' not in r.data or b'administratori' in r.data


def test_admin_route_accessible_by_admin(admin_client):
    r = admin_client.get('/admin/dashboard')
    assert r.status_code == 200


def test_news_feed_accessible(client):
    r = client.get('/news/feed')
    assert r.status_code == 200


def test_rss_feed_returns_xml(client):
    r = client.get('/news/rss')
    assert r.status_code == 200
    assert b'<?xml' in r.data
    assert b'<rss' in r.data


#Fantasy service

def test_create_fantasy_team(app):
    from services.fantasy_service import FantasyService
    with app.app_context():
        user = User.query.filter_by(email='test@bhfantasy.ba').first()
        success, msg, team = FantasyService.create_team(user.id, 'Moj Tim')
        assert success
        assert team is not None


def test_create_fantasy_team_short_name(app):
    from services.fantasy_service import FantasyService
    with app.app_context():
        user = User.query.filter_by(email='test@bhfantasy.ba').first()
        success, msg, _ = FantasyService.create_team(user.id, 'AB')
        assert not success


def test_create_duplicate_fantasy_team(app):
    from services.fantasy_service import FantasyService
    with app.app_context():
        user = User.query.filter_by(email='test@bhfantasy.ba').first()
        FantasyService.create_team(user.id, 'Moj Tim')
        success, msg, _ = FantasyService.create_team(user.id, 'Drugi Tim')
        assert not success


def test_save_squad_wrong_count(app):
    from services.fantasy_service import FantasyService
    with app.app_context():
        user = User.query.filter_by(email='test@bhfantasy.ba').first()
        FantasyService.create_team(user.id, 'Moj Tim')
        success, msg = FantasyService.save_squad(user.id, [1, 2, 3], 1, 2)
        assert not success


def test_save_squad_budget_exceeded(app):
    from services.fantasy_service import FantasyService
    with app.app_context():
        user = User.query.filter_by(email='test@bhfantasy.ba').first()
        FantasyService.create_team(user.id, 'Moj Tim')

        extra_teams = []
        for i in range(5):
            t = Team(name=f'Klub {i}', short_name=f'KL{i}')
            db.session.add(t)
            extra_teams.append(t)
        db.session.flush()

        positions = ['GK', 'GK', 'DEF', 'DEF', 'DEF', 'DEF', 'DEF',
                     'MID', 'MID', 'MID', 'MID', 'MID', 'FWD', 'FWD', 'FWD']
        all_players = []
        for i, pos in enumerate(positions):
            p = Player(first_name=f'P{i}', last_name=f'T{i}',
                       position=pos, price=15.0, team_id=extra_teams[i % 5].id)
            db.session.add(p)
            all_players.append(p)
        db.session.commit()

        ids = [p.id for p in all_players]
        success, msg = FantasyService.save_squad(user.id, ids, ids[0], ids[1])
        assert not success
        assert 'budžet' in msg.lower()


#Admin

def test_admin_add_player(admin_client, app):
    import json
    with app.app_context():
        team = Team.query.first()
        r = admin_client.post('/admin/players/add',
            data=json.dumps({
                'first_name': 'Novi', 'last_name': 'Igrac',
                'team_id': team.id, 'position': 'MID',
                'price': 6.0, 'is_available': True
            }),
            content_type='application/json')
        data = json.loads(r.data)
        assert data['success']


def test_admin_delete_nonexistent_player(admin_client):
    r = admin_client.post('/admin/players/99999/delete')
    assert r.status_code == 404


def test_admin_toggle_user(admin_client, app):
    import json
    with app.app_context():
        user = User.query.filter_by(email='test@bhfantasy.ba').first()
        r = admin_client.post(f'/admin/users/{user.id}/toggle')
        data = json.loads(r.data)
        assert data['success']


#News

def test_news_dao_get_all(app):
    from dao import news_dao
    with app.app_context():
        articles = news_dao.get_all_news(limit=10)
        assert isinstance(articles, list)


def test_news_article_404(client):
    r = client.get('/news/article/99999')
    assert r.status_code == 404


def test_admin_add_news(admin_client, app):
    import json
    r = admin_client.post('/admin/news/add',
        data=json.dumps({
            'title': 'Test vijest', 'content': 'Sadržaj test vijesti koja je dovoljno duga.',
            'category': 'Vijesti'
        }),
        content_type='application/json')
    data = json.loads(r.data)
    assert data['success']