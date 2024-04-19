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
    send_file,
    url_for,
)
from flask_login import current_user, login_required
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import asc, desc, extract, func, text
from sqlalchemy.orm import joinedload

from configu.config import DevelopmentConfig
from database.models import (
    Compra,
    CorteCaja,
    DetalleVenta,
    Insumo,
    InsumosReceta,
    LoteGalleta,
    LoteInsumo,
    Proveedor,
    Receta,
    RecetaLoteInsumo,
    Rol,
    SolicitudProduccion,
    TransaccionCaja,
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
    solicitudes = (
        SolicitudProduccion.query.filter(SolicitudProduccion.estatus != 4)
        .options(
            joinedload(SolicitudProduccion.receta),
            joinedload(SolicitudProduccion.usuarioSolicitud),
            joinedload(SolicitudProduccion.usuarioProduccion),
        )
        .all()
    )

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

            db.session.add(solicitud)

            if len(insumosReceta) > 0:
                recetaSePuedeProcesar = True
                mensajeInsumosCantidadesFaltantes = ""

                for insumoReceta in insumosReceta:
                    lotesInsumosCumplenCantidad = True

                    cantidadNecesaria = insumoReceta.cantidad * form.tandas.data

                    lotesInsumosReceta = (
                        LoteInsumo.query.filter_by(idInsumo=insumoReceta.idInsumo)
                        .order_by(asc(LoteInsumo.fecha_caducidad))
                        .all()
                    )

                    if len(lotesInsumosReceta) > 0:
                        for loteInsumo in lotesInsumosReceta:
                            if loteInsumo.cantidad >= cantidadNecesaria:
                                recetaLoteInsumo = RecetaLoteInsumo(
                                    idSolicitud=solicitud.id,
                                    idReceta=form.receta.data,
                                    idLoteInsumo=loteInsumo.id,
                                    cantidad=cantidadNecesaria,
                                )

                                db.session.add(recetaLoteInsumo)

                                loteInsumo.cantidad -= cantidadNecesaria
                                cantidadNecesaria = 0

                                break
                            else:
                                recetaLoteInsumo = RecetaLoteInsumo(
                                    idSolicitud=solicitud.id,
                                    idReceta=form.receta.data,
                                    idLoteInsumo=loteInsumo.id,
                                    cantidad=loteInsumo.cantidad,
                                )

                                db.session.add(recetaLoteInsumo)

                                cantidadNecesaria -= loteInsumo.cantidad
                                loteInsumo.cantidad = 0

                        if cantidadNecesaria != 0:
                            recetaSePuedeProcesar = False

                            if insumoReceta.insumo.unidad_medida == "Kilos":
                                if cantidadNecesaria >= 1:
                                    unidadMedida = "kg"
                                    cantidadFormateada = cantidadNecesaria
                                else:
                                    unidadMedida = "g"
                                    cantidadFormateada = cantidadNecesaria * 1000

                            elif insumoReceta.insumo.unidad_medida == "Litros":
                                if cantidadNecesaria >= 1:
                                    unidadMedida = "l"
                                    cantidadFormateada = cantidadNecesaria
                                else:
                                    unidadMedida = "ml"
                                    cantidadFormateada = cantidadNecesaria * 1000

                            mensajeInsumosCantidadesFaltantes += f"No cuentas con {cantidadFormateada:.2f} {unidadMedida} del insumo {insumoReceta.insumo.nombre}\n"
                    else:
                        recetaSePuedeProcesar = False

                        if insumoReceta.insumo.unidad_medida == "Kilos":
                            if cantidadNecesaria >= 1:
                                unidadMedida = "kg"
                                cantidadFormateada = cantidadNecesaria
                            else:
                                unidadMedida = "g"
                                cantidadFormateada = cantidadNecesaria * 1000
                        elif insumoReceta.insumo.unidad_medida == "Litros":
                            if cantidadNecesaria >= 1:
                                unidadMedida = "l"
                                cantidadFormateada = cantidadNecesaria
                            else:
                                unidadMedida = "ml"
                                cantidadFormateada = cantidadNecesaria * 1000

                        mensajeInsumosCantidadesFaltantes += f"No cuentas con {cantidadFormateada} {unidadMedida} del insumo {insumoReceta.insumo.nombre}\n"

                if not recetaSePuedeProcesar:
                    flash(
                        f"La receta no se puede procesar debido a los siguientes productos faltantes: \n\n{mensajeInsumosCantidadesFaltantes}",
                        "error",
                    )
                    return redirect(url_for("venta.solicitud_produccion_nuevo"))

                # Termina FOR DE INSUMOS

                db.session.commit()

                flash("Solicitud de producción creada correctamente", "success")

                return redirect(url_for("venta.solicitud_produccion"))
            else:
                flash(
                    "Esta receta no cuenta con insumos agregados, consultalo con un administrador",
                    "error",
                )

                return redirect(url_for("venta.solicitud_produccion_nuevo"))
        else:
            return redirect(url_for("venta.solicitud_produccion_nuevo"))


@venta.route("/solicitud_produccion/aceptar/<int:id>", methods=["POST"])
@requires_role("vendedor")
def aceptar_solicitud_produccion(id):
    solicitud = SolicitudProduccion.query.get(id)

    # agregar el lotes de galletas

    lote = LoteGalleta(
        idReceta=solicitud.idReceta,
        fecha_entrada=datetime.now(),
        tipo_venta=1,
        cantidad=solicitud.tandas * Receta.query.get(solicitud.idReceta).piezas,
        idProduccion=solicitud.id,
        idUsuarios=current_user.id,
    )
    db.session.add(lote)

    solicitud = SolicitudProduccion.query.get(id)
    solicitud.estatus = 4
    db.session.commit()

    flash("El lote se agrego al almacén", "success")

    return redirect(url_for("venta.solicitud_produccion"))


@venta.route("/solicitud_produccion/reintentar/<int:id>", methods=["POST"])
@requires_role("vendedor")
def reintentar_solicitud_produccion(id):
    solicitud = SolicitudProduccion.query.get(id)

    solicitud = SolicitudProduccion.query.get(id)
    solicitud.estatus = 1
    solicitud.fecha_solicitud = datetime.now()
    db.session.commit()

    flash("El lote se agrego al almacén", "success")

    return redirect(url_for("venta.solicitud_produccion"))


@venta.route("/solicitud_produccion/delete", methods=["POST"])
@requires_role("vendedor")
def delete_solicitud_produccion():
    id = request.form.get("id")

    solicitud = SolicitudProduccion.query.get_or_404(id)

    if solicitud.estatus == 1 or solicitud.estatus == 5:
        recetaLotesInsumosDevolver = RecetaLoteInsumo.query.filter_by(
            idSolicitud=solicitud.id
        ).all()

        mensajeDevolver = "Se devolvieron las siguientes cantidades al inventario: \n\n"

        for recetaLoteInsumoDevolver in recetaLotesInsumosDevolver:
            lote_insumo = LoteInsumo.query.get(recetaLoteInsumoDevolver.idLoteInsumo)
            lote_insumo.cantidad += recetaLoteInsumoDevolver.cantidad

            if lote_insumo.insumo.unidad_medida == "Kilos":
                if recetaLoteInsumoDevolver.cantidad >= 1:
                    unidadMedida = "kg"
                    cantidadFormateada = recetaLoteInsumoDevolver.cantidad
                else:
                    unidadMedida = "g"
                    cantidadFormateada = recetaLoteInsumoDevolver.cantidad * 1000
            elif lote_insumo.insumo.unidad_medida == "Litros":
                if recetaLoteInsumoDevolver.cantidad >= 1:
                    unidadMedida = "litros"
                    cantidadFormateada = recetaLoteInsumoDevolver.cantidad
                else:
                    unidadMedida = "ml"
                    cantidadFormateada = recetaLoteInsumoDevolver.cantidad * 1000

            mensajeDevolver += f"{cantidadFormateada} {unidadMedida} al insumo {lote_insumo.insumo.nombre}\n"

            db.session.delete(recetaLoteInsumoDevolver)

        db.session.delete(solicitud)

        db.session.commit()

        flash(
            f"Solicitud de producción eliminada correctamente \n{mensajeDevolver}",
            "receta",
        )

        return redirect(url_for("venta.solicitud_produccion"))
    else:
        flash(
            "La solicitud se encuentra en un status diferente a realizada o rechazada, solicita al cocinero que devuelva la solicitud",
            "info",
        )

        return redirect(url_for("venta.solicitud_produccion"))


@venta.route("/lotes/galletas", methods=["GET", "POST"])
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


@venta.route("/galletas", methods=["GET"])
def lotes_galletas_agrupados():

    galletas = Receta.query.all()

    for galleta in galletas:
        lotes = (
            LoteGalleta.query.filter(
                LoteGalleta.idReceta == galleta.id,
                LoteGalleta.fecha_entrada >= datetime.now().date() - timedelta(days=15),
                LoteGalleta.cantidad > 0,
            )
            .order_by(LoteGalleta.fecha_entrada)
            .all()
        )
        galleta.num_lotes = len(lotes)
        galleta.proxima_caducidad = lotes[0].fecha_entrada if lotes else "No hay lotes"
        galleta.cantidad = sum(lote.cantidad for lote in lotes)

        # agregar flash para los galletas que estan por agotarse
        if galleta.cantidad < 50:
            flash(
                f"(Escacez) Quedan menos de 50 unidades de {galleta.nombre}", "warning"
            )
        # agregar flash para los galletas que sobrepasan la capacidad de almacenamiento
        if galleta.cantidad > 400:
            flash(
                f"(Exceso) Hay más de 400 unidades de {galleta.nombre}",
                "info",
            )
        # agregar flash par los lotes del galleta que estan por caducar en los proximos 3 dias
        for lote in lotes:
            if lote.fecha_entrada <= datetime.now().date() - timedelta(days=12):
                flash(
                    f"(Caducidad) El lote {lote.id} de {galleta.nombre} esta por caducar",
                    "danger",
                )

    return render_template("modulos/venta/galleta_individual.html", galletas=galletas)


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

    if request.method == "POST":

        fecha_inicio_default = datetime.now().date() - timedelta(
            days=365
        )  # Ajusta el valor según sea necesario
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
    efectivo_caja = (
        db.session.query(CorteCaja.monto_final)
        .filter(CorteCaja.fecha_corte == datetime.now().date())
        .first()
    )
    efectivo_caja = efectivo_caja[0] if efectivo_caja else 0

    caja = (
        db.session.query(CorteCaja)
        .filter(CorteCaja.fecha_corte == datetime.now().date())
        .first()
    )

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
            transaccion = TransaccionCaja(
                monto_egreso=-compra.pago_proveedor,
                fecha_transaccion=datetime.now(),
                idCorteCaja=caja.id,
            )
            db.session.add(transaccion)
            db.session.commit()

            caja.monto_final -= float(compra.pago_proveedor)

            compra.idTransaccionCaja = transaccion.id

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
        "modulos/venta/compras/crear.html",
        form=form,
        insumos=insumos_choices,
        efectivo_caja=efectivo_caja,
    )


carrito = []


@venta.route("/punto_venta", methods=["GET"])
@requires_role("vendedor")
def punto_venta():
    form = forms.busquedaRecetaPuntoVenta(request.form)
    form2 = forms.agregarProductoPuntoVenta(request.form)
    form_devolucion = forms.devolucionForm(request.form)
    # galletas debe contener elnombre de la receta, id, cantidad de stock, imagen
    galletas = db.session.query(Receta).filter(Receta.estatus == 1).all()

    # saber el efectivo en caja en corte caja
    efectivo_caja = (
        db.session.query(CorteCaja.monto_final)
        .filter(CorteCaja.fecha_corte == datetime.now().date())
        .first()
    )
    efectivo_caja = efectivo_caja[0] if efectivo_caja else 0

    for galleta in galletas:
        galleta.stock = (
            db.session.query(func.sum(LoteGalleta.cantidad))
            .filter(LoteGalleta.cantidad > 0, LoteGalleta.idReceta == galleta.id)
            .scalar()
        )
        if not galleta.stock:
            galleta.stock = 0
        galleta.imagen = galleta.imagen if galleta.imagen else "galleta 1.png"

    total = sum([item["subtotal"] for item in carrito])

    return render_template(
        "modulos/venta/punto-venta.html",
        galletas=galletas,
        form_busqueda=form,
        form=form2,
        carrito=carrito,
        total=total,
        form_devolucion=form_devolucion,
        efectivo_caja=efectivo_caja,
    )


@venta.route("/punto_venta/caja", methods=["GET", "POST"])
@requires_role("vendedor")
def punto_venta_devolucion():
    form_devolucion = forms.devolucionForm(request.form)
    # saber el efectivo en caja en corte caja
    if form_devolucion.validate():
        caja = (
            db.session.query(CorteCaja)
            .filter(CorteCaja.fecha_corte == datetime.now().date())
            .first()
        )
        caja.monto_final -= float(form_devolucion.cantidad.data)

        db.session.commit()

    return redirect(url_for("venta.punto_venta"))


@venta.route("/punto_venta/buscar", methods=["POST"])
@requires_role("vendedor")
def punto_venta_buscar():
    form_devolucion = forms.devolucionForm(request.form)
    form = forms.busquedaRecetaPuntoVenta(request.form)
    form2 = forms.agregarProductoPuntoVenta(request.form)

    efectivo_caja = (
        db.session.query(CorteCaja.monto_final)
        .filter(CorteCaja.fecha_corte == datetime.now().date())
        .first()
    )
    efectivo_caja = efectivo_caja[0] if efectivo_caja else 0

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
            if not galleta.stock:
                galleta.stock = 0
            galleta.imagen = galleta.imagen if galleta.imagen else "galleta 1.png"

        total = sum([item["subtotal"] for item in carrito])

        return render_template(
            "modulos/venta/punto-venta.html",
            galletas=galletas,
            form_busqueda=form,
            form=form2,
            total=total,
            carrito=carrito,
            efectivo_caja=efectivo_caja,
            form_devolucion=form_devolucion,
        )

    total = sum([item["subtotal"] for item in carrito])

    galletas = db.session.query(Receta).filter(Receta.estatus == 1).all()
    for galleta in galletas:
        galleta.stock = (
            db.session.query(func.sum(LoteGalleta.cantidad))
            .filter(LoteGalleta.cantidad > 0, LoteGalleta.idReceta == galleta.id)
            .scalar()
        )
        if not galleta.stock:
            galleta.stock = 0

        galleta.imagen = galleta.imagen if galleta.imagen else "galleta 1.png"

    return render_template(
        "modulos/venta/punto-venta.html",
        galletas=galletas,
        form_busqueda=form,
        form=form2,
        carrito=carrito,
        efectivo_caja=efectivo_caja,
        form_devolucion=form_devolucion,
    )


@venta.route("/punto_venta/agregar", methods=["POST"])
@requires_role("vendedor")
def punto_venta_agregar():
    form = forms.busquedaRecetaPuntoVenta(request.form)
    form2 = forms.agregarProductoPuntoVenta(request.form)
    form_devolucion = forms.devolucionForm()
    # galletas debe contener elnombre de la receta, id, cantidad de stock, imagen

    efectivo_caja = (
        db.session.query(CorteCaja.monto_final)
        .filter(CorteCaja.fecha_corte == datetime.now().date())
        .first()
    )
    efectivo_caja = efectivo_caja[0] if efectivo_caja else 0

    galletas = db.session.query(Receta).filter(Receta.estatus == 1).all()
    for galleta in galletas:
        galleta.stock = (
            db.session.query(func.sum(LoteGalleta.cantidad))
            .filter(LoteGalleta.cantidad > 0, LoteGalleta.idReceta == galleta.id)
            .scalar()
        )

        if not galleta.stock:
            galleta.stock = 0

        galleta.imagen = galleta.imagen if galleta.imagen else "galleta 1.png"

    if form2.validate():
        idReceta = form2.id.data
        cantidad = form2.cantidad.data

        receta = Receta.query.get(idReceta)

        # Sumar las cantidades de la receta en el carrito
        cantidad_en_carrito = sum(
            item["cantidad"] for item in carrito if item["idReceta"] == idReceta
        )
        # Buscar la receta específica en la lista de galletas para obtener su stock
        galleta_en_carrito = next(
            (
                item
                for item in galletas
                if item.id == int(idReceta) and item.stock is not None
            ),
            0,
        )
        if (
            galleta_en_carrito
            and cantidad_en_carrito + cantidad <= galleta_en_carrito.stock
        ):
            carrito.append(
                {
                    "idCarrito": len(carrito) + 1,
                    "idReceta": idReceta,
                    "nombre": receta.nombre,
                    "cantidad": cantidad,
                    "precio_unidad": receta.utilidad,
                    "subtotal": receta.utilidad * cantidad,
                }
            )
            # Aquí puedes manejar el caso de éxito, por ejemplo, redirigiendo al usuario o mostrando un mensaje
        else:
            flash(
                f"La cantidad solicitada de {receta.nombre} excede la cantidad disponible en stock.",
                "info",
            )
        form2 = forms.agregarProductoPuntoVenta()

    total = sum([item["subtotal"] for item in carrito])

    return render_template(
        "modulos/venta/punto-venta.html",
        galletas=galletas,
        form_busqueda=form,
        form=form2,
        carrito=carrito,
        total=total,
        efectivo_caja=efectivo_caja,
        form_devolucion=form_devolucion,
    )


@venta.route("/punto_venta/eliminar/<int:id>", methods=["POST"])
@requires_role("vendedor")
def punto_venta_eliminar(id):
    form = forms.busquedaRecetaPuntoVenta(request.form)
    form2 = forms.agregarProductoPuntoVenta(request.form)
    form_devolucion = forms.devolucionForm(request.form)

    efectivo_caja = (
        db.session.query(CorteCaja.monto_final)
        .filter(CorteCaja.fecha_corte == datetime.now().date())
        .first()
    )
    efectivo_caja = efectivo_caja[0] if efectivo_caja else 0
    # galletas debe contener elnombre de la receta, id, cantidad de stock, imagen
    galletas = db.session.query(Receta).filter(Receta.estatus == 1).all()
    global carrito
    carrito = [item for item in carrito if item["idCarrito"] != id]

    for galleta in galletas:
        galleta.stock = (
            db.session.query(func.sum(LoteGalleta.cantidad))
            .filter(LoteGalleta.cantidad > 0, LoteGalleta.idReceta == galleta.id)
            .scalar()
        )
        if not galleta.stock:
            galleta.stock = 0

        galleta.imagen = galleta.imagen if galleta.imagen else "galleta 1.png"

    total = sum([item["subtotal"] for item in carrito])

    return render_template(
        "modulos/venta/punto-venta.html",
        galletas=galletas,
        form_busqueda=form,
        form=form2,
        carrito=carrito,
        total=total,
        efectivo_caja=efectivo_caja,
        form_devolucion=form_devolucion,
    )


@venta.route("/punto_venta/cancelar", methods=["POST"])
@requires_role("vendedor")
def punto_venta_cancelar():
    form = forms.busquedaRecetaPuntoVenta(request.form)
    form2 = forms.agregarProductoPuntoVenta(request.form)
    form_devolucion = forms.devolucionForm(request.form)

    efectivo_caja = (
        db.session.query(CorteCaja.monto_final)
        .filter(CorteCaja.fecha_corte == datetime.now().date())
        .first()
    )
    efectivo_caja = efectivo_caja[0] if efectivo_caja else 0
    # galletas debe contener elnombre de la receta, id, cantidad de stock, imagen
    galletas = db.session.query(Receta).filter(Receta.estatus == 1).all()
    for galleta in galletas:
        galleta.stock = (
            db.session.query(func.sum(LoteGalleta.cantidad))
            .filter(LoteGalleta.cantidad > 0, LoteGalleta.idReceta == galleta.id)
            .scalar()
        )
        if not galleta.stock:
            galleta.stock = 0

        galleta.imagen = galleta.imagen if galleta.imagen else "galleta 1.png"

    global carrito
    carrito = []

    total = sum([item["subtotal"] for item in carrito])

    return render_template(
        "modulos/venta/punto-venta.html",
        galletas=galletas,
        form_busqueda=form,
        form=form2,
        carrito=carrito,
        total=total,
        efectivo_caja=efectivo_caja,
        form_devolucion=form_devolucion,
    )


@venta.route("/punto_venta/confirmar", methods=["POST"])
@requires_role("vendedor")
def punto_venta_confirmar():
    # galletas debe contener elnombre de la receta, id, cantidad de stock, imagen

    global carrito
    total = sum([item["subtotal"] for item in carrito])

    galletas = db.session.query(Receta).filter(Receta.estatus == 1).all()
    for galleta in galletas:
        galleta.stock = (
            db.session.query(func.sum(LoteGalleta.cantidad))
            .filter(LoteGalleta.cantidad > 0, LoteGalleta.idReceta == galleta.id)
            .scalar()
        )
        if not galleta.stock:
            galleta.stock = 0

        galleta.imagen = galleta.imagen if galleta.imagen else "galleta 1.png"

    corte_de_hoy = CorteCaja.query.filter_by(fecha_corte=datetime.now().date()).first()

    transaccion = TransaccionCaja(
        monto_ingreso=total,
        idCorteCaja=corte_de_hoy.id,
        fecha_transaccion=datetime.now(),
    )

    db.session.add(transaccion)
    db.session.commit()

    venta = Venta(
        idUsuario=current_user.id,
        idTransaccionCaja=transaccion.id,
        fecha_venta=datetime.now(),
        total_venta=sum([item["subtotal"] for item in carrito]),
    )
    db.session.add(venta)
    db.session.commit()

    # buscar cada elemento del carrito y restar la cantidad en el lote con la fecha de caducidad mas próxima, si el lote no tiene suficiente cantidad, se debe de buscar otro lote
    for item in carrito:
        receta = Receta.query.get(item["idReceta"])

        while item["cantidad"] > 0:
            lote = (
                LoteGalleta.query.filter(
                    LoteGalleta.idReceta == receta.id, LoteGalleta.cantidad > 0
                )
                .order_by(LoteGalleta.fecha_entrada)
                .first()
            )
            if lote.cantidad >= item["cantidad"]:
                lote.cantidad -= item["cantidad"]

                detalle = DetalleVenta(
                    idVenta=venta.id,
                    idStock=lote.id,
                    cantidad=item["cantidad"],
                    precio=item["precio_unidad"],
                )
                db.session.add(detalle)
                item["cantidad"] = 0

            else:
                item["cantidad"] -= lote.cantidad

                detalle = DetalleVenta(
                    idVenta=venta.id,
                    idStock=lote.id,
                    cantidad=lote.cantidad,
                    precio=item["precio_unidad"],
                )
                db.session.add(lote)
                lote.cantidad = 0
            db.session.commit()
    carrito = []
    caja = (
        db.session.query(CorteCaja)
        .filter(CorteCaja.fecha_corte == datetime.now().date())
        .first()
    )
    caja.monto_final += total
    db.session.commit()
    flash("Venta registrada correctamente", "success")

    return redirect(url_for("venta.punto_venta"))
