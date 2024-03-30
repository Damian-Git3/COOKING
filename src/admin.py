from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_babel import Babel

# Importar base de datos
from models import db

# Importar modelos de base de datos
from models import Usuario, Rol, Insumo, Proveedor

# Importar configuración
from config import config

# Inicializar aplicación
app = Flask(__name__)
app.config.from_object(config['development'])

# Inicializar Flask_Admin
admin = Admin(app, template_mode='bootstrap4')
babel = Babel(app)

# Agregar módulos a Flask_Admin
admin.add_view(ModelView(Rol, db.session))
admin.add_view(ModelView(Usuario, db.session))
admin.add_view(ModelView(Insumo, db.session))
admin.add_view(ModelView(Proveedor, db.session))

# Función para cambiar idioma al Flask_Admin
def get_locale():
    return 'es'

if __name__ == '__main__':
    babel.init_app(app, locale_selector=get_locale)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.run()