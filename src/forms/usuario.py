"""Clase que define el formulario de usuario"""

from wtforms import (EmailField, Form, PasswordField, StringField, SubmitField,
                     validators)


class UsuarioForm(Form):
    """Clase que define el formulario de usuario"""

    nombre = StringField(
        "Nombre",
        [
            validators.DataRequired(message="el campo es requerido"),
            validators.Length(min=4, max=10, message="ingresa nombre valido"),
        ],
    )
    correo = EmailField(
        "Correo",
        [
            validators.DataRequired(message="el campo es requerido"),
            validators.Email(message="ingresa un correo electrónico válido"),
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

    submit = SubmitField("Guardar")
