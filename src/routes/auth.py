from datetime import datetime
from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

import forms.forms as forms
from database.models import LogLogin, Usuario, db

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    if current_user.is_authenticated:

        usuario_id = current_user.get_id()

        # Obtiene el usuario de la base de datos
        user = Usuario.query.filter_by(id=usuario_id).first()

        user.last_login_at = user.current_login_at
        user.current_login_at = datetime.now()

        # Guarda los cambios en la base de datos
        db.session.commit()
        return redirect(url_for("main.menu"))
    return render_template("login.html")


@auth.route("/login", methods=["POST"])
def login_post():
    usuario = request.form.get("usuario")
    contrasenia = request.form.get("contrasenia")
    recordar = True if request.form.get("recordarme") else False

    user = Usuario.query.filter_by(nombre=usuario).first()

    if not user:
        flash(
            "No se ha encontrado un usuario con esas credenciales"
            + "Por favor, verifica la información"
        )
        log_login = LogLogin(fecha=datetime.now(), exito=False)
        db.session.add(log_login)
        db.session.commit()
        return render_template("login.html")
    elif not check_password_hash(user.contrasenia, contrasenia):
        flash("Credenciales incorrectas. Por favor, inténtelo de nuevo.")
        log_login = LogLogin(fecha=datetime.now(), exito=False, idUsuario=user.id)
        db.session.add(log_login)
        db.session.commit()
        return render_template("login.html")
    elif not user.estatus:
        flash("Usuario no activo. Por favor, consulta con tu administrador.")
        log_login = LogLogin(fecha=datetime.now(), exito=False, idUsuario=user.id)
        db.session.add(log_login)
        db.session.commit()
        return render_template("login.html")

    user.last_login_at = user.current_login_at
    user.current_login_at = datetime.now()

    # Guarda los cambios en la base de datos
    db.session.commit()

    log_login = LogLogin(fecha=datetime.now(), exito=True, idUsuario=user.id)
    db.session.add(log_login)
    db.session.commit()

    login_user(user, remember=recordar)
    return redirect(url_for("main.menu"))


@auth.route("/signup")
def signup():
    form = forms.SignupForm(request.form)
    return render_template("signup_temporal.html", form=form)


@auth.route("/signup", methods=["POST"])
def signup_post():
    form = forms.SignupForm(request.form)
    correo = request.form.get("correo")
    nombre = request.form.get("nombre")
    contrasenia = request.form.get("contrasenia")

    if not form.validate():
        return render_template("signup_temporal.html", form=form)

    user = Usuario.query.filter_by(correo=correo).first()

    if user:
        flash("Este correo ya existe.")
        return redirect(url_for("auth.signup"))

    new_user = Usuario(
        correo=correo, nombre=nombre, contrasenia=generate_password_hash(contrasenia)
    )

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("auth.login"))


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


def requires_role(role_name):
    def decorator(f):
        @login_required
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login", next=request.url))
            if current_user.has_role("admin"):
                return f(*args, **kwargs)
            if not current_user.has_role(role_name):
                return redirect(url_for("main.menu"))
            return f(*args, **kwargs)

        return decorated_function

    return decorator
