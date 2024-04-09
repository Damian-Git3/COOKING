from flask import Blueprint, render_template
from flask_login import login_required

dashboard = Blueprint(
    "dashboard", __name__, url_prefix="/dashboard", template_folder="templates"
)


@dashboard.route("/")
@login_required
def index():
    galletaVentasMes = [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210]

    ventasMes = [85, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190]

    return render_template(
        "dashboard/dashboard.html",
        galletaVentasMes=galletaVentasMes,
        ventasMes=ventasMes,
        galletasTipos=['Chocolate', 'Vainilla', 'Fresa', 'Nuez'],
        galletasVendidas=[120, 100, 90, 80]
    )
