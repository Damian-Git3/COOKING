from flask import Flask, render_template, url_for
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from configu.config import DevelopmentConfig
from database.models import db, Usuario
from sassutils.wsgi import SassMiddleware
from configu.admin_config import setup_admin


if __name__ == "__main__":
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    CORS(app, resources={r"/*": {"origins": "http://localhost:*"}})

    app.wsgi_app = SassMiddleware(
        app.wsgi_app,
        {
            "__main__": {
                "sass_path": "static/sass",
                "css_path": "static/css",
                "wsgi_path": "/static/css",
                "strip_extension": False,
            }
        },
    )

    csrf = CSRFProtect()
    csrf.init_app(app)
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Por favor inicie sesión para acceder a esta página."
    login_manager.init_app(app)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return (
            render_template(
                "error_page.html",
                error="500",
                mensaje="Error del servidor porfavor intentelo más tarde",
            ),
            500,
        )

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("error_page.html", error="403", mensaje="Prohibido"), 403

    @app.errorhandler(401)
    def unauthorized(e):
        return (
            render_template("error_page.html", error="401", mensaje="No autorizado"),
            401,
        )

    @app.errorhandler(400)
    def bad_request(e):
        return (
            render_template(
                "error_page.html", error="400", mensaje="Petición incorrecta"
            ),
            400,
        )

    @app.errorhandler(405)
    def method_not_allowed(e):
        return (
            render_template(
                "error_page.html", error="405", mensaje="Método no autorizado"
            ),
            405,
        )

    @app.errorhandler(AttributeError)
    def attribute_error(e):
        return render_template(
            "error_page.html", error="500", mensaje="Error en la carga de los atributos"
        )

    @app.errorhandler(ZeroDivisionError)
    def zero_division_error(e):
        return render_template(
            "error_page.html", error="500", mensaje="Se generó una división entre cero"
        )

    @app.errorhandler(ImportError)
    def import_error(e):
        return render_template(
            "error_page.html", error="500", mensaje="Error de importación"
        )

    @app.errorhandler(NotImplementedError)
    def not_implemented_error(e):
        return render_template(
            "error_page.html", error="500", mensaje="Error de implementación"
        )

    @app.errorhandler(Exception)
    def exception_error(e):
        return (
            render_template("error_page.html", error="500", mensaje="Error inesperado"),
            500,
        )

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.filter_by(id=int(user_id)).first()

    from routes.auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    from routes.main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from routes.cocina import cocina

    app.register_blueprint(cocina)

    from routes.dashboard import dashboard as dashboard_blueprint

    app.register_blueprint(dashboard_blueprint)

    from routes.venta import venta

    app.register_blueprint(venta)

    setup_admin(app, db)

    def has_no_empty_params(rule):
        defaults = rule.defaults if rule.defaults is not None else ()
        arguments = rule.arguments if rule.arguments is not None else ()
        return len(defaults) >= len(arguments)

    @app.route("/site-map")
    def site_map():
        links = []
        for rule in app.url_map.iter_rules():
            links.append(rule)
            print(rule)

        return str(links)

    app.run(port=4000)
