from flask import Blueprint, render_template 
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/inicio')
@login_required
def menu():
    return render_template('inicio.html')

@main.route('/mermas')
@login_required
def mermas():
    return render_template('modulos/general/mermas.html')

@main.route('/inventario')
@login_required
def inventario():
    return render_template('modulos/general/inventario.html')



