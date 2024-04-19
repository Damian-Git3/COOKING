from datetime import datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from database.models import (
    Compra,
    Insumo,
    InsumosReceta,
    LoteInsumo,
    Receta,
    SolicitudProduccion,
    Usuario,
    db,
)
from forms import forms

cocina = Blueprint("cocina", __name__, url_prefix="/cocina")


@cocina.route("/cocinar")
@login_required
def cocinar():
    solicitudesProduccion = SolicitudProduccion.query.all()
    print(solicitudesProduccion)

    return render_template(
        "modulos/cocina/cocinar.html", solicitudesProduccion=solicitudesProduccion
    )


@cocina.route("/recetas")
@login_required
def recetas():
    return redirect(url_for("cocina."))


@cocina.route("/aceptar-solicitud/<int:idSolicitud>")
@login_required
def aceptarSolicitud(idSolicitud):
    solicitudProduccion = SolicitudProduccion.query.get(idSolicitud)

    if solicitudProduccion:
        solicitudProduccion.estatus = 2

        insumosReceta = InsumosReceta.query.filter_by(
            idReceta=solicitudProduccion.idReceta
        ).all()

        receta = Receta.query.get(solicitudProduccion.idReceta)

        mensajeReceta = f"Descripción receta: \n{receta.descripcion}\n\n"
        mensajeReceta += "Los ingredientes para esta receta son:\n"

        for insumoReceta in insumosReceta:
            insumo = Insumo.query.get(insumoReceta.idInsumo)
            mensajeReceta += f"{insumo.nombre}: {insumoReceta.cantidad * solicitudProduccion.tandas:.2f} {insumo.unidad_medida}\n"

        db.session.commit()

        flash(mensajeReceta, "receta")

        return redirect(url_for("cocina.cocinar"))
    else:
        flash(
            "No se encontro la solicitud de producción con los datos proporcionados",
            "info",
        )
        return redirect(url_for("cocina.cocinar"))


@cocina.route("/finalizar-produccion/<int:idSolicitud>")
@login_required
def finalizarProduccion(idSolicitud):
    print("Finalizando producción")

    solicitudProduccion = SolicitudProduccion.query.get(idSolicitud)
    insumosRecetaProduccion = InsumosReceta.query.filter_by(
        idReceta=solicitudProduccion.idReceta
    ).all()

    print(insumosRecetaProduccion)

    if solicitudProduccion:
        return redirect(url_for("cocina.cocinar"))
    else:
        flash(
            "No se encontro la solicitud de producción con los datos proporcionados",
            "info",
        )
        return redirect(url_for("cocina.cocinar"))


@cocina.route("/lotes/insumos", methods=["GET", "POST"])
def lotes_insumos():
    form = forms.BusquedaLoteInsumoForm(request.form)

    form.insumo.choices = [(0, "Todas los insumos")] + [
        (insumo.id, insumo.nombre) for insumo in Insumo.query.all()
    ]

    if request.method == "POST":
        fecha_inicio_default = datetime.now().date()
        fecha_fin_default = datetime.now().date() + timedelta(
            days=365 * 1000
        )  # Ajusta el valor según sea necesario
        insumo_default = 0

        # Validación y asignación de valores
        try:
            fecha_inicio = (
                form.fecha_inicio.data
                if form.fecha_inicio.data
                else fecha_inicio_default
            )

        except ValueError:
            fecha_inicio = fecha_inicio_default

        try:
            fecha_fin = (
                form.fecha_fin.data if form.fecha_fin.data else fecha_fin_default
            )
        except ValueError:
            fecha_fin = fecha_fin_default

        insumo = form.insumo.data if form.insumo.data else insumo_default
        lotes = []

        if insumo == "0":
            lotes = (
                db.session.query(LoteInsumo, Insumo, Usuario.nombre)
                .join(Insumo, LoteInsumo.idInsumo == Insumo.id)
                .join(Compra, LoteInsumo.idCompra == Compra.id)
                .join(Usuario, Compra.idUsuario == Usuario.id)
                .filter(
                    LoteInsumo.cantidad > 0,
                    LoteInsumo.fecha_caducidad >= fecha_inicio,
                    LoteInsumo.fecha_caducidad <= fecha_fin,
                )
                .order_by(LoteInsumo.fecha_caducidad.asc())
                .all()
            )
        else:
            lotes = (
                db.session.query(LoteInsumo, Insumo, Usuario.nombre)
                .join(Insumo, LoteInsumo.idInsumo == Insumo.id)
                .join(Compra, LoteInsumo.idCompra == Compra.id)
                .join(Usuario, Compra.idUsuario == Usuario.id)
                .filter(
                    LoteInsumo.cantidad > 0,
                    LoteInsumo.fecha_caducidad >= fecha_inicio,
                    LoteInsumo.fecha_caducidad <= fecha_fin,
                    LoteInsumo.idInsumo == insumo,
                )
                .order_by(LoteInsumo.fecha_caducidad.asc())
                .all()
            )

        return render_template(
            "modulos/cocina/insumos.html", form=form, lotes=lotes, lista=True
        )

    lotes = (
        db.session.query(LoteInsumo, Insumo, Usuario.nombre)
        .join(Insumo, LoteInsumo.idInsumo == Insumo.id)
        .join(Compra, LoteInsumo.idCompra == Compra.id)
        .join(Usuario, Compra.idUsuario == Usuario.id)
        .filter(
            LoteInsumo.cantidad > 0,
            LoteInsumo.fecha_caducidad >= datetime.now(),
        )
        .order_by(LoteInsumo.fecha_caducidad.asc())
        .all()
    )

    return render_template(
        "modulos/cocina/insumos.html", form=form, lotes=lotes, lista=True
    )


@cocina.route("/insumos", methods=["GET"])
def lotes_insumos_agrupados():

    insumos = Insumo.query.all()

    for insumo in insumos:
        lotes = (
            LoteInsumo.query.filter(
                LoteInsumo.idInsumo == insumo.id,
                LoteInsumo.fecha_caducidad >= datetime.now().date(),
                LoteInsumo.cantidad > 0,
            )
            .order_by(LoteInsumo.fecha_caducidad)
            .all()
        )
        insumo.num_lotes = len(lotes)
        insumo.proxima_caducidad = lotes[0].fecha_caducidad if lotes else "No hay lotes"
        insumo.cantidad = sum(lote.cantidad for lote in lotes)
        insumo.coste_promedio = (
            sum(lote.precio_unidad * lote.cantidad for lote in lotes) / insumo.cantidad
            if insumo.cantidad
            else 1
        )
        # agregar flash para los insumos que estan por agotarse
        if insumo.cantidad < insumo.cantidad_minima:
            flash(f"(Escacez) El insumo {insumo.nombre} esta por agotarse", "warning")
        # agregar flash para los insumos que sobrepasan la capacidad de almacenamiento
        if insumo.cantidad > insumo.cantidad_maxima:
            flash(
                f"(Exceso) El insumo {insumo.nombre} sobrepasa la capacidad de almacenamiento",
                "info",
            )
        # agregar flash par los lotes del insumo que estan por caducar en los proximos 3 dias
        for lote in lotes:
            if lote.fecha_caducidad <= datetime.now().date() + timedelta(days=3):
                flash(
                    f"(Caducidad) El lote {lote.id} del insumo {insumo.nombre} esta por caducar",
                    "danger",
                )

    return render_template("modulos/cocina/insumo_individual.html", insumos=insumos)


@cocina.route("/merma/insumos/<int:id>", methods=["GET", "POST"])
def merma_insumos(id):
    form = forms.MermaInsumoForm(request.form)
    form.lot_id.data = id

    lote = LoteInsumo.query.get(id)

    cantidad_maxima = lote.cantidad

    insumo = Insumo.query.get(lote.idInsumo)

    tipo_medida = insumo.unidad_medida

    if request.method == "POST" and form.validate():
        cantidad = form.cantidad.data

        id = form.lot_id.data

        if cantidad > lote.cantidad:
            flash(
                "La cantidad de merma no puede ser mayor a la cantidad almacenada en el lote",
                "error",
            )
            return render_template(
                "modulos/venta/insumos.html",
                form=form,
                cantidad_maxima=cantidad_maxima,
                tipo_medida=tipo_medida,
            )

        lote.cantidad -= float(cantidad)
        lote.merma += float(cantidad)
        db.session.commit()
        flash("Merma registrada correctamente", "success")
        return redirect(url_for("cocina.lotes_insumos"))

    return render_template(
        "modulos/cocina/insumos.html",
        form=form,
        cantidad_maxima=cantidad_maxima,
        tipo_medida=tipo_medida,
    )
