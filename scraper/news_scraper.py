import sys
import os
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models.database import db

SCRAPER_USER_ID = 12
BASE_URL        = 'https://sportsport.ba'
LISTING_URL     = 'https://sportsport.ba/fudbal/bosna-i-hercegovina/wwin-liga-bih'
HEADERS         = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'bs,hr;q=0.9',
}
MAX_ARTICLES  = 20
DELAY_SECONDS = 1.5

SKIP_PHRASES = [
    'NAPOMENA:', 'Komentari odražavaju', 'Copyright 2008',
    'Sva prava zadržana', 'Zabranjeno preuzimanje',
    'Pravila o zaštiti', 'SportSport d.o.o', 'ISSN 2744',
    'Niko nije obratio pažnju',
]


def get_soup(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, 'html.parser')
    except Exception as e:
        print(f'[ERROR] Could not fetch {url}: {e}')
        return None


def already_exists(source_url):
    from models.database import News
    return db.session.query(News).filter_by(source_url=source_url).first() is not None


def scrape_listing():
    soup = get_soup(LISTING_URL)
    if not soup:
        return []

    urls = []
    pattern = re.compile(r'https://sportsport\.ba/fudbal/[^/]+/\d+$')

    for a in soup.find_all('a', href=True):
        href = a['href']
        if pattern.match(href) and href not in urls:
            urls.append(href)

    print(f'[INFO] Found {len(urls)} article links')
    return urls[:MAX_ARTICLES]


def scrape_article(url):
    soup = get_soup(url)
    if not soup:
        return None

    try:
        title_el = soup.find('h1')
        title = title_el.get_text(strip=True) if title_el else None
        if not title:
            return None

        image_url = None
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            image_url = og_image['content']

        all_paragraphs = soup.find_all('p')
        content_parts = []
        for p in all_paragraphs:
            text = p.get_text(strip=True)
            if len(text) < 40:
                continue
            if any(phrase in text for phrase in SKIP_PHRASES):
                continue
            content_parts.append(text)

        content = '\n\n'.join(content_parts)
        if not content:
            return None

        excerpt = content[:200].rsplit(' ', 1)[0] + '...' if len(content) > 200 else content

        published_at = None
        pub_meta = soup.find('meta', property='article:published_time')
        if pub_meta and pub_meta.get('content'):
            try:
                published_at = datetime.fromisoformat(pub_meta['content'].replace('Z', '+00:00'))
            except Exception:
                published_at = datetime.utcnow()
        else:
            published_at = datetime.utcnow()

        return {
            'title':        title,
            'content':      content,
            'excerpt':      excerpt,
            'image_url':    image_url,
            'published_at': published_at,
        }

    except Exception as e:
        print(f'[ERROR] Failed to parse {url}: {e}')
        return None


def save_article(data, source_url):
    from models.database import News
    article = News(
        admin_id=SCRAPER_USER_ID,
        title=data['title'],
        content=data['content'],
        excerpt=data['excerpt'],
        image_url=data['image_url'],
        source_url=source_url,
        scraped_at=datetime.utcnow(),
        category='Vijesti',
        created_at=data['published_at'],
    )
    db.session.add(article)
    db.session.commit()
    print(f'[SAVED] {data["title"][:70]}')


def run():
    print(f'[START] News scraper — {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    urls = scrape_listing()

    if not urls:
        print('[WARN] No article URLs found.')
        return

    saved = skipped = 0

    for url in urls:
        if already_exists(url):
            print(f'[SKIP] Already in DB: {url}')
            skipped += 1
            continue

        print(f'[FETCH] {url}')
        data = scrape_article(url)

        if not data:
            print(f'[SKIP] Could not parse: {url}')
            continue

        save_article(data, url)
        saved += 1
        time.sleep(DELAY_SECONDS)

    print(f'\n[DONE] Saved: {saved} | Skipped: {skipped}')


if __name__ == '__main__':
    with app.app_context():
        run()