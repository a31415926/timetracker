from flask import render_template, Blueprint, request
from . import db
from .models import Office
from flask_login import login_required, current_user

admin = Blueprint('admin', __name__, url_prefix='/admin')


@admin.route('/office', methods=['GET'])
def get_office():
    offices = Office.query.all()
    return render_template(
        'offices.html',
        offices=offices,
    )


@admin.route('/office', methods=['POST'])
def post_office():
    action = request.form.get('action')
    print(action)
    if action == 'create':
        name = request.form.get('name', '').strip()
        if not name:
            return {'success': False, 'msg': 'Field name is empty'}
        new_office = Office(name=name)
        db.session.add(new_office)
        db.session.commit()
        return {'success': True, 'msg': 'Office created'}
    elif action == 'edit':
        name = request.form.get('name', '').strip()
        oid = request.form.get('office_id')
        if not name or not oid:
            return {'success': False, 'msg': 'Field name or office_id is empty'}
        Office.query.filter_by(id=oid).update({
            'name': name,
        })
        db.session.commit()
    return {'success': True}
