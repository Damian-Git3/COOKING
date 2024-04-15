from wtforms import Form, PasswordField
from wtforms import StringField
from wtforms import validators


class UsuarioForm(Form):
    nombre = StringField(
        "nombre",
        [
            validators.DataRequired(message="el campo es requerido"),
            validators.Length(min=4, max=10, message="ingresa nombre valido"),
        ],
    )
    contrasenia = PasswordField(
        "Contraseña",
        [
            validators.DataRequired(message="el campo es requerido"),
            validators.EqualTo("confirmacion", message="las contraseñas no coinciden"),
        ],
    )
    confirmacion = PasswordField("Confirmar Contraseña")
    correo = StringField(
        "Correo",
        [
            validators.DataRequired(message="el campo es requerido"),
            validators.Email(message="ingresa un correo electrónico válido"),
        ],
    )
