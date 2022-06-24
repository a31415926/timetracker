from flask import render_template, request, redirect, url_for, Blueprint
from flask_login import login_required, current_user
from . import db
from .models import User, Vacation, TimeTracker, Office
from datetime import timedelta, datetime

dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard.route('/', methods=['GET'])
@login_required
def main_dashboard():
    uid = current_user.id
    vacations = Vacation.query.filter_by(user_id=uid).order_by(Vacation.id.desc()).limit(5)
    new_vacations = []
    if current_user.is_approve_vacation:
        new_vacations = Vacation.query.filter_by(
            responsible_id=uid,
            state=0,
        )
    visits = TimeTracker.query.filter_by(user_id=uid).order_by(TimeTracker.id.desc()).limit(10)
    return render_template(
        'main_dashboard.html',
        vacations=vacations,
        new_vacations=new_vacations,
        visits=visits,
    )


@dashboard.route('/users', methods=['GET', 'POST'])
@login_required
def users_edit_form():
    offices = Office.query.all()
    select_kwargs = {}
    if request.method == 'GET':
        users = User.query.all()
    elif request.method == 'POST':
        office_id = request.form.get('office_id')
        if office_id and office_id != '0':
            select_kwargs['office_id'] = office_id

        users = User.query.filter_by(**select_kwargs)

    return render_template(
        'all_users.html',
        users=users,
        offices=offices,
        filters=select_kwargs,
    )


@dashboard.route('/user', methods=['POST'])
@login_required
def user_edit_post():
    uid = request.form.get('user_id')
    email = request.form.get('email')
    office_id = request.form.get('office')
    name = request.form.get('name')
    error_msg = ''
    if not office_id.isnumeric():
        error_msg += 'Office id incorrect\n'
    elif not uid:
        error_msg += 'user id incorrect\n'
    elif not email:
        error_msg += 'email incorrect\n'
    elif not name:
        error_msg += 'name incorrect\n'
    if error_msg:
        return {'success': False, 'msg': error_msg}
    is_admin = True if request.form.get('is_admin') else False
    is_active = True if request.form.get('is_active') else False
    User.query.filter_by(id=uid).update({
        'name': name,
        'email': email,
        'office_id': office_id,
    })
    db.session.commit()

    return {'success': True}


@dashboard.route('/visits', methods=['GET'])
@login_required
def my_visits():
    uid = current_user.id
    last_days = 3
    time_start = datetime.now() - timedelta(days=last_days)
    visits = TimeTracker.query.filter(
        (TimeTracker.user_id == uid) & (TimeTracker.date_start > time_start)
    ).order_by(TimeTracker.id.desc())
    all_dates = {}
    date_start = datetime.today()
    weekdays = {
        '1': 'Понедельник',
        '2': 'Вторник',
        '3': 'Среда',
        '4': 'Четверг',
        '5': 'Пятница',
        '6': 'Суббота',
        '7': 'Воскресенье',
    }
    for i in range(last_days):
        date = date_start - timedelta(days=i)
        all_dates[f'{date.month}-{date.day}'] = {
            'visits': [],
            'date': date.strftime('%Y-%m-%d'),
            'weekday': weekdays.get(f'{date.isoweekday()}', '')
        }
    for visit in visits:
        date = f"{visit.date_start.month}-{visit.date_start.day}"
        tmp_visits = {
            'date_start': visit.date_start.strftime('%H:%M:%S') if visit.date_start else '',
            'date_end': visit.date_end.strftime('%H:%M:%S') if visit.date_end else '',
            'time_delta': visit.time_delta if visit.time_delta else '',
        }
        if visit.time_delta:
            _time_delta = timedelta(
                hours=visit.time_delta.hour,
                minutes=visit.time_delta.minute,
                seconds=visit.time_delta.second,
            )
        else:
            _time_delta = timedelta(hours=0, minutes=0, seconds=0)
        if all_dates.get(date, {}).get('times_day') and visit.time_delta:
            all_dates[date]['times_day'] = all_dates[date]['times_day'] + _time_delta
        else:
            all_dates[date]['times_day'] = _time_delta
        all_dates.get(date, {}).get('visits', []).append(tmp_visits)

    return render_template(
        'my_visits.html',
        all_dates=all_dates,
    )


@dashboard.route('/visit', methods=['POST', 'GET'])
@login_required
def post_visit():
    uid = current_user.id
    action = request.form.get('action')

    if action == 'exit':
        end_visit = TimeTracker.query.filter_by(user_id=uid).order_by(TimeTracker.id.desc()).first()
        if end_visit and not end_visit.date_end:
            date_now = datetime.utcnow()
            TimeTracker.query.filter_by(id=end_visit.id).update({
                'date_end': date_now,
                'time_delta': date_now - end_visit.date_start,
            })
            db.session.commit()
    elif action == 'enter':
        new_visit = TimeTracker(user_id=uid)
        db.session.add(new_visit)
        db.session.commit()
    else:
        return {'success': False, 'msg': 'Unknown action'}
    return {'success': True}


@dashboard.route('/get_responsible_id', methods=['POST'])
@login_required
def get_responsible_id():
    users = User.query.filter_by(is_approve_vacation=True)
    resp_users = {}
    for user in users:
        resp_users[f'{user.id}'] = user.name
    return {'success': True, 'users': resp_users}
