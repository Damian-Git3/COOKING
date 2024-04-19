"""Clase que define el formulario de usuario"""

from wtforms import EmailField, Form, PasswordField, SubmitField, validators


class UsuarioForm(Form):
    """Clase que define el formulario de usuario"""

    correo = EmailField(
        "Correo",
        [
            validators.DataRequired(message="Campo Requerido"),
            validators.Email(message="Ingresa un Correo Electrónico Válido"),
        ],
        render_kw={"placeholder": "CORREO", "type": "password"},
    )
    contrasenia = PasswordField(
        "Contraseña",
        [
            validators.DataRequired(message="Campo Requerido"),
            validators.EqualTo("confirmacion", message="Las Contraseñas no Coinciden"),
        ],
        render_kw={"placeholder": "CONTRASENIA", "type": "password"},
    )
    confirmacion = PasswordField(
        "Confirmar Contraseña", render_kw={"placeholder": "CORREO"}
    )

    submit = SubmitField("Guardar")
