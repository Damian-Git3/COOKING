from flask import Blueprint, flash, redirect, request, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError
from database.models import db, Usuario
from forms import usuario

configuracion = Blueprint("configuracion", __name__, url_prefix="/configuracion")


@configuracion.route("/usuario", methods=["POST"])
@login_required
def guardar_informacion_usuario():
    """Guarda la información del usuario en la base de datos"""
    try:
        form_usuario = usuario.UsuarioForm(request.form)
        # Busca el usuario actual en la base de datos
        usuario_actual = Usuario.query.get(current_user.id)

        if request.method == "POST" and form_usuario.validate():
            nombre = form_usuario.nombre.data
            correo = form_usuario.correo.data
            contrasenia = form_usuario.contrasenia.data
            confirmacion = form_usuario.confirmacion.data

            if nombre:
                usuario_actual.nombre = nombre
            if correo:
                usuario_actual.correo = correo
            if contrasenia and confirmacion and contrasenia == confirmacion:
                usuario_actual.contrasenia = generate_password_hash(contrasenia)

            db.session.commit()
            return redirect(url_for("auth.logout"))
        else:
            flash("La información proporcionada no es válida", "error")
            return redirect(url_for("main.configuracion"))

    except SQLAlchemyError as e:
        # Aquí puedes manejar el error, por ejemplo, mostrándolo al usuario o registrándolo
        print(f"Error al guardar el usuario: {e}")
