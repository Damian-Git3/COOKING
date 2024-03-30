
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

asignacion_rol_usuario = db.Table('asignacion_rol_usuario',
    db.Column('idUsuario', db.Integer, db.ForeignKey('usuarios.id')),
    db.Column('idRol', db.Integer, db.ForeignKey('roles.id')))

class Roles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(45), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))
    
    def __repr__(self):
        return f"<Rol: {self}>"

class Usuarios(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(255), unique=True, nullable=False)
    nombre = db.Column(db.String(255), unique=True, nullable=False)
    contrasenia = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(255), nullable=True)
    last_login_at = db.Column(db.DateTime)
    current_login_at = db.Column(db.DateTime)
    #last_login_ip = db.Column(db.String(100))
    #current_login_ip = db.Column(db.String(100))
    #login_count = db.Column(db.Integer)
    is_active = db.Column(db.Boolean(), default=True)
    is_authenticated = db.Column(db.Boolean(), default=True)
    is_anonymous = db.Column(db.Boolean(), default=False)
    estatus = db.Column(db.Boolean(), nullable=False, default=True)
    #fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime)
    roles = db.relationship('Roles', secondary=asignacion_rol_usuario, backref=db.backref('usuarios', lazy='dynamic'))
    def get_id(self):
        return str(self.id)