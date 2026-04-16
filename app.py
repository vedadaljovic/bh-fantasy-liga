import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from config import config
from models.database import db, User

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static',
                static_url_path='/static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Molimo prijavite se.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.news import news_bp
    from routes.fantasy import fantasy_bp
    from routes.admin import admin_bp
    from routes.user import user_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(fantasy_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    
    @app.route('/')
    def index():
        return redirect(url_for('news.feed'))
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
