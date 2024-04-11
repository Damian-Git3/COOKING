from flask import Blueprint, Flask, request, render_template, Response, redirect, url_for
from flask_login import login_required, current_user

from flask_wtf.csrf import CSRFProtect
from flask import g
from flask import flash, jsonify
from configu.config import DevelopmentConfig
from database.models import db, Usuario, Rol, asignacion_rol_usuario, Insumo, Receta, SolicitudProduccion, Venta, DetalleVenta, Compra, Proveedor, LoteGalleta

from forms import forms
from sqlalchemy.orm import joinedload
from sqlalchemy import desc, extract, text
from datetime import datetime, timedelta

venta = Blueprint('venta', __name__, url_prefix="/venta")


@venta.route('/compras')
@login_required
def compras():
    return render_template('modulos/venta/compras.html')

@venta.route('/punto_venta')
@login_required
def punto_venta():
    return render_template('modulos/venta/punto-venta.html')

@venta.route('/solicitud_produccion')
@login_required
def solicitud_produccion():
    solicitudes = SolicitudProduccion.query.options(
        # Asume que 'receta' es el nombre de la relación en SolicitudProduccion
        joinedload(SolicitudProduccion.receta),
        # Asume que 'usuarioSolicitud' es el nombre de la relación en SolicitudProduccion
        joinedload(SolicitudProduccion.usuarioSolicitud),
        # Asume que 'usuarioProduccion' es el nombre de la relación en SolicitudProduccion
        joinedload(SolicitudProduccion.usuarioProduccion)
    ).all()

    return render_template('modulos/venta/solicitudes-produccion.html', solicitudes=solicitudes)


@venta.route('/solicitud_produccion/crear', methods=["GET", "POST"])
@login_required
def solicitud_produccion_nuevo():
    form = forms.SolicitudProduccionForm(request.form)
    form.receta.choices = [(0, 'Todas las recetas')] + \
            [(receta.id, receta.nombre) for receta in Receta.query.all()]
    
    if request.method == "GET":
        return render_template('modulos/venta/solicitudesProduccion/create.html', form=form, nuevo=True)
    else:
        if form.validate():
            solicitud = SolicitudProduccion(
                idReceta=form.receta.data,
                idUsuarioSolicitud=current_user.id,
                tandas=form.tandas.data,
                status=1
            )

            db.session.add(solicitud)
            db.session.commit()

            flash('Solicitud de producción creada correctamente', 'success')

            return redirect(url_for('venta.solicitud_produccion'))
        else:
            return render_template('modulos/venta/solicitudesProduccion/create.html', form=form)

@venta.route('/solicitud_produccion/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_solicitud_produccion(id):
    solicitud = SolicitudProduccion.query.get(id)
    
    form = forms.ModificarSolicitudProduccionForm(request.form)

    if request.method == 'POST' and form.validate():
        solicitud = SolicitudProduccion.query.get(id)
        solicitud.tandas = form.tandas.data
        solicitud.fecha_solicitud = form.fecha_solicitud.data
        db.session.commit()
        
        flash('Solicitud de producción modificada correctamente', 'success')
        
        return redirect(url_for('venta.solicitud_produccion'))

    return render_template('modulos/venta/solicitudesProduccion/edit.html', form=form, solicitud = solicitud)


@venta.route('/solicitud_produccion/delete', methods=['POST'])
@login_required
def delete_solicitud_produccion():
    id = request.form.get('id')
    solicitud = SolicitudProduccion.query.get_or_404(id)
    db.session.delete(solicitud)
    db.session.commit()
    flash('Solicitud de producción eliminada correctamente', 'success')
    return redirect(url_for('venta.solicitud_produccion'))


@venta.route('/almacen/galletas', methods=['GET', 'POST'])
def lotes_galletas():
    form = forms.BusquedaLoteGalletaForm(request.form)

    form.receta.choices = [(0, 'Todas las recetas')] + \
        [(receta.id, receta.nombre) for receta in Receta.query.all()]

    if request.method == "POST" and form.validate():
        fecha_inicio = form.fecha_inicio.data
        fecha_fin = form.fecha_fin.data
        receta = form.receta.data
        lotes = []

        base_query = db.session.query(LoteGalleta, Receta.nombre, Usuario.nombre).join(
            Receta, LoteGalleta.idReceta == Receta.id).join(Usuario, LoteGalleta.idUsuarios == Usuario.id)
        print(fecha_inicio, fecha_fin, receta)
        if receta == 0:
            lotes = base_query.filter(
                LoteGalleta.fecha_entrada >= fecha_inicio,
                LoteGalleta.fecha_entrada <= fecha_fin,
                LoteGalleta.cantidad > 0
            ).all()
        else:
            lotes = base_query.filter(
                LoteGalleta.fecha_entrada >= fecha_inicio,
                LoteGalleta.fecha_entrada <= fecha_fin,
                LoteGalleta.idReceta == receta,
                LoteGalleta.cantidad > 0
            ).all()

        return render_template('modulos/venta/galletas.html', form=form, lotes=lotes, lista=True)

    lotes = db.session.query(LoteGalleta, Receta.nombre, Usuario.nombre).join(Receta, LoteGalleta.idReceta == Receta.id).join(
        Usuario, LoteGalleta.idUsuarios == Usuario.id).filter(LoteGalleta.cantidad > 0).all()

    return render_template('modulos/venta/galletas.html', form=form, lotes=lotes, lista=True)


@venta.route('/merma/galletas', methods=['GET', 'POST'])
def merma_galletas():
    form = forms.MermaGalletaForm(request.form)
    if form.validate():
        tipo_medida = form.tipo_medida.data
        cantidad = form.cantidad.data

    return redirect(url_for('venta.lotes_galletas'))
