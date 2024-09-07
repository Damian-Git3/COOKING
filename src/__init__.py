""" Archivo principal de la aplicación, aquí se inicializan las configuraciones de la aplicación y se registran las rutas y los manejadores de errores. """

import wtforms
from flask import Flask, render_template
from flask_cors import CORS
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from pymysql import IntegrityError
from sassutils.wsgi import SassMiddleware
from sqlalchemy.exc import SQLAlchemyError

from flask_socketio import SocketIO, send

from configu.admin_config import setup_admin
from configu.config import DevelopmentConfig
from database.models import Usuario, db
from error_handler import (
    attribute_error,
    bad_request,
    exception_error,
    forbidden,
    import_error,
    integrity_error,
    internal_server_error,
    method_not_allowed,
    not_implemented_error,
    page_not_found,
    sqlalchemy_error,
    type_error,
    unauthorized,
    value_error,
    zero_division_error,
)

if __name__ == "__main__":
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    CORS(app, resources={r"/*": {"origins": "http://localhost:*"}})

    socketio = SocketIO(app)

    @socketio.on('message')
    def handleMessage(msg):
        print(msg)
        send(msg, broadcast=True)

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

    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)
    app.register_error_handler(403, forbidden)
    app.register_error_handler(401, unauthorized)
    app.register_error_handler(400, bad_request)
    app.register_error_handler(405, method_not_allowed)
    app.register_error_handler(AttributeError, attribute_error)
    app.register_error_handler(ZeroDivisionError, zero_division_error)
    app.register_error_handler(ImportError, import_error)
    app.register_error_handler(NotImplementedError, not_implemented_error)
    app.register_error_handler(TypeError, type_error)
    app.register_error_handler(IntegrityError, integrity_error)
    app.register_error_handler(ValueError, value_error)
    app.register_error_handler(SQLAlchemyError, sqlalchemy_error)
    app.register_error_handler(Exception, exception_error)

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

    from routes.dashboard import dashboard

    app.register_blueprint(dashboard)

    from routes.venta import venta

    app.register_blueprint(venta)

    from routes.configuracion import configuracion

    app.register_blueprint(configuracion)

    from routes.utilidad import utilidad

    app.register_blueprint(utilidad)

    setup_admin(app, db)

    def has_no_empty_params(rule):
        """Revisa si la regla tiene parámetros vacíos"""
        defaults = rule.defaults if rule.defaults is not None else ()
        arguments = rule.arguments if rule.arguments is not None else ()
        return len(defaults) >= len(arguments)

    def get_field_type(field):
        if isinstance(field, wtforms.PasswordField):
            return "password"
        elif isinstance(field, wtforms.IntegerField):
            return "number"
        # Agrega más condiciones aquí para otros tipos de campos si es necesario
        else:
            return "text"  # Valor predeterminado para campos de texto

    @app.route("/site-map")
    def site_map():
        """Muestra el mapa del sitio"""
        links = []
        for rule in app.url_map.iter_rules():
            links.append(rule)
            print(rule)

        return str(links)

    app.jinja_env.globals.update(get_field_type=get_field_type)

    socketio.run(app, port=4000)
