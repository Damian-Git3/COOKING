from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError
from database.models import (
    db,
    Usuario

)
from routes import auth

configuracion = Blueprint("configuracion", __name__, url_prefix="/configuracion")

@configuracion.route("/usuario", methods=["POST"])
@login_required
def guardar_informacion_usuario():
    try:
        # Busca el usuario actual en la base de datos
        usuario_actual = Usuario.query.get(current_user.id)

        nombre = request.form.get("nombre")
        correo = request.form.get("correo")
        contrasenia = request.form.get("contrasenia")

        if nombre:
            usuario_actual.nombre = nombre
        if correo:
            usuario_actual.correo = correo
        if contrasenia:
            usuario_actual.contrasenia = generate_password_hash(contrasenia)

        db.session.commit()

        
        return redirect(url_for('auth.logout'))
    except SQLAlchemyError as e:
        # Aquí puedes manejar el error, por ejemplo, mostrándolo al usuario o registrándolo
        print(f"Error al guardar el usuario: {e}")
