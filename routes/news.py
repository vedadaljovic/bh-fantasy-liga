from flask import Blueprint, render_template

news_bp = Blueprint('news', __name__, url_prefix='/news')

@news_bp.route('/feed')
def feed():
    return render_template('news/feed.html')

@news_bp.route('/article/<int:article_id>')
def article(article_id):
    return render_template('news/article.html')
