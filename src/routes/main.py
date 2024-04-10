from flask import Blueprint, render_template 
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/inicio')
@login_required
def menu():
    usuario = current_user.nombre
    admin = current_user.has_rol('admin')
    vendedor = current_user.has_rol('vendedor')
    cocinero = current_user.has_rol('cocinero')
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
    return render_template('inicio.html', mensaje=mensaje)
