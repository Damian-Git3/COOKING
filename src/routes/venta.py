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
    InsumosReceta,
    LoteInsumo
)

from forms import forms
from sqlalchemy.orm import joinedload
from sqlalchemy import desc, extract, text, asc
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
    recetas = [(receta.id, receta.imagen, receta.piezas) for receta in Receta.query.all()]

    if request.method == "GET":
        return render_template(
            "modulos/venta/solicitudesProduccion/create.html",
            form=form,
            nuevo=True,
            recetas=recetas
        )
    else:
        if form.validate():
            insumosReceta = InsumosReceta.query.filter_by(idReceta=form.receta.data).all()
            
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
                    
                    lotesInsumosReceta = LoteInsumo.query.filter_by(idInsumo=insumoReceta.idInsumo).order_by(asc(LoteInsumo.fecha_caducidad)).all()
                    
                    print(f"Cantidad de lotes insumos para este insumo: {len(lotesInsumosReceta)}")
                    
                    if(len(lotesInsumosReceta) > 0):
                        recetaSePuedeProcesar = False
                        
                        for loteInsumo in lotesInsumosReceta:
                            print("----------------------")
                            print(f"Lote insumo: {loteInsumo.cantidad}")
                            
                            if loteInsumo.cantidad <= cantidadNecesaria:
                                pass
                            else:
                                pass
                    else:
                        recetaSePuedeProcesar = False
                        
                        if(insumoReceta.insumo.unidad_medida == "Kilos"):
                            if (cantidadNecesaria >= 1):
                                unidadMedida = "kg"
                                
                                cantidadFormateada = cantidadNecesaria
                            else:
                                unidadMedida = "g"
                                
                                cantidadFormateada = cantidadNecesaria*1000
                        elif(insumoReceta.insumo.unidad_medida == "Litros"):
                            if (cantidadNecesaria >= 1):
                                unidadMedida = "l"
                                
                                cantidadFormateada = cantidadNecesaria
                            else:
                                unidadMedida = "ml"
                                
                                cantidadFormateada = cantidadNecesaria*1000
                        
                        mensajeInsumosCantidadesFaltantes += f"No cuentas con {cantidadFormateada} {unidadMedida} del insumo {insumoReceta.insumo.nombre}\n"
                
                if not recetaSePuedeProcesar:
                    flash(f"La receta no se puede procesar debido a los siguientes productos faltantes: \n\n{mensajeInsumosCantidadesFaltantes}", "receta-error")
                    return redirect(url_for("venta.solicitud_produccion_nuevo"))
                
                #Termina FOR DE INSUMOS
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

                #db.session.add(solicitud)
                #db.session.commit()

                flash("Solicitud de producción creada correctamente", "success")

                return redirect(url_for("venta.solicitud_produccion"))
            else:
                flash("Esta receta no cuenta con insumos agregados, consultalo con un administrador", "error")
                
                return redirect(url_for("venta.solicitud_produccion_nuevo"))
        else:
            return redirect(url_for("venta.solicitud_produccion_nuevo"))

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
    
    if (solicitud.estatus == 1):
        db.session.delete(solicitud)
        db.session.commit()
        flash("Solicitud de producción eliminada correctamente", "success")
        
        return redirect(url_for("venta.solicitud_produccion"))
    else:
        flash("La solicitud se encuentra en un status diferente a realizada, solicita al cocinero que descienda los status para poder eliminarla", "error")
        
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
        print(fecha_inicio, fecha_fin, receta)
        if receta == 0:
            lotes = base_query.filter(
                LoteGalleta.fecha_entrada >= fecha_inicio,
                LoteGalleta.fecha_entrada <= fecha_fin,
                LoteGalleta.cantidad > 0,
            ).all()
        else:
            lotes = base_query.filter(
                LoteGalleta.fecha_entrada >= fecha_inicio,
                LoteGalleta.fecha_entrada <= fecha_fin,
                LoteGalleta.idReceta == receta,
                LoteGalleta.cantidad > 0,
            ).all()

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


@venta.route("/merma/galletas", methods=["GET", "POST"])
def merma_galletas():
    form = forms.MermaGalletaForm(request.form)
    if form.validate():
        tipo_medida = form.tipo_medida.data
        cantidad = form.cantidad.data

    return redirect(url_for("venta.lotes_galletas"))
