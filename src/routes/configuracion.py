import binascii
import hashlib

import requests
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash

from database.models import Usuario, db
from forms import usuario

configuracion = Blueprint("configuracion", __name__, url_prefix="/configuracion")


@configuracion.route("/usuario", methods=["POST"])
@login_required
def guardar_informacion_usuario():
    """Guarda la información del usuario en la base de datos"""

    form_usuario = usuario.UsuarioForm(request.form)
    # Busca el usuario actual en la base de datos
    usuario_actual = Usuario.query.get(current_user.id)

    if request.method == "POST" and form_usuario.validate():
        correo = form_usuario.correo.data
        contrasenia = form_usuario.contrasenia.data
        confirmacion = form_usuario.confirmacion.data

        result = check_password_compromised(contrasenia)

        if result:
            flash(
                f"La contraseña que ingresaste ha sido filtrada {result}"
                + " veces en bases de datos de contraseñas filtradas"
                + "Usa otra contraseña",
                "error",
            )
            return render_template(
                "configuracion/configuracion.html", formUsuario=form_usuario
            )

        if correo:
            usuario_actual.correo = correo
        if contrasenia and confirmacion and contrasenia == confirmacion:
            usuario_actual.contrasenia = generate_password_hash(contrasenia)

            db.session.commit()
            return redirect(url_for("auth.logout"))
    else:
        flash("La información proporcionada no es válida", "error")
        return render_template(
            "configuracion/configuracion.html", formUsuario=form_usuario
        )


def check_password_compromised(password):
    """Verifica si la contraseña ha sido comprometida en una filtración de datos"""

    # Crea un hash SHA-1 de la contraseña
    sha1_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix = sha1_hash[:5]
    suffix = sha1_hash[5:]

    # Realiza una solicitud GET a la API de Have I Been Pwned
    response = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}")
    response.raise_for_status()  # Asegura que la solicitud fue exitosa

    # Busca el sufijo en la respuesta
    for line in response.text.splitlines():
        hash_suffix, count = line.split(":")
        if hash_suffix == suffix:
            return int(
                count
            )  # Devuelve el número de veces que la contraseña ha sido comprometida

    return 0  # La contraseña no ha sido comprometida
