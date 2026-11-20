from dao import news_dao


class NewsService:

    @staticmethod
    def get_feed(page=1, per_page=12):
        offset = (page - 1) * per_page
        articles = news_dao.get_all_news(limit=per_page, offset=offset)
        total    = news_dao.get_news_count()
        has_more = (offset + per_page) < total
        return {
            'articles': articles,
            'total':    total,
            'page':     page,
            'has_more': has_more,
        }

    @staticmethod
    def get_article(news_id):
        article = news_dao.get_news_by_id(news_id)
        if not article:
            return None, None
        related = news_dao.get_recent_news(limit=4)
        related = [a for a in related if a.id != news_id][:3]
        return article, related