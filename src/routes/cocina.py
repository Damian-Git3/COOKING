from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from database.models import (
    SolicitudProduccion,
    Receta,
    Insumo,
    InsumosReceta,
    LoteInsumo,
    Compra,
    Usuario,
)
from database.models import db
from forms import forms
from datetime import datetime

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
    return redirect(url_for("admin.receta"))


@cocina.route("/lotes/insumos")
@login_required
def lotes_insumos():
    return render_template("modulos/cocina/recetas.html")


@cocina.route("/aceptar-solicitud/<int:idSolicitud>")
@login_required
def aceptarSolicitud(idSolicitud):
    solicitudProduccion = SolicitudProduccion.query.get(idSolicitud)

    if solicitudProduccion:
        solicitudProduccion.estatus = 2
        solicitudProduccion.idUsuarioProduccion = current_user.id
        db.session.commit()

        insumosReceta = InsumosReceta.query.filter_by(
            idReceta=solicitudProduccion.idReceta
        ).all()

        receta = Receta.query.get(solicitudProduccion.idReceta)

        mensajeReceta = f"Descripción receta: \n{receta.descripcion}\n\n"
        mensajeReceta += "Los ingredientes para esta receta son:\n"

        for insumoReceta in insumosReceta:
            insumo = Insumo.query.get(insumoReceta.idInsumo)
            mensajeReceta += (
                f"{insumo.nombre}: {insumoReceta.cantidad} {insumo.unidad_medida}\n"
            )

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

    if request.method == "POST" and form.validate():
        fecha_inicio = form.fecha_inicio.data
        fecha_fin = form.fecha_fin.data
        insumo = form.insumo.data
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
