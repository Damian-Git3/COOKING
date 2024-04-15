from flask import (
    Blueprint,
    Flask,
    request,
    render_template,
    Response,
    redirect,
    url_for,
)
from flask_login import login_required, current_user
import math

from flask_wtf.csrf import CSRFProtect
from flask import g
from flask import flash, jsonify
from configu.config import DevelopmentConfig
from database.models import (
    db,
    Usuario,
    Rol,
    asignacion_rol_usuario,
    Insumo,
    Receta,
    SolicitudProduccion,
    Venta,
    DetalleVenta,
    Compra,
    Proveedor,
    LoteGalleta,
    LoteInsumo,
)

from forms import forms
from sqlalchemy.orm import joinedload
from sqlalchemy import desc, extract, text
from datetime import datetime, timedelta
from routes.auth import requires_role

venta = Blueprint("venta", __name__, url_prefix="/venta")


@venta.route("/compras")
@requires_role("vendedor")
def compras():
    return render_template("modulos/venta/compras.html")


@venta.route("/punto_venta")
@requires_role("vendedor")
def punto_venta():
    return render_template("modulos/venta/punto-venta.html")


@venta.route("/solicitud_produccion")
@requires_role("vendedor")
def solicitud_produccion():
    solicitudes = SolicitudProduccion.query.options(
        # Asume que 'receta' es el nombre de la relación en SolicitudProduccion
        joinedload(SolicitudProduccion.receta),
        # Asume que 'usuarioSolicitud' es el nombre de la relación en SolicitudProduccion
        joinedload(SolicitudProduccion.usuarioSolicitud),
        # Asume que 'usuarioProduccion' es el nombre de la relación en SolicitudProduccion
        joinedload(SolicitudProduccion.usuarioProduccion),
    ).all()

    return render_template(
        "modulos/venta/solicitudes-produccion.html", solicitudes=solicitudes
    )


@venta.route("/solicitud_produccion/crear", methods=["GET", "POST"])
@requires_role("vendedor")
def solicitud_produccion_nuevo():
    form = forms.SolicitudProduccionForm(request.form)
    form.receta.choices = [(receta.id, receta.nombre) for receta in Receta.query.all()]
    images = [(receta.id, receta.imagen) for receta in Receta.query.all()]

    if request.method == "GET":
        return render_template(
            "modulos/venta/solicitudesProduccion/create.html",
            form=form,
            images=images,
            nuevo=True,
        )
    else:
        if form.validate():
            usuario_cocinero = 0
            rol_cocinero = Rol.query.filter_by(nombre="cocinero").first()
            if rol_cocinero is not None:
                # Luego, filtra los usuarios que tienen el rol 'cocinero' y ordena por 'is_active'
                usuario_cocinero = (
                    Usuario.query.join(asignacion_rol_usuario)
                    .join(Rol)
                    .filter(Rol.id == rol_cocinero.id)
                    .order_by(desc("is_active"))
                    .first()
                )

                # Si no se encuentra un usuario cocinero con is_active, intenta obtener el usuario con el last_login_at más reciente
                if usuario_cocinero is None:
                    usuario_cocinero = (
                        Usuario.query.join(asignacion_rol_usuario)
                        .join(Rol)
                        .filter(Rol.id == rol_cocinero.id)
                        .order_by(desc("last_login_at"))
                        .first()
                    )

                if usuario_cocinero is not None:
                    usuario_cocinero = usuario_cocinero.id
                else:
                    # Maneja el caso en que no se encuentre ningún usuario cocinero
                    usuario_cocinero = current_user.id

            solicitud = SolicitudProduccion(
                idReceta=form.receta.data,
                idUsuarioSolicitud=current_user.id,
                idUsuarioProduccion=usuario_cocinero,
                tandas=form.tandas.data,
                estatus=1,
            )

            db.session.add(solicitud)
            db.session.commit()

            flash("Solicitud de producción creada correctamente", "success")

            return redirect(url_for("venta.solicitud_produccion"))
        else:
            return render_template(
                "modulos/venta/solicitudesProduccion/create.html",
                form=form,
                images=images,
                nuevo=True,
            )


@venta.route("/solicitud_produccion/edit/<int:id>", methods=["GET", "POST"])
@requires_role("vendedor")
def edit_solicitud_produccion(id):
    solicitud = SolicitudProduccion.query.get(id)

    form = forms.ModificarSolicitudProduccionForm(request.form)

    if request.method == "POST" and form.validate():
        solicitud = SolicitudProduccion.query.get(id)
        solicitud.tandas = form.tandas.data
        solicitud.fecha_solicitud = form.fecha_solicitud.data
        db.session.commit()

        flash("Solicitud de producción modificada correctamente", "success")

        return redirect(url_for("venta.solicitud_produccion"))

    return render_template(
        "modulos/venta/solicitudesProduccion/edit.html", form=form, solicitud=solicitud
    )


@venta.route("/solicitud_produccion/delete", methods=["POST"])
@requires_role("vendedor")
def delete_solicitud_produccion():
    id = request.form.get("id")
    solicitud = SolicitudProduccion.query.get_or_404(id)
    db.session.delete(solicitud)
    db.session.commit()
    flash("Solicitud de producción eliminada correctamente", "success")
    return redirect(url_for("venta.solicitud_produccion"))


@venta.route("/almacen/galletas", methods=["GET", "POST"])
def lotes_galletas():
    form = forms.BusquedaLoteGalletaForm(request.form)

    form.receta.choices = [(0, "Todas las recetas")] + [
        (receta.id, receta.nombre) for receta in Receta.query.all()
    ]

    if request.method == "POST" and form.validate():
        fecha_inicio = form.fecha_inicio.data
        fecha_fin = form.fecha_fin.data
        receta = form.receta.data
        lotes = []

        base_query = (
            db.session.query(LoteGalleta, Receta.nombre, Usuario.nombre)
            .join(Receta, LoteGalleta.idReceta == Receta.id)
            .join(Usuario, LoteGalleta.idUsuarios == Usuario.id)
        )

        if receta == "0":
            lotes = (
                db.session.query(LoteGalleta, Receta.nombre, Usuario.nombre)
                .join(Receta, LoteGalleta.idReceta == Receta.id)
                .join(Usuario, LoteGalleta.idUsuarios == Usuario.id)
                .filter(
                    LoteGalleta.cantidad > 0,
                    LoteGalleta.fecha_entrada >= fecha_inicio,
                    LoteGalleta.fecha_entrada <= fecha_fin,
                )
                .all()
            )
        else:
            lotes = (
                db.session.query(LoteGalleta, Receta.nombre, Usuario.nombre)
                .join(Receta, LoteGalleta.idReceta == Receta.id)
                .join(Usuario, LoteGalleta.idUsuarios == Usuario.id)
                .filter(
                    LoteGalleta.cantidad > 0,
                    LoteGalleta.fecha_entrada >= fecha_inicio,
                    LoteGalleta.fecha_entrada <= fecha_fin,
                    LoteGalleta.idReceta == receta,
                )
                .all()
            )

        return render_template(
            "modulos/venta/galletas.html", form=form, lotes=lotes, lista=True
        )

    lotes = (
        db.session.query(LoteGalleta, Receta.nombre, Usuario.nombre)
        .join(Receta, LoteGalleta.idReceta == Receta.id)
        .join(Usuario, LoteGalleta.idUsuarios == Usuario.id)
        .filter(LoteGalleta.cantidad > 0)
        .all()
    )

    return render_template(
        "modulos/venta/galletas.html", form=form, lotes=lotes, lista=True
    )


@venta.route("/merma/galletas/<int:id>", methods=["GET", "POST"])
def merma_galletas(id):
    form = forms.MermaGalletaForm(request.form)
    form.lot_id.data = id

    lote = LoteGalleta.query.get(id)

    cantidad_maxima = lote.cantidad

    receta = Receta.query.get(lote.idReceta)
    peso_pieza = receta.peso_estimado

    if request.method == "POST" and form.validate():
        tipo_medida = form.tipo_medida.data
        cantidad = form.cantidad.data

        id = form.lot_id.data

        if tipo_medida == "g":
            cantidad = cantidad / 1000
            cantidad = math.ceil(cantidad / peso_pieza)
        if cantidad > lote.cantidad:
            flash(
                "La cantidad de piezas a merma no puede ser mayor a la cantidad de piezas en el lote",
                "error",
            )
            return render_template(
                "modulos/venta/galletas.html",
                form=form,
                cantidad_maxima=cantidad_maxima,
                peso_pieza=peso_pieza,
                imagen=receta.imagen,
            )

        lote.cantidad -= cantidad
        lote.merma += cantidad
        db.session.commit()
        flash("Merma registrada correctamente", "success")
        return redirect(url_for("venta.lotes_galletas"))

    return render_template(
        "modulos/venta/galletas.html",
        form=form,
        cantidad_maxima=cantidad_maxima,
        peso_pieza=peso_pieza,
        imagen=receta.imagen,
    )


@venta.route("/compras/ver", methods=["GET"])
@requires_role("vendedor")
def compras_ver():
    form = forms.BusquedaCompra(request.args)
    form.insumo.choices = [(0, "Todos los insumos")] + [
        (insumo.id, insumo.nombre) for insumo in Insumo.query.all()
    ]
    compras = (
        db.session.query(Compra)
        .join(Usuario, Compra.idUsuario == Usuario.id)
        .join(Proveedor, Compra.idProveedores == Proveedor.id)
        .with_entities(Compra, Usuario.nombre, Proveedor.empresa)
        .all()
    )
    for compra, usuario, proveedor in compras:

        lotes = (
            db.session.query(LoteInsumo, Insumo)
            .join(Insumo, LoteInsumo.idInsumo == Insumo.id)
            .filter(LoteInsumo.idCompra == compra.id)
            .all()
        )

        compra.insumos = ", ".join([lote.insumo.nombre for lote in lotes])
        compra.caja = True if compra.idTransaccionCaja else False

    return render_template("modulos/venta/compras/ver.html", compras=compras, form=form)


@venta.route("/compras/nueva", methods=["GET", "POST"])
@requires_role("vendedor")
def compras_crear():
    form = forms.NuevaCompraForm(request.form)
    form.proveedores.choices = [
        (proveedor.id, proveedor.empresa) for proveedor in Proveedor.query.all()
    ]

    insumos_choices = [(insumo.id, insumo.nombre) for insumo in Insumo.query.all()]

    for lote_insumo_form in form.lotes_insumos:
        lote_insumo_form.insumos.choices = insumos_choices

    if request.method == "POST" and form.validate():

        compra = Compra(
            idUsuario=current_user.id,
            idProveedores=form.proveedores.data,
            fecha_compra=datetime.now(),
            pago_proveedor=sum([lote.costo_lote.data for lote in form.lotes_insumos]),
        )
        if form.caja.data:
            compra.idTransaccionCaja = form.caja.data

        db.session.add(compra)
        db.session.commit()

        for lote_insumo_form in form.lotes_insumos:
            lote_insumo = LoteInsumo(
                idCompra=compra.id,
                idInsumo=lote_insumo_form.insumos.data,
                cantidad=lote_insumo_form.cantidad.data,
                fecha_caducidad=lote_insumo_form.fecha_caducidad.data,
                precio_unidad=lote_insumo_form.costo_lote.data
                / lote_insumo_form.cantidad.data,
            )
            db.session.add(lote_insumo)

        db.session.commit()

        flash("Compra registrada correctamente", "success")
        return redirect(url_for("venta.compras_ver"))

    return render_template("modulos/venta/compras/crear.html", form=form)


@venta.route("/compras/editar/<int:id>", methods=["GET", "POST"])
@requires_role("vendedor")
def compras_editar(id):
    form = forms.NuevaCompraForm(request.form)
    form.proveedores.choices = [
        (proveedor.id, proveedor.empresa) for proveedor in Proveedor.query.all()
    ]

    if request.method == "POST" and form.validate():
        compra = Compra(
            idUsuario=current_user.id,
            idProveedores=form.proveedores.data,
            fecha_compra=datetime.now(),
            pago_proveedor=99.99,
        )
        if form.caja.data:
            compra.idTransaccionCaja = form.caja.data

        db.session.add(compra)
        db.session.commit()

        flash("Compra registrada correctamente", "success")
        return redirect(url_for("venta.compras_ver"))

    return render_template("modulos/venta/compras/crear.html", form=form)
