from flask import render_template, request, redirect, url_for, Blueprint, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User, Vacation
from flask_login import login_user
from datetime import timedelta, datetime

user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/<int:uid>', methods=['GET', 'POST'])
@login_required
def user_edit_post(uid):
    user_info = User.query.get_or_404(uid)
    if request.method == 'POST':
        return jsonify(user_info.serialize)
    return render_template(
        'user_page.html',
        user=user_info
    )

