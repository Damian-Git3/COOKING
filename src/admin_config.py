from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash
from models import Usuario, Rol, Insumo, Proveedor
from flask_babel import Babel

def setup_admin(app, db):
    admin = Admin(app, template_mode='bootstrap4')
    babel = Babel(app)
    
    # Modificiar idioma de flask_admin
    def get_locale():
        return 'es'
    
    babel.init_app(app, locale_selector=get_locale)

    # Clase de vista personalizada para Usuario
    class UsuarioView(ModelView):
        form_columns = ['nombre', 'correo', 'estatus', 'roles']
        column_list = ['nombre', 'correo', 'estatus', 'roles']
        
        def on_model_change(self, form, Usuario, is_created):
            if is_created:
                Usuario.contrasenia = generate_password_hash('1234')

    # Clase de vista personalizada para Rol
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
