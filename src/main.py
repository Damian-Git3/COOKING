from flask import Blueprint, render_template 
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/menu')
@login_required
def menu():
    
    admin = current_user.has_rol('Administrador')
    cocinero = current_user.has_rol('Cocinero')
    vendedor = current_user.has_rol('Vendedor')
    
    return render_template('menu.html', admin=admin, cocinero=cocinero, vendedor=vendedor)



