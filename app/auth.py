from flask import render_template, request, redirect, url_for, Blueprint, flash
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User
from flask_login import login_user, current_user

auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/', methods=['GET'])
def main_page():
    redirect_url = 'dashboard.main_dashboard' if current_user.is_authenticated else 'auth.login_form'
    return redirect(url_for(redirect_url))


@auth.route('/login', methods=['GET', 'POST'])
def login_form():
    if request.method == 'GET':
        return render_template('auth_page.html')
    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            # flash('user not found')
            return redirect(url_for('auth.login_form'))
        else:
            a = login_user(user, remember=True)
            print(a)
            return redirect(url_for('dashboard.main_dashboard'))


@auth.route('/register', methods=['GET', 'POST'])
def register_form():
    if request.method == 'GET':
        return render_template('register_page.html')
    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        print(user)
        if user:
            flash('user not found')
            return redirect(url_for('auth.register_form'))
        else:
            new_user = User(
                email=email,
                password=generate_password_hash(password, 'sha256')
            )
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('auth.login_form'))
