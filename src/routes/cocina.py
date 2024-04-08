from flask import Blueprint, render_template
from flask_login import login_required, current_user

cocina = Blueprint('cocina', __name__, url_prefix="/cocina")


@cocina.route('/')
@login_required
def solicitudesProduccion():
    return render_template('modulos/cocina/solicitudes-produccion.html')
