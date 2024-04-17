""" Rutas de la sección de utilidad """

from flask import Blueprint, render_template, request
from flask_login import login_required

from forms import utilidad as utilidad_form

utilidad = Blueprint("utilidad", __name__, url_prefix="/utilidad")


@utilidad.route("/")
@login_required
def gestion():
    """Ruta para la página de inicio de la sección de utilidad"""
    form = utilidad_form.UtilidadForm(request.form)

    return render_template("utilidad/utilidad.html", form=form)
