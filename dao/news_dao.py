from models.database import db, News


def get_all_news(limit=20, offset=0):
    return (
        News.query
        .order_by(News.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


def get_news_count():
    return News.query.count()


def get_news_by_id(news_id):
    return db.session.get(News, news_id)


def get_recent_news(limit=3):
    return (
        News.query
        .order_by(News.created_at.desc())
        .limit(limit)
        .all()
    )


def get_news_by_category(category, limit=20):
    return (
        News.query
        .filter_by(category=category)
        .order_by(News.created_at.desc())
        .limit(limit)
        .all()
    )


def article_exists_by_url(source_url):
    return News.query.filter_by(source_url=source_url).first() is not None


def save_article(admin_id, title, content, excerpt=None, image_url=None,
                 source_url=None, scraped_at=None, category='Vijesti'):
    article = News(
        admin_id=admin_id,
        title=title,
        content=content,
        excerpt=excerpt,
        image_url=image_url,
        source_url=source_url,
        scraped_at=scraped_at,
        category=category,
    )
    db.session.add(article)
    db.session.commit()
    return article