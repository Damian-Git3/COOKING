""" Rutas de la sección de utilidad """

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
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
    form_utilidad = utilidad_form.UtilidadForm(request.form)

    return render_template(
        "utilidad/utilidad.html", form=form, formUtilidad=form_utilidad
    )


@utilidad.route("/obtener-ingredientes", methods=["POST"])
def obtener_ingredientes():
    """Ruta para obtener los ingredientes de una receta"""
    form = utilidad_form.GetRecetaForm(request.form)
    form_utilidad = utilidad_form.UtilidadForm(request.form)
    log.debug(form)
    id_receta = form.receta.data

    ingredientes_receta = (
        db.session.query(
            InsumosReceta, Insumo.nombre, Insumo.unidad_medida
        )  # Añadir Insumo.nombre aquí
        .join(Insumo, InsumosReceta.idInsumo == Insumo.id)  # Unir las tablas
        .filter(InsumosReceta.idReceta == id_receta)
        .all()
    )

    log.debug(ingredientes_receta)

    ingredientes_con_nombres = []

    for insumo_receta, nombre_insumo, unidad_medida in ingredientes_receta:
        ingredientes_con_nombres.append(
            {
                "insumo": nombre_insumo,
                "inventario": calcular_precio_total(insumo_receta.idInsumo)[
                    "cantidad_total"
                ],
                "unidad": unidad_medida,
                "precio_total": round(
                    calcular_precio_total(insumo_receta.idInsumo)["precio_total"], 2
                ),
                "cantidad": insumo_receta.cantidad,
                "costo_total": round(
                    insumo_receta.cantidad
                    * calcular_precio_total(insumo_receta.idInsumo)["precio_total"],
                    2,
                ),
            }
        )

    log.debug(ingredientes_con_nombres)
    receta_seleccionada = Receta.query.get(id_receta)
    titulo_receta = receta_seleccionada.nombre if receta_seleccionada else None
    utilidad_receta = receta_seleccionada.utilidad if receta_seleccionada else None
    form_utilidad.id_receta.data = id_receta
    form_utilidad.costo_total.data = round(
        sum(ingrediente["costo_total"] for ingrediente in ingredientes_con_nombres), 2
    )
    form_utilidad.costo_venta.data = utilidad_receta

    return render_template(
        "utilidad/utilidad.html",
        form=form,
        formUtilidad=form_utilidad,
        ingredientes=ingredientes_con_nombres,
        titulo_receta=titulo_receta,
        receta_seleccionada=id_receta,
        utilidad_receta=utilidad_receta,
    )


@utilidad.route("/guardar", methods=["POST"])
def guardar():
    """Ruta para guardar la utilidad de una receta"""
    form_utilidad = utilidad_form.UtilidadForm(request.form)

    id_receta = form_utilidad.id_receta.data
    precio = form_utilidad.costo_venta.data

    receta_seleccionada = Receta.query.get(id_receta)
    receta_seleccionada.utilidad = precio
    db.session.commit()

    flash(
        "Utilidad Registrada Correctamente",
        "success",
    )

    return redirect(url_for("utilidad.gestion"))


def calcular_precio_total(id_insumo):
    """
    Calcula el precio total de la harina basado en la cantidad total disponible,
    considerando solo los lotes con fecha de caducidad mayor a la fecha actual.

    Parámetros:
    - id_insumo: El ID del insumo (harina) para el cual se calculará el precio total.

    Retorna:
    - Un diccionario con el precio total calculado y la cantidad total de harina disponible.
    """

    fecha_actual = datetime.now().date()

    # Realiza la consulta a la base de datos para obtener los lotes de harina por id_insumo
    # y que tengan una fecha de caducidad mayor a la fecha actual
    lotes = (
        db.session.query(LoteInsumo)
        .filter(
            LoteInsumo.idInsumo == id_insumo, LoteInsumo.fecha_caducidad > fecha_actual
        )
        .all()
    )

    # Inicializa el total de cantidad y el total de precio
    total_cantidad = 0
    total_precio = 0

    # Itera sobre cada lote
    for lote in lotes:
        # Suma la cantidad y el precio de cada lote al total
        total_cantidad += lote.cantidad
        total_precio += lote.cantidad * lote.precio_unidad

    # Calcula el precio total
    precio_total = total_precio / total_cantidad if total_cantidad > 0 else 0

    # Retorna el precio total y la cantidad total
    return {"precio_total": precio_total, "cantidad_total": total_cantidad}
