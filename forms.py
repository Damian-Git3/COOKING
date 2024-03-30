from wtforms import Form
from wtforms import StringField, TextAreaField,IntegerField, SelectField, RadioField, BooleanField, PasswordField
from wtforms import EmailField
from wtforms import validators

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