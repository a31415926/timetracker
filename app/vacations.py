from flask import render_template, request, redirect, url_for, Blueprint
from flask_login import login_required, current_user
from . import db
from .models import User, Vacation, TimeTracker, Office
from flask_login import login_user
from datetime import timedelta, datetime

vacations = Blueprint('vacations', __name__)


@vacations.route('/new_vacation', methods=['GET'])
@login_required
def create_vacation_get():
    all_approve = User.query.filter_by(
        is_approve_vacation=True,
    )
    return render_template(
        'vacations/create.html',
        users=all_approve
    )


@vacations.route('/new_vacation', methods=['POST'])
@login_required
def create_vacation_post():
    if request.form.get('date_from') and request.form.get('date_to'):
        date_from = datetime.strptime(request.form.get('date_from'), '%Y-%m-%d')
        date_to = datetime.strptime(request.form.get('date_to'), '%Y-%m-%d')
    else:
        return {'error': 'field date is empty'}
    if request.form.get('responsible_id'):
        responsible_id = request.form.get('responsible_id')
    else:
        return {'error': 'field responsible_id is empty'}
    delta = (date_to - date_from).days + 1
    is_mailing = request.form.get('is_mailing', 0)
    new_vacation = Vacation(
        user_id=current_user.id,
        date_from=date_from,
        date_to=date_to,
        responsible_id=responsible_id,
        comment=request.form.get('comment', ''),
        date_delta=delta,
        is_mailing=True if is_mailing else False,
        mailing_comment=request.form.get('text_mailing', ''),
    )
    db.session.add(new_vacation)
    db.session.commit()
    return {'success': True}


@vacations.route('/vacation/<int:vid>', methods=['POST'])
@login_required
def action_vacation(vid):
    action = request.form.get('action')
    if action == 'approve':
        new_state = 1
    elif action == 'rejected':
        new_state = -1
    else:
        return {'success': False, 'msg': 'Unknown action'}

    tmp = Vacation(id=vid)
    tmp.approve_vacation(state=new_state)
    return {'msg': 'ok', 'success': True, 'new_status': new_state}

