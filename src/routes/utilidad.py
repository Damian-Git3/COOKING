""" Rutas de la sección de utilidad """

from flask import Blueprint, render_template, request
from flask_login import login_required

from database.models import InsumosReceta, Receta, db
from forms import utilidad as utilidad_form
from logger import logger as log

utilidad = Blueprint("utilidad", __name__, url_prefix="/utilidad")


@utilidad.route("/")
@login_required
def gestion():
    """Ruta para la página de inicio de la sección de utilidad"""
    form = utilidad_form.GetRecetaForm(request.form)

    return render_template("utilidad/utilidad.html", form=form)


@utilidad.route("/obtener-ingredientes", methods=["POST"])
def obtener_ingredientes():
    """Ruta para obtener los ingredientes de una receta"""
    form = utilidad_form.GetRecetaForm(request.form)
    log.debug(form)
    id_receta = form.receta.data

    ingredientes_receta = (
        db.session.query(InsumosReceta)
        .filter(InsumosReceta.idReceta == id_receta)
        .all()
    )

    for ingrediente in ingredientes_receta:
        log.debug(ingrediente)
        log.info(ingrediente.idInsumo)
        log.info(ingrediente.idReceta)
        log.info(ingrediente.cantidad)

    receta_seleccionada = Receta.query.get(id_receta)
    titulo_receta = receta_seleccionada.nombre if receta_seleccionada else None

    insumos_receta = []
    for ingrediente in ingredientes_receta:
        insumos_receta = (
            db.session.query(InsumosReceta)
            .filter(InsumosReceta.idReceta == id_receta)
            .all()
        )

    log.debug(insumos_receta)
    return render_template(
        "utilidad/utilidad.html",
        form=form,
        ingredientes=ingredientes_receta,
        titulo_receta=titulo_receta,
        receta_seleccionada=id_receta,
    )
