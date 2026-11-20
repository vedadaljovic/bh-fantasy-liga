import sys
import os
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models.database import db

SCHEDULE_URL = 'https://sportsport.ba/raspored/fudbal/bosna-i-hercegovina/wwin-liga-bih/1'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36',
}

TEAM_MAP = {
    'FK Borac':         1,
    'NK Čelik':         2,
    'FK Radnik B.':     3,
    'FK BSK':           4,
    'FK Sarajevo':      5,
    'FK Sloga':         6,
    'NK Široki B.':     7,
    'FK Velež':         8,
    'HŠK Zrinjski':     9,
    'FK Željezničar':   10,
}


def resolve_team(name):
    name = name.strip()
    for key, tid in TEAM_MAP.items():
        if key in name or name in key:
            return tid
    print(f'[WARN] Unknown team: {name}')
    return None


def parse_date(date_str, time_str):
    try:
        date_str = date_str.strip().rstrip('.')
        dt = datetime.strptime(f'{date_str} {time_str.strip()}', '%d.%m.%y %H:%M')
        return dt
    except Exception as e:
        print(f'[WARN] Could not parse date {date_str} {time_str}: {e}')
        return None


def parse_score(score_str):
    score_str = score_str.strip()
    if '-' in score_str or not score_str:
        return None, None
    m = re.search(r'(\d+)\s*:\s*(\d+)', score_str)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None


def scrape_schedule():
    resp = requests.get(SCHEDULE_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    rounds = []
    current_round = None

    for el in soup.find_all(['h2', 'table']):
        if el.name == 'h2':
            text = el.get_text(strip=True)
            m = re.match(r'(\d+)\.\s*kolo', text)
            if m:
                current_round = int(m.group(1))
                rounds.append({'number': current_round, 'fixtures': []})

        elif el.name == 'table' and rounds:
            for row in el.find_all('tr'):
                cols = row.find_all('td')
                if len(cols) < 6:
                    continue

                date_str  = cols[0].get_text(strip=True)
                time_str  = cols[1].get_text(strip=True)
                home_name = cols[2].get_text(strip=True)
                away_name = cols[4].get_text(strip=True)
                score_raw = cols[5].get_text(strip=True)

                match_dt = parse_date(date_str, time_str)
                home_id  = resolve_team(home_name)
                away_id  = resolve_team(away_name)

                if not home_id or not away_id or not match_dt:
                    continue

                home_score, away_score = parse_score(score_raw)
                is_finished = home_score is not None

                rounds[-1]['fixtures'].append({
                    'match_date':   match_dt,
                    'home_team_id': home_id,
                    'away_team_id': away_id,
                    'home_score':   home_score,
                    'away_score':   away_score,
                    'is_finished':  is_finished,
                })

    return rounds


def save_to_db(rounds):
    from models.database import Gameweek, Fixture

    for r in rounds:
        if not r['fixtures']:
            continue

        number   = r['number']
        fixtures = r['fixtures']

        dates       = [f['match_date'] for f in fixtures if f['match_date']]
        earliest    = min(dates) if dates else None
        latest      = max(dates) if dates else None
        deadline    = earliest - timedelta(minutes=30) if earliest else None
        is_finished = all(f['is_finished'] for f in fixtures)

        now = datetime.now()
        is_active = (
            earliest is not None and
            latest is not None and
            earliest <= now <= latest + timedelta(hours=3)
        )

        gw = Gameweek.query.filter_by(number=number).first()
        if gw:
            gw.deadline    = deadline
            gw.is_finished = is_finished
            if is_active:
                Gameweek.query.update({'is_active': False})
                gw.is_active = True
            print(f'[UPDATE] Gameweek {number}')
        else:
            if is_active:
                Gameweek.query.update({'is_active': False})
            gw = Gameweek(
                number=number,
                name=f'Kolo {number}',
                deadline=deadline or datetime.now(),
                is_active=is_active,
                is_finished=is_finished,
            )
            db.session.add(gw)
            db.session.flush()  # get gw.id
            print(f'[CREATE] Gameweek {number}')

        db.session.commit()

        for f in fixtures:
            existing = Fixture.query.filter_by(
                gameweek_id=gw.id,
                home_team_id=f['home_team_id'],
                away_team_id=f['away_team_id'],
            ).first()

            if existing:
                existing.match_date  = f['match_date']
                existing.home_score  = f['home_score']
                existing.away_score  = f['away_score']
                existing.is_finished = f['is_finished']
            else:
                fixture = Fixture(
                    gameweek_id=gw.id,
                    home_team_id=f['home_team_id'],
                    away_team_id=f['away_team_id'],
                    match_date=f['match_date'],
                    home_score=f['home_score'],
                    away_score=f['away_score'],
                    is_finished=f['is_finished'],
                )
                db.session.add(fixture)

        db.session.commit()
        print(f'  -> {len(fixtures)} fixtures saved for round {number}')


def run():
    print(f'[START] Fixtures scraper — {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    print(f'[INFO] Fetching schedule from sportsport.ba...')

    rounds = scrape_schedule()
    print(f'[INFO] Found {len(rounds)} rounds')

    if not rounds:
        print('[WARN] No rounds found.')
        return

    save_to_db(rounds)
    print(f'\n[DONE] All rounds processed.')


if __name__ == '__main__':
    with app.app_context():
        run()