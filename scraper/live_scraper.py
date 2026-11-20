"""
Live match scraper using Playwright + Flashscore.
Scrapes scores, events, lineups and stats for WWin Liga BiH matches.
"""

import sys
import os
import re
import time
import unicodedata
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models.database import db

LEAGUE_URL = 'https://www.flashscore.com/football/bosnia-and-herzegovina/wwin-liga-bih/'
POLL_INTERVAL = 60 
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36'
}

TEAM_MAP = {
    'Borac Banja Luka': 1,
    'Celik Zenica':     2,
    'Čelik Zenica':     2,
    'NK Čelik Zenica':  2,
    'Radnik Bijeljina': 3,
    'BSK Banja Luka':   4,
    'FK BSK Banja Luka':4,
    'FK Sarajevo':      5,
    'Sloga Meridian':   6,
    'FK Sloga':         6,
    'Siroki Brijeg':    7,
    'Velez Mostar':     8,
    'FK Velež':         8,
    'Zrinjski':         9,
    'Zeljeznicar':      10,
    'FK Željezničar':   10,
}


FLASHSCORE_SLUG = {
    1:  'borac',
    2:  'celik',
    3:  'radnik',
    4:  'bsk',
    5:  'sarajevo',
    6:  'sloga',
    7:  'siroki',
    8:  'velez',
    9:  'zrinjski',
    10: 'zeljeznicar',
}


def strip_diacritics(s):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', s)
        if not unicodedata.combining(c)
    ).replace('đ', 'dj').replace('Đ', 'Dj')


def resolve_team(name):
    name = name.strip()
    for key, tid in TEAM_MAP.items():
        if key.lower() in name.lower() or name.lower() in key.lower():
            return tid
    return None


def get_active_fixtures():
    from models.database import Fixture, Gameweek
    gw = Gameweek.query.filter_by(is_active=True).first()
    if not gw:
        gw = Gameweek.query.filter_by(is_finished=False).order_by(Gameweek.number.asc()).first()
    if not gw:
        return []

    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0)
    today_end   = now.replace(hour=23, minute=59, second=59)

    return Fixture.query.filter(
        Fixture.gameweek_id == gw.id,
        Fixture.match_date >= today_start,
        Fixture.match_date <= today_end,
    ).all()


def find_flashscore_match_url(page, home_team_id, away_team_id):
    """Find the Flashscore match URL for a given fixture."""
    page.goto(LEAGUE_URL)
    page.wait_for_timeout(3000)

    links = page.eval_on_selector_all(
        'a[href*="/match/"]',
        'els => els.map(e => ({href: e.href, text: e.innerText}))'
    )

    home_slug = FLASHSCORE_SLUG.get(home_team_id)
    away_slug = FLASHSCORE_SLUG.get(away_team_id)
    if not home_slug or not away_slug:
        print(f'[WARN] No Flashscore slug for team {home_team_id} or {away_team_id}')
        return None

    for link in links:
        href = link.get('href', '')
        if '/match/' not in href:
            continue
        href_lower = strip_diacritics(href.lower())
        tokens = set(re.split(r'[^a-z0-9]+', href_lower))
        if home_slug in tokens and away_slug in tokens:
            return href.split('?')[0]

    return None


def scrape_match(page, url, fixture_id):
    page.goto(url)
    page.wait_for_timeout(4000)

    text = page.evaluate('() => document.body.innerText')
    result = {
        'fixture_id': fixture_id,
        'home_score': None,
        'away_score': None,
        'status':     'unknown',
        'minute':     None,
        'is_finished': False,
        'events':     [],
        'lineups':    {'home': [], 'away': []},
        'stats':      {},
    }

    score_match = re.search(
        r'(\w[\w\s]+)\n(\d+)\n-\n(\d+)\n(2ND HALF|1ST HALF|FINISHED|FT|HT)',
        text
    )
    if score_match:
        result['home_score'] = int(score_match.group(2))
        result['away_score'] = int(score_match.group(3))
        status = score_match.group(4)
        result['status'] = status
        result['is_finished'] = status in ('FINISHED', 'FT')


    minute_match = re.search(r"(1ST HALF|2ND HALF)\s*(\d+):\d+", text)
    if minute_match:
        result['minute'] = minute_match.group(2) + "'"


    lines = text.split('\n')
    i = 0
    current_home = 0
    current_away = 0

    while i < len(lines):
        line = lines[i].strip()

        minute_m = re.match(r"^(\d+(?:\+\d+)?)'$", line)
        if minute_m and i + 1 < len(lines):
            minute = line
            next_line = lines[i + 1].strip()

            score_m = re.match(r'^(\d+)\s*-\s*(\d+)$', next_line)
            if score_m and i + 2 < len(lines):
                h, a = int(score_m.group(1)), int(score_m.group(2))
                scorer = lines[i + 2].strip()
                if h > current_home:
                    team_side = 'home'
                elif a > current_away:
                    team_side = 'away'
                else:
                    team_side = 'unknown'
                current_home, current_away = h, a

                result['events'].append({
                    'minute':     minute,
                    'event_type': 'goal',
                    'player':     scorer,
                    'player2':    None,
                    'team_side':  team_side,
                    'score_home': h,
                    'score_away': a,
                })
                i += 3
                continue

        i += 1

    try:
        page.get_by_text('LINEUPS').first.click()
        page.wait_for_timeout(2000)
        text_with_lineups = page.evaluate('() => document.body.innerText')
    except:
        text_with_lineups = text

    if 'STARTING LINEUPS' in text_with_lineups:
        result['lineups'] = parse_lineups(text_with_lineups)

    try:
        page.get_by_text('STATS').first.click()
        page.wait_for_timeout(2000)
        stats_text = page.evaluate('() => document.body.innerText')
        result['stats'] = parse_stats(stats_text)
    except:
        pass

    return result


def parse_lineups(text):
    lineups = {'home': [], 'away': []}

    if 'STARTING LINEUPS' not in text:
        return lineups

    idx = text.index('STARTING LINEUPS')
    section = text[idx:]

    lines = [l.strip() for l in section.split('\n') if l.strip()]

    sub_idx = None
    for j, l in enumerate(lines):
        if 'SUBSTITUTES' in l:
            sub_idx = j
            break

    starting_lines = lines[1:sub_idx] if sub_idx else lines[1:23]

    players = []
    i = 0
    while i < len(starting_lines):
        line = starting_lines[i]
        num_m = re.match(r'^(\d+)$', line)
        if num_m and i + 1 < len(starting_lines):
            number = line
            name   = starting_lines[i + 1]
            is_gk  = '(G)' in name
            is_cap = '(C)' in name
            name   = name.replace('(G)', '').replace('(C)', '').strip()
            players.append({
                'number': number,
                'name':   name,
                'is_gk':  is_gk,
                'is_cap': is_cap,
            })
            i += 2
        else:
            i += 1

    mid = len(players) // 2
    for p in players[:mid]:
        lineups['home'].append(p)
    for p in players[mid:]:
        lineups['away'].append(p)

    return lineups


def parse_stats(text):
    stats = {}
    patterns = [
        ('possession', r'(\d+)%\s*Ball possession\s*(\d+)%'),
        ('shots_total', r'(\d+)\s*Total shots\s*(\d+)'),
        ('shots_on_target', r'(\d+)\s*Shots on target\s*(\d+)'),
        ('corners', r'(\d+)\s*Corner kicks\s*(\d+)'),
        ('fouls', r'(\d+)\s*Fouls\s*(\d+)'),
        ('yellow_cards', r'(\d+)\s*Yellow cards\s*(\d+)'),
        ('red_cards', r'(\d+)\s*Red cards\s*(\d+)'),
    ]
    for key, pattern in patterns:
        m = re.search(pattern, text)
        if m:
            stats[key] = {'home': m.group(1), 'away': m.group(2)}
    return stats


def save_match_data(data):
    from models.database import Fixture, MatchEvent, MatchLineup

    fixture = Fixture.query.get(data['fixture_id'])
    if not fixture:
        return

    if data['home_score'] is not None:
        fixture.home_score  = data['home_score']
        fixture.away_score  = data['away_score']
        fixture.is_finished = data['is_finished']
        db.session.commit()

    MatchEvent.query.filter_by(fixture_id=fixture.id).delete()
    for ev in data['events']:
        db.session.add(MatchEvent(
            fixture_id=fixture.id,
            minute=ev['minute'],
            event_type=ev['event_type'],
            player_name=ev['player'],
            player2_name=ev.get('player2'),
            team_side=ev['team_side'],
            score_home=ev.get('score_home'),
            score_away=ev.get('score_away'),
        ))

    existing_lineups = MatchLineup.query.filter_by(fixture_id=fixture.id).count()
    if existing_lineups == 0:
        for side in ('home', 'away'):
            for p in data['lineups'].get(side, []):
                db.session.add(MatchLineup(
                    fixture_id=fixture.id,
                    team_side=side,
                    player_name=p['name'],
                    shirt_number=p.get('number'),
                    is_starting=True,
                    is_goalkeeper=p.get('is_gk', False),
                    is_captain=p.get('is_cap', False),
                ))

    db.session.commit()
    print(f'[SAVED] Fixture {fixture.id}: {fixture.home_score}-{fixture.away_score} '
          f'| {len(data["events"])} events')


def run():
    from playwright.sync_api import sync_playwright

    print(f'[START] Live scraper — {datetime.now().strftime("%Y-%m-%d %H:%M")}')

    with app.app_context():
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page    = browser.new_page()
            page.set_extra_http_headers({'User-Agent': HEADERS['User-Agent']})

            while True:
                fixtures = get_active_fixtures()

                if not fixtures:
                    print('[INFO] No fixtures today. Exiting.')
                    break

                all_finished = all(f.is_finished for f in fixtures)
                if all_finished:
                    print('[INFO] All matches finished. Exiting.')
                    break

                print(f'\n[POLL] {datetime.now().strftime("%H:%M:%S")} '
                      f'— {len(fixtures)} fixtures')

                for fixture in fixtures:
                    if fixture.is_finished:
                        continue

                    url = find_flashscore_match_url(
                        page, fixture.home_team_id, fixture.away_team_id
                    )

                    if not url:
                        print(f'[SKIP] Could not find URL for fixture {fixture.id}')
                        continue

                    print(f'[FETCH] {url}')
                    try:
                        data = scrape_match(page, url, fixture.id)
                        save_match_data(data)
                    except Exception as e:
                        print(f'[ERROR] Fixture {fixture.id}: {e}')

                print(f'[WAIT] Next poll in {POLL_INTERVAL}s...')
                time.sleep(POLL_INTERVAL)

            browser.close()

    print('[DONE] Live scraper finished.')


if __name__ == '__main__':
    run()