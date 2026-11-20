from flask import Blueprint, render_template, request, abort, Response
from services.news_service import NewsService
from datetime import timezone

news_bp = Blueprint('news', __name__, url_prefix='/news')


@news_bp.route('/feed')
def feed():
    page = request.args.get('page', 1, type=int)
    data = NewsService.get_feed(page=page, per_page=12)
    return render_template('news/feed.html', **data)


@news_bp.route('/article/<int:article_id>')
def article(article_id):
    article, related = NewsService.get_article(article_id)
    if not article:
        abort(404)
    return render_template('news/article.html', article=article, related=related)


@news_bp.route('/rss')
def rss():
    from dao import news_dao
    from flask import url_for
    articles = news_dao.get_all_news(limit=20)

    def pub_date(dt):
        if not dt:
            return ''
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.strftime('%a, %d %b %Y %H:%M:%S %z')

    items = ''
    for a in articles:
        link    = url_for('news.article', article_id=a.id, _external=True)
        excerpt = (a.excerpt or a.content[:200]).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        title   = a.title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        items  += f"""
        <item>
            <title>{title}</title>
            <link>{link}</link>
            <description>{excerpt}</description>
            <pubDate>{pub_date(a.created_at)}</pubDate>
            <guid>{link}</guid>
            <category>{a.category or 'Vijesti'}</category>
        </item>"""

    base_url = url_for('news.feed', _external=True)
    rss_xml  = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <title>BH Fantasy Liga — Vijesti</title>
        <link>{base_url}</link>
        <description>Najnovije vijesti iz WWin Lige Bosne i Hercegovine</description>
        <language>bs</language>
        <atom:link href="{url_for('news.rss', _external=True)}" rel="self" type="application/rss+xml"/>
        {items}
    </channel>
</rss>"""

    return Response(rss_xml, mimetype='application/rss+xml')