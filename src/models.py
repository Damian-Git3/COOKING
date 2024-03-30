from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(45), nullable=False)
    rol = db.Column(db.Integer, nullable=False)
    correo = db.Column(db.String(45), unique=True, nullable=False)
    contrasenia = db.Column(db.String(45), nullable=False)
    token = db.Column(db.String(45))
    
class Insumo(db.Model):
    __tablename__ = 'insumos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(45), nullable=False)
    descripcion = db.Column(db.String(45), nullable=False)
    unidad_medida = db.Column(db.String(45), nullable=False)
    cantidad_maxima = db.Column(db.Float, nullable=False)
    cantidad_minima = db.Column(db.Float, nullable=False)
    merma = db.Column(db.Float, nullable=False)
    
class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    
    id = db.Column(db.Integer, primary_key=True)
    empresa = db.Column(db.String(45), nullable=False)
    direccion = db.Column(db.String(45), nullable=False)
    nombre_proveedor = db.Column(db.String(45), nullable=False)
    
class Receta(db.Model):
    __tablename__ = 'recetas'
    
    id = db.Column(db.Integer, primary_key=True)
    peso_estimado = db.Column(db.Float, nullable=False)
    utilidad = db.Column(db.Float)
    piezas = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.String(500))
    nombre = db.Column(db.String(50), nullable=False)

class AsignacionRolUsuario(db.Model):
    __tablename__ = 'asignaciones_rol_usuario'
    
    idRol = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), primary_key=True)

class Compra(db.Model):
    __tablename__ = 'compras'
    
    id = db.Column(db.Integer, primary_key=True)
    pago_proveedor = db.Column(db.Float, nullable=False)
    
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    idTransaccionCaja = db.Column(db.Integer, primary_key=True)
    idProveedores = db.Column(db.Integer, db.ForeignKey('proveedores.id'), primary_key=True)
    
class Venta(db.Model):
    __tablename__ = 'ventas'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_venta = db.Column(db.DateTime, nullable=False)
    total_venta = db.Column(db.Float, nullable=False)
    
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    idProveedores = db.Column(db.Integer, db.ForeignKey('proveedores.id'), primary_key=True)

class CorteCaja(db.Model):
    __tablename__ = 'cortes_caja'
    
    id = db.Column(db.Integer, primary_key=True)
    monto_final = db.Column(db.Float)
    monto_inicial = db.Column(db.Float)
    fecha_corte = db.Column(db.Date)

class DetalleVenta(db.Model):
    __tablename__ = 'detalles_venta'
    
    precio = db.Column(db.Float, nullable=False)
    cantidad = db.Column(db.Integer)
    
    idVenta = db.Column(db.Integer, db.ForeignKey('ventas.id'), primary_key=True)
    idStock = db.Column(db.Integer, db.ForeignKey('lotes_galletas.id'), primary_key=True)

class IngredienteReceta(db.Model):
    __tablename__ = 'ingredientes_receta'
    
    cantidad = db.Column(db.Float, nullable=False)
    
    idReceta = db.Column(db.Integer, db.ForeignKey('recetas.id'), primary_key=True)
    idInsumo = db.Column(db.Integer, db.ForeignKey('insumos.id'), primary_key=True)

class LogAccion(db.Model):
    __tablename__ = 'logs_acciones'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False)
    modulo = db.Column(db.String(45), nullable=False)
    detalles = db.Column(db.String(200), nullable=False)
    
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

class LogLogin(db.Model):
    __tablename__ = 'logs_login'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False)
    exito = db.Column(db.Boolean, nullable=False)
    
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

class LoteGalleta(db.Model):
    __tablename__ = 'lotes_galletas'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_entrada = db.Column(db.Date)
    cantidad = db.Column(db.Integer, nullable=False)
    merma = db.Column(db.Integer)
    tipo_venta = db.Column(db.Integer, nullable=False)
    
    idProduccion = db.Column(db.Integer, db.ForeignKey('solicitudes_produccion.id'), nullable=False)
    idReceta = db.Column(db.Integer, nullable=False)
    idUsuarios = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

class LoteInsumo(db.Model):
    __tablename__ = 'lotes_insumo'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_caducidad = db.Column(db.Date, nullable=False)
    cantidad = db.Column(db.Float, nullable=False)
    fecha_compra = db.Column(db.Date, nullable=False)
    precio_unidad = db.Column(db.Float, nullable=False)
    
    idInsumo = db.Column(db.Integer, db.ForeignKey('insumos.id'), primary_key=True)
    idCompra = db.Column(db.Integer, db.ForeignKey('compras.id'), primary_key=True)

class Rol(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(45), nullable=False)
    descripcion = db.Column(db.String(45), nullable=False)
    permisos = db.Column(db.Text)

class SolicitudProduccion(db.Model):
    __tablename__ = 'solicitudes_produccion'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_produccion = db.Column(db.Date, nullable=False)
    mensaje = db.Column(db.String(50))
    status = db.Column(db.Boolean)
    tandas = db.Column(db.Integer)
    merma = db.Column(db.Integer)
    fecha_solicitud = db.Column(db.Date)
    
    idReceta = db.Column(db.Integer, db.ForeignKey('recetas.id'), nullable=False)
    idUsuarioSolictud = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    idUsuarioProduccion = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

class TransaccionCaja(db.Model):
    __tablename__ = 'transacciones_caja'
    
    id = db.Column(db.Integer, primary_key=True)
    monto_egreso = db.Column(db.Float)
    monto_ingreso = db.Column(db.Float)
    fecha_transaccion = db.Column(db.Date)
    
    idCorteCaja = db.Column(db.Integer, db.ForeignKey('cortes_caja.id'), nullable=False)