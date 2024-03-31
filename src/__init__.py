from flask import Flask, render_template

from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager 
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_babel import Babel
from config import DevelopmentConfig

if __name__ == "__main__":
    from models import db, Usuario, Rol, Insumo, Proveedor, UserMixin
    
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    
    admin = Admin(app, template_mode='bootstrap4')
    babel = Babel(app)
    
    class UsuarioView(ModelView):
        form_colums = ['nombre', 'correo', 'estatus', 'roles']
        column_list = ['nombre', 'correo', 'estatus', 'roles']
        
    class RolView(ModelView):
        can_create = False
        can_delete = False
        form_colums = ['descripcion', 'usuarios']
        column_list = ['nombre', 'descripcion', 'usuarios']

    # Agregar módulos a Flask_Admin
    admin.add_view(UsuarioView(Usuario, db.session))
    admin.add_view(RolView(Rol, db.session))
    admin.add_view(ModelView(Insumo, db.session))
    admin.add_view(ModelView(Proveedor, db.session))

    # Función para cambiar idioma al Flask_Admin
    def get_locale():
        return 'es'
    
    csrf=CSRFProtect()
    
    babel.init_app(app, locale_selector=get_locale)
    csrf.init_app(app)
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'
    login_manager.init_app(app)
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"),404


    @login_manager.user_loader
    def load_user(user_id): 
        return Usuario.query.filter_by(id=int(user_id)).first()

    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    with app.app_context():
        db.create_all()
        
    app.run(port=4000)
    
