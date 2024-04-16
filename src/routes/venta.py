import math
from datetime import datetime, timedelta

from flask import (
    Blueprint,
    Flask,
    Response,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import asc, desc, extract, func, text
from sqlalchemy.orm import joinedload

from configu.config import DevelopmentConfig
from database.models import (
    Compra,
    DetalleVenta,
    Insumo,
    InsumosReceta,
    LoteGalleta,
    LoteInsumo,
    Proveedor,
    Receta,
    Rol,
    SolicitudProduccion,
    Usuario,
    Venta,
    asignacion_rol_usuario,
    db,
)
from forms import forms
from routes.auth import requires_role

venta = Blueprint("venta", __name__, url_prefix="/venta")


@venta.route("/compras")
@requires_role("vendedor")
def compras():
    return render_template("modulos/venta/compras.html")


@venta.route("/solicitud_produccion")
@requires_role("vendedor")
def solicitud_produccion():
    solicitudes = SolicitudProduccion.query.options(
        joinedload(SolicitudProduccion.receta),
        joinedload(SolicitudProduccion.usuarioSolicitud),
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
    recetas = [
        (receta.id, receta.imagen, receta.piezas) for receta in Receta.query.all()
    ]

    if request.method == "GET":
        return render_template(
            "modulos/venta/solicitudesProduccion/create.html",
            form=form,
            nuevo=True,
            recetas=recetas,
        )
    else:
        if form.validate():
            insumosReceta = InsumosReceta.query.filter_by(
                idReceta=form.receta.data
            ).all()

            if len(insumosReceta) > 0:
                recetaSePuedeProcesar = True
                mensajeInsumosCantidadesFaltantes = ""

                for insumoReceta in insumosReceta:
                    lotesInsumosCumplenCantidad = True

                    cantidadNecesaria = insumoReceta.cantidad * form.tandas.data

                    print("----------------------")
                    print(f"Insumo: {insumoReceta.insumo.nombre}")
                    print(f"Insumo cantidad en receta: {insumoReceta.cantidad}")
                    print(f"Tandas: {form.tandas.data}")
                    print(f"Cantidad necesaria: {cantidadNecesaria}")

                    lotesInsumosReceta = (
                        LoteInsumo.query.filter_by(idInsumo=insumoReceta.idInsumo)
                        .order_by(asc(LoteInsumo.fecha_caducidad))
                        .all()
                    )

                    print(
                        f"Cantidad de lotes insumos para este insumo: {len(lotesInsumosReceta)}"
                    )

                    if len(lotesInsumosReceta) > 0:
                        recetaSePuedeProcesar = False

                        for loteInsumo in lotesInsumosReceta:
                            print("----------------------")
                            print(f"Lote insumo: {loteInsumo.cantidad}")

                            if loteInsumo.cantidad <= cantidadNecesaria:
                                pass
                            else:
                                pass
                    else:
                        if insumoReceta.insumo.unidad_medida == "Kilos":
                            if cantidadNecesaria >= 1:
                                unidadMedida = "kg"
                            else:
                                unidadMedida = "g"
                                cantidadNecesaria * 1000
                        elif insumoReceta.insumo.unidad_medida == "Litros":
                            if cantidadNecesaria >= 1:
                                unidadMedida = "l"
                            else:
                                unidadMedida = "ml"
                                cantidadNecesaria * 1000

                        mensajeInsumosCantidadesFaltantes += f"No cuentas con {cantidadNecesaria} {unidadMedida} del insumo {insumoReceta.insumo.nombre}\n"
                        print(mensajeInsumosCantidadesFaltantes)

                # Termina FOR DE INSUMOS
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
                        usuario_cocinero = current_user.id

                solicitud = SolicitudProduccion(
                    idReceta=form.receta.data,
                    idUsuarioSolicitud=current_user.id,
                    idUsuarioProduccion=usuario_cocinero,
                    tandas=form.tandas.data,
                    estatus=1,
                )

                # db.session.add(solicitud)
                # db.session.commit()

                flash("Solicitud de producción creada correctamente", "success")

                return redirect(url_for("venta.solicitud_produccion"))
            else:
                flash(
                    "Esta receta no cuenta con insumos agregados, consultalo con un administrador",
                    "error",
                )

                return render_template(
                    "modulos/venta/solicitudesProduccion/create.html",
                    form=form,
                    recetas=recetas,
                    nuevo=True,
                )
        else:
            return render_template(
                "modulos/venta/solicitudesProduccion/create.html",
                form=form,
                recetas=recetas,
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

    if solicitud.estatus == 1:
        db.session.delete(solicitud)
        db.session.commit()
        flash("Solicitud de producción eliminada correctamente", "success")

        return redirect(url_for("venta.solicitud_produccion"))
    else:
        flash(
            "La solicitud se encuentra en un status diferente a realizada, solicita al cocinero que descienda los status para poder eliminarla",
            "error",
        )

        return redirect(url_for("venta.solicitud_produccion"))


@venta.route("/almacen/galletas", methods=["GET", "POST"])
@requires_role("vendedor")
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
@requires_role("vendedor")
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


@venta.route("/compras/ver", methods=["GET", "POST"])
@requires_role("vendedor")
def compras_ver():
    form = forms.BusquedaCompra(request.form)
    form.insumo.choices = [(0, "Todos los insumos")] + [
        (insumo.id, insumo.nombre) for insumo in Insumo.query.all()
    ]

    if request.method == "POST" and form.validate():
        fecha_inicio = form.fecha_inicio.data
        fecha_fin = form.fecha_fin.data
        insumo = form.insumo.data
        lotes = []

        if insumo == "0":

            compras = (
                db.session.query(Compra)
                .join(Usuario, Compra.idUsuario == Usuario.id)
                .join(Proveedor, Compra.idProveedores == Proveedor.id)
                .with_entities(Compra, Usuario.nombre, Proveedor.empresa)
                .filter(
                    Compra.fecha_compra >= fecha_inicio,
                    Compra.fecha_compra <= fecha_fin,
                )
                .order_by(Compra.fecha_compra.desc())
                .all()
            )
        else:
            compras = (
                db.session.query(Compra)
                .join(Usuario, Compra.idUsuario == Usuario.id)
                .join(Proveedor, Compra.idProveedores == Proveedor.id)
                .join(LoteInsumo, LoteInsumo.idCompra == Compra.id)
                .with_entities(Compra, Usuario.nombre, Proveedor.empresa)
                .filter(
                    LoteInsumo.idInsumo == insumo,
                    Compra.fecha_compra >= fecha_inicio,
                    Compra.fecha_compra <= fecha_fin,
                )
                .order_by(Compra.fecha_compra.desc())
                .all()
            )
        for compra, usuario, proveedor in compras:

            lotes = (
                db.session.query(LoteInsumo, Insumo)
                .join(Insumo, LoteInsumo.idInsumo == Insumo.id)
                .filter(LoteInsumo.idCompra == compra.id)
                .all()
            )

            compra.insumos = ", ".join([lote.nombre for loteInsumo, lote in lotes])
            compra.caja = True if compra.idTransaccionCaja else False

        return render_template(
            "modulos/venta/compras/ver.html", compras=compras, form=form
        )

    compras = (
        db.session.query(Compra)
        .join(Usuario, Compra.idUsuario == Usuario.id)
        .join(Proveedor, Compra.idProveedores == Proveedor.id)
        .with_entities(Compra, Usuario.nombre, Proveedor.empresa)
        .order_by(Compra.fecha_compra.desc())
        .all()
    )
    for compra, usuario, proveedor in compras:

        lotes = (
            db.session.query(LoteInsumo, Insumo)
            .join(Insumo, LoteInsumo.idInsumo == Insumo.id)
            .filter(LoteInsumo.idCompra == compra.id)
            .all()
        )

        compra.insumos = ", ".join([lote.nombre for loteInsumo, lote in lotes])
        compra.caja = True if compra.idTransaccionCaja else False

    return render_template("modulos/venta/compras/ver.html", compras=compras, form=form)


@venta.route("/compras/ver/<int:id>", methods=["GET"])
@requires_role("vendedor")
def compras_ver_detalle(id):
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

        compra.insumos = ", ".join([lote.nombre for loteInsumo, lote in lotes])
        compra.caja = True if compra.idTransaccionCaja else False

    detalles_insumos = (
        db.session.query(LoteInsumo, Insumo)
        .join(Insumo, LoteInsumo.idInsumo == Insumo.id)
        .filter(LoteInsumo.idCompra == id)
        .all()
    )

    return render_template(
        "modulos/venta/compras/ver.html",
        compras=compras,
        form=form,
        detalles_insumos=detalles_insumos,
    )


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
                fecha_compra=datetime.now(),
            )
            db.session.add(lote_insumo)

        db.session.commit()

        flash("Compra registrada correctamente", "success")
        return redirect(url_for("venta.compras_ver"))

    return render_template(
        "modulos/venta/compras/crear.html", form=form, insumos=insumos_choices
    )


@venta.route("/punto_venta", methods=["GET"])
@requires_role("vendedor")
def punto_venta():
    form = forms.busquedaRecetaPuntoVenta(request.form)
    form2 = forms.agregarProductoPuntoVenta(request.form)
    # galletas debe contener elnombre de la receta, id, cantidad de stock, imagen
    galletas = db.session.query(Receta).filter(Receta.estatus == 1).all()
    for galleta in galletas:
        galleta.stock = (
            db.session.query(func.sum(LoteGalleta.cantidad))
            .filter(LoteGalleta.cantidad > 0, LoteGalleta.idReceta == galleta.id)
            .scalar()
        )

        galleta.imagen = galleta.imagen if galleta.imagen else "galleta 1.png"

    return render_template(
        "modulos/venta/punto-venta.html",
        galletas=galletas,
        form_busqueda=form,
        form=form2,
    )


@venta.route("/punto_venta/buscar", methods=["POST"])
@requires_role("vendedor")
def punto_venta_buscar():
    form = forms.busquedaRecetaPuntoVenta(request.form)
    form2 = forms.agregarProductoPuntoVenta(request.form)

    if form.validate():
        galletas = (
            db.session.query(Receta)
            .filter(Receta.estatus == 1, Receta.nombre.like(f"%{form.buscar.data}%"))
            .all()
        )
        for galleta in galletas:
            galleta.stock = (
                db.session.query(func.sum(LoteGalleta.cantidad))
                .filter(LoteGalleta.cantidad > 0, LoteGalleta.idReceta == galleta.id)
                .scalar()
            )

            galleta.imagen = galleta.imagen if galleta.imagen else "galleta 1.png"

        return render_template(
            "modulos/venta/punto-venta.html",
            galletas=galletas,
            form_busqueda=form,
            form=form2,
        )

    galletas = db.session.query(Receta).filter(Receta.estatus == 1).all()
    for galleta in galletas:
        galleta.stock = (
            db.session.query(func.sum(LoteGalleta.cantidad))
            .filter(LoteGalleta.cantidad > 0, LoteGalleta.idReceta == galleta.id)
            .scalar()
        )

        galleta.imagen = galleta.imagen if galleta.imagen else "galleta 1.png"

    return render_template(
        "modulos/venta/punto-venta.html",
        galletas=galletas,
        form_busqueda=form,
        form=form2,
    )


carrito = []


@venta.route("/punto_venta/agregar", methods=["POST"])
@requires_role("vendedor")
def punto_venta_agregar():
    form = forms.busquedaRecetaPuntoVenta(request.form)
    form2 = forms.agregarProductoPuntoVenta(request.form)
    # galletas debe contener elnombre de la receta, id, cantidad de stock, imagen

    if form2.validate():
        idReceta = form2.id.data
        cantidad = form2.cantidad.data

        receta = Receta.query.get(idReceta)

        carrito.append(
            {
                "id": idReceta,
                "nombre": receta.nombre,
                "cantidad": cantidad,
                "precio": receta.utilidad,
                "imagen": receta.imagen,
            }
        )

        flash("Galleta agregada correctamente", "success")

    galletas = db.session.query(Receta).filter(Receta.estatus == 1).all()
    for galleta in galletas:
        galleta.stock = (
            db.session.query(func.sum(LoteGalleta.cantidad))
            .filter(LoteGalleta.cantidad > 0, LoteGalleta.idReceta == galleta.id)
            .scalar()
        )

        galleta.imagen = galleta.imagen if galleta.imagen else "galleta 1.png"

    return render_template(
        "modulos/venta/punto-venta.html",
        galletas=galletas,
        form_busqueda=form,
        form=form2,
    )


@venta.route("/punto_venta/eliminar/<int:id>", methods=["POST"])
@requires_role("vendedor")
def punto_venta_eliminar(id):
    return render_template("modulos/venta/punto-venta.html")


@venta.route("/punto_venta/cancelar", methods=["POST"])
@requires_role("vendedor")
def punto_venta_cancelar():
    return render_template("modulos/venta/punto-venta.html")


@venta.route("/punto_venta/confirmar", methods=["POST"])
@requires_role("vendedor")
def punto_venta_confirmar():
    return render_template("modulos/venta/punto-venta.html")
