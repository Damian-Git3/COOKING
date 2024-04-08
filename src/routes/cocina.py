from flask import Blueprint, render_template
from flask_login import login_required, current_user
from database.models import SolicitudProduccion
from database.models import db

cocina = Blueprint('cocina', __name__, url_prefix="/cocina")

@cocina.route('/')
@login_required
def solicitudesProduccion():
    solicitudesProduccion = SolicitudProduccion.query.all()
    
    return render_template('modulos/cocina/solicitudes-produccion.html', solicitudesProduccion = solicitudesProduccion)
