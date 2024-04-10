from flask_admin import Admin, AdminIndexView
from flask_admin.form import ImageUploadField
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash
from database.models import Usuario, Rol, Insumo, Proveedor, Receta, InsumosReceta
from flask_babel import Babel
from flask import flash, url_for
from wtforms.validators import DataRequired
from markupsafe import Markup
from flask_login import current_user
from flask import redirect, url_for, request

import os

class AdminModelView(ModelView):
    def is_accessible(self):
        """
        Verifica si el usuario actual tiene el rol de "admin".
        Si no es así, redirige al usuario a la página de inicio de sesión.
        """
        if not current_user.is_authenticated:
            return False
        if not current_user.has_rol('admin'):
            return False
        return True

    def inaccessible_callback(self, name, **kwargs):
        """
        Redirige al usuario a la página de inicio de sesión si intenta acceder a una vista
        a la que no tiene acceso.
        """
        return redirect(url_for('auth.login', next=request.url))
    
class AdminIndexView(AdminIndexView):
    def is_accessible(self):
        """
        Verifica si el usuario actual tiene el rol de "admin".
        Si no es así, redirige al usuario a la página de inicio de sesión.
        """
        if not current_user.is_authenticated:
            return False
        if not current_user.has_rol('admin'):
            return False
        return True

    def inaccessible_callback(self, name, **kwargs):
        """
        Redirige al usuario a la página de inicio de sesión si intenta acceder a una vista
        a la que no tiene acceso.
        """
        return redirect(url_for('auth.login', next=request.url))


def setup_admin(app, db):
    
    admin = Admin(app, index_view=AdminIndexView(
        menu_icon_type='fa-solid',
        menu_icon_value='fa-home'
    ), template_mode='bootstrap4')

    # Clase base para modelos configuration
    class BaseModelConfiguration(AdminModelView):
        page_size = 10

    # Clase de vista personalizada para Usuario
    class UsuarioView(BaseModelConfiguration):
        form_columns = ['nombre', 'correo', 'estatus', 'roles']
        column_list = ['nombre', 'correo', 'estatus', 'roles']
        column_searchable_list = ('nombre', 'correo')

        def on_model_change(self, form, Usuario, is_created):
            if is_created:
                Usuario.contrasenia = generate_password_hash('1234')
                flash(
                    f"La contraseña automatica para {Usuario.nombre} es 1234")

    class RecetaView(BaseModelConfiguration):
        form_columns = ['nombre', 'descripcion', 'piezas', 'utilidad', 'peso_estimado', 'imagen']
        column_list = ['nombre', 'descripcion', 'piezas', 'utilidad', 'peso_estimado']
        
        inline_models = ((
            InsumosReceta,
            {
                'form_columns': ('cantidad', 'insumo', 'idReceta', 'idInsumo'),
                'form_label': 'Insumos'
            }
        ),)

        column_formatters = {
            'imagen': lambda v, c, m, p: Markup(f'<img src="{url_for("static", filename="img/cookies/" + m.imagen)}" style="max-width:300px; max-height:300px;">')
        }

        def delete_model(self, model):
            try:
                # Eliminar los registros relacionados en la tabla InsumosReceta
                InsumosReceta.query.filter_by(idReceta=model.id).delete()
                # Llamar al método delete_model de la superclase para eliminar la receta
                return super(RecetaView, self).delete_model(model)
            except Exception as e:
                flash('Error al eliminar la receta y los registros relacionados: {}'.format(
                    str(e)), 'error')
                return False

    # Clase de vista personalizada para Rol
    class RolView(BaseModelConfiguration):
        can_create = True
        can_delete = False
        form_colums = ['descripcion', 'usuarios']
        column_list = ['nombre', 'descripcion', 'usuarios']

    babel = Babel(app)

    # Modificiar idioma de flask_admin
    def get_locale():
        return 'es'
    babel.init_app(app, locale_selector=get_locale)

    # Agregar módulos a Flask_Admin
    admin.add_view(UsuarioView(Usuario, db.session,
                   menu_icon_type='fa-solid', menu_icon_value='fa-user'))
    admin.add_view(RolView(Rol, db.session,
                   menu_icon_type='fa-solid', menu_icon_value='fa-ruler'))
    admin.add_view(AdminModelView(Insumo, db.session,
                   menu_icon_type='fa-solid', menu_icon_value='fa-carrot'))
    admin.add_view(AdminModelView(Proveedor, db.session,
                   menu_icon_type='fa-solid', menu_icon_value='fa-handshake'))
    admin.add_view(RecetaView(Receta, db.session,
                   menu_icon_type='fa-solid', menu_icon_value='fa-clipboard'))

    return admin