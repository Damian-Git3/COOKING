from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
import forms.forms as forms
from database.models import Usuario
from database.models import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    usuario = request.form.get('usuario')
    contrasenia = request.form.get('contrasenia')
    recordar = True if request.form.get('recordarme') else False

    user = Usuario.query.filter_by(nombre=usuario).first()
    
    if not user:
        flash('No se ha encontrado un usuario con esas credenciales. Por favor, verifica la información')
        return render_template('login.html')
    elif not check_password_hash(user.contrasenia, contrasenia):
        flash('Credenciales incorrectas. Por favor, inténtelo de nuevo.')
        return render_template('login.html')
    elif not user.estatus:
        flash('Usuario no activo. Por favor, consulta con tu administrador.')
        return render_template('login.html')

    login_user(user, remember=recordar)
    return redirect(url_for('main.menu'))

@auth.route('/signup')
def signup():
    form = forms.SignupForm(request.form)
    return render_template('signup_temporal.html',form=form)

@auth.route('/signup', methods=['POST'])
def signup_post():
    form = forms.SignupForm(request.form)
    correo = request.form.get('correo')
    nombre = request.form.get('nombre')
    contrasenia = request.form.get('contrasenia')
    
    if not form.validate():
        return render_template('signup_temporal.html', form=form)

    user = Usuario.query.filter_by(correo=correo).first()

    if user:
        flash('Este correo ya existe.')
        return redirect(url_for('auth.signup'))

    new_user = Usuario(correo=correo, nombre=nombre, contrasenia=generate_password_hash(contrasenia))

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))