from wtforms import Form
from wtforms import StringField, TextAreaField,IntegerField, SelectField, RadioField, BooleanField, PasswordField, DateField
from wtforms import EmailField
from wtforms import validators
from datetime import date

class SignupForm(Form):
    nombre = StringField("nombre", [
        validators.DataRequired(message='el campo es requerido'),
        validators.Length(min=4, max=10, message='ingresa nombre valido')
    ])
    contrasenia = PasswordField("Contraseña", [
        validators.DataRequired(message='el campo es requerido'),
        validators.EqualTo('confirmacion', message='las contraseñas no coinciden')
    ])
    confirmacion = PasswordField("Confirmar Contraseña")
    correo = StringField("Correo", [
        validators.DataRequired(message='el campo es requerido'),
        validators.Email(message='ingresa un correo electrónico válido')
        ])
    

class SolicitudProduccionForm(Form):
    
    receta = SelectField("Receta", [
        validators.DataRequired(message='Selecciona una receta')
    ], choices=[])
    tandas = IntegerField("Número de Tandas", [
        validators.DataRequired(message='Ingresa el número de tandas'),
        validators.NumberRange(min=1, message='El número de tandas debe ser mayor a 0')
    ])
    fecha_solicitud = DateField("Fecha de Solicitud", default=date.today(), format='%Y-%m-%d')
    
class ModificarSolicitudProduccionForm(Form):
    
    tandas = IntegerField("Número de Tandas", [
        validators.DataRequired(message='Ingresa el número de tandas'),
        validators.NumberRange(min=1, message='El número de tandas debe ser mayor a 0')
    ])
    fecha_solicitud = DateField("Fecha de Solicitud", default=date.today(), format='%Y-%m-%d')
    mensaje = TextAreaField("Mensaje")