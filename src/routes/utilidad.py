""" Rutas de la sección de utilidad """

from flask import Blueprint, render_template, request
from flask_login import login_required
from datetime import datetime
from sqlalchemy import func


from database.models import Insumo, InsumosReceta, LoteInsumo, Receta, db
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

    # Modificar la consulta para incluir el nombre del insumo
    ingredientes_receta = (
        db.session.query(InsumosReceta, Insumo.nombre)  # Añadir Insumo.nombre aquí
        .join(Insumo, InsumosReceta.idInsumo == Insumo.id)  # Unir las tablas
        .filter(InsumosReceta.idReceta == id_receta)
        .all()
    )

    log.debug(ingredientes_receta)

    ingredientes_con_nombres = [
        {
            "insumo": nombre_insumo,  # Acceder al nombre del insumo
            "cantidad": insumo_receta.cantidad,  # Acceder a la cantidad del insumo en la receta
            "cantidad_total": obtener_cantidad_y_promedio_precio_insumo(
                insumo_receta.idInsumo
            )[
                0
            ],  # Obtener la cantidad total del insumo
            "promedio_precio": round(obtener_cantidad_y_promedio_precio_insumo(
                insumo_receta.idInsumo
            )[
                1
            ],2),  # Obtener el promedio del precio por unidad del insumo
            "costo_total": round(insumo_receta.cantidad
            * promedio_precio,2)  # Calcular el costo total por insumo
        }
        for insumo_receta, nombre_insumo in ingredientes_receta  # Desempaquetar la tupla
        for cantidad_total, promedio_precio in [
            obtener_cantidad_y_promedio_precio_insumo(insumo_receta.idInsumo)
        ]
    ]

    log.debug(ingredientes_con_nombres)
    receta_seleccionada = Receta.query.get(id_receta)
    titulo_receta = receta_seleccionada.nombre if receta_seleccionada else None

    return render_template(
        "utilidad/utilidad.html",
        form=form,
        ingredientes=ingredientes_con_nombres,  # Pasar la lista modificada
        titulo_receta=titulo_receta,
        receta_seleccionada=id_receta,
        # Calcular el costo total de la receta sumando todos los costos totales de los ingredientes
        costo_total_receta=round(
            sum(ingrediente["costo_total"] for ingrediente in ingredientes_con_nombres),
            2,
        ),
    )


def obtener_cantidad_y_promedio_precio_insumo(id_insumo):
    """Obtiene la cantidad total de un insumo, considerando solo lotes con fecha de caducidad vigente."""
    # Obtener la fecha actual
    fecha_actual = (
        datetime.now().date()
    )  # Asegúrate de obtener solo la fecha, no la hora

    # Realizar la consulta para sumar la cantidad y calcular el promedio del precio por unidad
    resultado = (
        db.session.query(
            func.sum(LoteInsumo.cantidad).label('cantidad_total'),
            func.avg(LoteInsumo.precio_unidad).label('promedio_precio')
        )
        .filter(LoteInsumo.idInsumo == id_insumo, LoteInsumo.fecha_caducidad > fecha_actual)
        .one()
    )

    # Si no hay lotes que cumplan con los criterios, la función devuelve 0 para la cantidad total y None para el promedio del precio
    return resultado.cantidad_total if resultado.cantidad_total is not None else 0, resultado.promedio_precio
