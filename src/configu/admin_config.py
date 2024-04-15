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
from wtforms.fields import BooleanField, DecimalField
from wtforms.validators import NumberRange
from wtforms import TextAreaField

import os


class AdminModelView(ModelView):
    def is_accessible(self):
        """
        Verifica si el usuario actual tiene el rol de "admin".
        Si no es así, redirige al usuario a la página de inicio de sesión.
        """
        if not current_user.is_authenticated:
            return False
        if not current_user.has_role("admin"):
            return False
        return True

    def inaccessible_callback(self, name, **kwargs):
        """
        Redirige al usuario a la página de inicio de sesión si intenta acceder a una vista
        a la que no tiene acceso.
        """
        return redirect(url_for("auth.login", next=request.url))


class AdminIndexView(AdminIndexView):
    def is_accessible(self):
        """
        Verifica si el usuario actual tiene el rol de "admin".
        Si no es así, redirige al usuario a la página de inicio de sesión.
        """
        if not current_user.is_authenticated:
            return False
        if not current_user.has_role("admin"):
            return False
        return True

    def inaccessible_callback(self, name, **kwargs):
        """
        Redirige al usuario a la página de inicio de sesión si intenta acceder a una vista
        a la que no tiene acceso.
        """
        return redirect(url_for("auth.login", next=request.url))


def setup_admin(app, db):

    admin = Admin(
        app,
        index_view=AdminIndexView(menu_icon_type="fa-solid", menu_icon_value="fa-home"),
        template_mode="bootstrap4",
    )

    # Clase base para modelos configuration
    class BaseModelConfiguration(AdminModelView):
        page_size = 10

    # Clase de vista personalizada para Usuario
    class UsuarioView(BaseModelConfiguration):
        form_columns = ["nombre", "correo", "estatus", "roles"]
        column_list = ["nombre", "correo", "estatus", "roles"]
        column_searchable_list = ("nombre", "correo")
        form_columns = ["nombre", "correo", "estatus", "roles"]
        column_list = ["nombre", "correo", "estatus", "roles"]
        column_searchable_list = ("nombre", "correo")

        def on_model_change(self, form, Usuario, is_created):
            if is_created:
                Usuario.contrasenia = generate_password_hash("1234")
                flash(f"La contraseña automatica para {Usuario.nombre} es 1234")

    class RecetaView(BaseModelConfiguration):
        form_columns = [
            "nombre",
            "descripcion",
            "piezas",
            "utilidad",
            "imagen",
            "estatus",
        ]
        column_list = [
            "nombre",
            "descripcion",
            "piezas",
            "utilidad",
            "peso_estimado",
            "estatus",
        ]
        column_labels = {
            "peso_estimado": "Peso promedio por Pieza"  # Cambia el nombre de la columna para especificar gramos
        }
        form_extra_fields = {
            "imagen": ImageUploadField(
                "Imagen",
                base_path=os.path.join(
                    os.path.dirname(__file__), "..", "static", "img", "cookies"
                ),
                url_relative_path="img/cookies/",
            ),
            "estatus": BooleanField("Activar Receta"),
            "utilidad": DecimalField(
                "Utilidad (%)",
                validators=[
                    NumberRange(
                        min=0,
                        message="La utilidad no puede ser menor a 0 porque genera perdidas",
                    )
                ],
            ),
        }
        form_args = {
            "utilidad": {
                "description": "La utilidad es tomada como porcentaje, una utilidad del 100% genera un precio de venta del doble del costo de producción.",
                "type": "number",
                "step": "1",
            }
        }

        form_overrides = {"descripcion": TextAreaField}

        def peso_estimado_formatter(view, context, model, name):
            return f"{model.peso_estimado * 1000:.0f} gr"

        def utilidad_formatter(view, context, model, name):
            return f"{model.utilidad * 1:.2f}%"

        # Asigna el formateador personalizado a la columna peso_estimado
        column_formatters = {
            "peso_estimado": peso_estimado_formatter,
            "utilidad": utilidad_formatter,
        }
        inline_models = (
            (
                InsumosReceta,
                {
                    "form_columns": ("cantidad", "insumo", "idReceta", "idInsumo"),
                    "form_label": "Insumos",
                },
            ),
        )

        def on_model_change(self, form, model, is_created):

            total_cantidad = sum(insumo.cantidad for insumo in model.insumos)
            model.peso_estimado = total_cantidad / model.piezas if model.piezas else 0
            model.estatus = form.estatus.data

        def on_model_delete(self, model):
            model.estatus = 0
            db.session.commit()

        def delete_model(self, model):
            try:
                # Eliminar los registros relacionados en la tabla InsumosReceta
                InsumosReceta.query.filter_by(idReceta=model.id).delete()
                # Llamar al método delete_model de la superclase para eliminar la receta
                return super(RecetaView, self).delete_model(model)
            except Exception as e:
                flash(
                    "Error al eliminar la receta y los registros relacionados: {}".format(
                        str(e)
                    ),
                    "error",
                )
                return False

    class InsumoView(BaseModelConfiguration):
        form_columns = [
            "nombre",
            "descripcion",
            "unidad_medida",
            "cantidad_maxima",
            "cantidad_minima",
            "merma",
        ]
        column_list = [
            "nombre",
            "descripcion",
            "unidad_medida",
            "cantidad_maxima",
            "cantidad_minima",
            "merma",
        ]

        inline_models = (
            (
                InsumosReceta,
                {
                    "form_columns": ("cantidad", "receta", "idReceta", "idInsumo"),
                    "form_label": "Recetas Asociadas",
                },
            ),
        )

        column_formatters = {
            # Aquí puedes agregar formatters personalizados si es necesario
        }

        def delete_model(self, model):
            try:
                # Eliminar los registros relacionados en la tabla InsumosReceta
                InsumosReceta.query.filter_by(idInsumo=model.id).delete()
                # Llamar al método delete_model de la superclase para eliminar el insumo
                return super(InsumoView, self).delete_model(model)
            except Exception as e:
                flash(
                    "Error al eliminar el insumo y los registros relacionados: {}".format(
                        str(e)
                    ),
                    "error",
                )
                return False

    # Clase de vista personalizada para Rol
    class RolView(BaseModelConfiguration):
        can_create = True
        can_delete = False
        form_colums = ["descripcion", "usuarios"]
        column_list = ["nombre", "descripcion", "usuarios"]

    babel = Babel(app)

    # Modificiar idioma de flask_admin
    def get_locale():
        return "es"

    babel.init_app(app, locale_selector=get_locale)

    # Agregar módulos a Flask_Admin
    admin.add_view(
        UsuarioView(
            Usuario, db.session, menu_icon_type="fa-solid", menu_icon_value="fa-user"
        )
    )
    # admin.add_view(RolView(Rol, db.session,
    # menu_icon_type='fa-solid', menu_icon_value='fa-ruler'))
    admin.add_view(
        InsumoView(
            Insumo, db.session, menu_icon_type="fa-solid", menu_icon_value="fa-carrot"
        )
    )
    admin.add_view(
        AdminModelView(
            Proveedor,
            db.session,
            menu_icon_type="fa-solid",
            menu_icon_value="fa-handshake",
        )
    )
    admin.add_view(
        RecetaView(
            Receta,
            db.session,
            menu_icon_type="fa-solid",
            menu_icon_value="fa-clipboard",
        )
    )

    return admin
