from datetime import datetime, timedelta
from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash

from database.models import CorteCaja, LogLogin, LoteGalleta, LoteInsumo, Usuario, db

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    corte_de_hoy = CorteCaja.query.filter_by(fecha_corte=datetime.now().date()).first()

    if not corte_de_hoy:
        nuevo_corte = CorteCaja(
            fecha_corte=datetime.now().date(), monto_inicial=1000, monto_final=1000
        )
        db.session.add(nuevo_corte)
        # Guarda los cambios en la base de datos
        db.session.commit()

        # mandar a merma toda la cantidad de los lotes de insumos cuya fecha de caducidad sea menor a la fecha actual
        lotes_insumo = LoteInsumo.query.filter(
            LoteInsumo.fecha_caducidad < datetime.now().date()
        ).all()
        for lote in lotes_insumo:
            lote.merma += lote.cantidad
            lote.cantidad = 0
            db.session.commit()
        # mandar a merma toda la cantidad de los lotes de galletas cuya fecha de entrada sea menor a la fecha de hace 15 dias
        lotes_galleta = LoteGalleta.query.filter(
            LoteGalleta.fecha_entrada < datetime.now().date() - timedelta(days=15)
        ).all()
        for lote in lotes_galleta:
            lote.merma += lote.cantidad
            lote.cantidad = 0
            db.session.commit()

    if current_user.is_authenticated:

        usuario_id = current_user.get_id()

        # Obtiene el usuario de la base de datos
        user = Usuario.query.filter_by(id=usuario_id).first()

        user.last_login_at = user.current_login_at
        user.current_login_at = datetime.now()

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
            "No se ha encontrado un usuario con esas credenciales. Por favor, verifica la información"
        )
        return render_template("login.html")
    print(user)
    una_hora_atras = datetime.now() - timedelta(minutes=30)
    intentos_fallidos = (
        db.session.query(LogLogin)
        .filter(
            LogLogin.idUsuario == user.id,
            LogLogin.fecha >= datetime.date(una_hora_atras),
        )
        .order_by(LogLogin.fecha.desc())
        .limit(4)
        .all()
    )

    intentos = 0

    for intento in intentos_fallidos:
        if not intento.exito:
            intentos += 1
    if intentos > 3:
        flash(
            "Has alcanzado el límite de intentos fallidos. Por favor, inténtalo de nuevo más tarde."
        )
        log_login = LogLogin(fecha=datetime.now(), exito=False)
        db.session.add(log_login)
        db.session.commit()
        return render_template("login.html")

    if not user:
        flash(
            "No se ha encontrado un usuario con esas credenciales. Por favor, verifica la información"
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
