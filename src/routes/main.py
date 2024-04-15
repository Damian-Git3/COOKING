from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from forms import usuario

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/inicio")
@login_required
def menu():
    usuario = current_user.nombre
    admin = current_user.has_role("admin")
    vendedor = current_user.has_role("vendedor")
    cocinero = current_user.has_role("cocinero")
    mensaje = f"Bienvenido {usuario} "
    if admin or vendedor or cocinero:
        mensaje += " tienes "
        if admin and vendedor and cocinero:
            mensaje += "todos los permisos del sistema."
        if admin and vendedor and not cocinero:
            mensaje += "permisos de administrador y vendedor."
        if admin and cocinero and not vendedor:
            mensaje += "permisos de administrador y cocinero."
        if vendedor and cocinero and not admin:
            mensaje += "permisos de vendedor y cocinero."
        if admin and not vendedor and not cocinero:
            mensaje += "permisos de administrador."
        if vendedor and not admin and not cocinero:
            mensaje += "permisos de vendedor."
        if cocinero and not admin and not vendedor:
            mensaje += "permisos de cocinero."
    else:
        mensaje += "no tienes rol asignado."

    return render_template("inicio.html", mensaje=mensaje)

@main.route("/configuracion")
@login_required
def configuracion():
    """Ruta para la configuración del usuario"""

    form_usuario = usuario.UsuarioForm(request.form)
    return render_template("configuracion/configuracion.html", formUsuario=form_usuario)
