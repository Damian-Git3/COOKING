#Run pip install flask-blueprint
import re
from flask import Blueprint

utilidad = Blueprint('utilidad',__name__, url_prefix='/utilidad')

@utilidad.route('/')
def utilidad:
    
    return render_template('utilidad/utilidad.html')