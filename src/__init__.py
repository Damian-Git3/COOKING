from flask import Flask, render_template, url_for
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from configu.config import DevelopmentConfig
from configu.admin_config import setup_admin
from database.models import db, Usuario
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

    from routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from routes.cocina import cocina
    app.register_blueprint(cocina)

    from routes.dashboard.dashboard import dashboard as dashboard_blueprint
    app.register_blueprint(dashboard_blueprint)

    with app.app_context():
        db.create_all()

    setup_admin(app, db)

    def has_no_empty_params(rule):
        defaults = rule.defaults if rule.defaults is not None else ()
        arguments = rule.arguments if rule.arguments is not None else ()
        return len(defaults) >= len(arguments)

    @app.route("/site-map")
    def site_map():
        links = []
        for rule in app.url_map.iter_rules():
            # Filter out rules we can't navigate to in a browser
            # and rules that require parameters
            if "GET" in rule.methods and has_no_empty_params(rule):
                url = url_for(rule.endpoint, **(rule.defaults or {}))
                links.append((url, rule.endpoint))
        print(links)

    app.run(port=4000)
