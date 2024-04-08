from flask import Blueprint, render_template
from flask_login import login_required, current_user

cocina = Blueprint('cocina', __name__, url_prefix="/cocina")


@cocina.route('/cocinar')
@login_required
def cocinar():
    return render_template('modulos/cocina/cocinar.html')

@cocina.route('/recetas')
@login_required
def recetas():
    return render_template('modulos/cocina/recetas.html')

@cocina.route('/insumos')
@login_required
def insumos():
    return render_template('modulos/cocina/insumos.html')
