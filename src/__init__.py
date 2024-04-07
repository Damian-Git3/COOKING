from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from config import DevelopmentConfig
from admin_config import setup_admin
from models import db, Usuario
from sassutils.wsgi import SassMiddleware

if __name__ == "__main__":
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    app.wsgi_app = SassMiddleware(app.wsgi_app, {
        '__main__': ('static/sass', 'static/css', '/static/css')
    })

    csrf = CSRFProtect()
    csrf.init_app(app)
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'
    login_manager.init_app(app)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.filter_by(id=int(user_id)).first()

    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    with app.app_context():
        db.create_all()

    setup_admin(app, db)

    app.run(port=4000)

