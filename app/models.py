from . import db
from flask_login import UserMixin
from datetime import datetime, date


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_approve_vacation = db.Column(db.Boolean, default=False)
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id'))
    name = db.Column(db.String(70))

    office = db.relationship('Office', foreign_keys=[office_id])

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'office': self.office_id,
        }


class Vacation(db.Model):
    __tablename__ = 'vacations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_create = db.Column(db.DateTime, default=datetime.utcnow)
    date_from = db.Column(db.Date, nullable=False)
    date_to = db.Column(db.Date, nullable=False)
    date_delta = db.Column(db.SmallInteger, default=1)
    type = db.Column(db.SmallInteger, default=1)  # 1 - отпуск, 2 - больничный
    state = db.Column(db.SmallInteger, default=0)  # -1 - отклонена, 0 - ожидает, 1 - подтверждена
    comment = db.Column(db.Text)
    is_mailing = db.Column(db.Boolean, default=False)
    mailing_comment = db.Column(db.Text)
    user = db.relationship('User', foreign_keys=[user_id])
    responsible = db.relationship('User', foreign_keys=[responsible_id])

    def __init__(self, **kwargs):
        super(Vacation, self).__init__(**kwargs)

    def approve_vacation(self, state: int = 0, cnt_days: int = 1):
        vac = Vacation.query.get(self.id)
        vac.state = state
        vac.date_delta = cnt_days
        # если подтверждена и это отпуск, то меняем использованное кол-во дней
        if state == 1 and vac.type == 1:
            uid = vac.user_id
            year = vac.date_to.year
            vac_used = VacationUsed.query.filter_by(user_id=uid, year=year).first()
            if vac_used is None:
                _new = VacationUsed(user_id=uid, year=year, days=cnt_days)
                db.session.add(_new)
            else:
                vac_used.days += cnt_days
            # рассылка
            if vac.is_mailing:
                print('расссыыыыыыылка')
                print(vac.mailing_comment)
        db.session.commit()


class VacationUsed(db.Model):
    __tablename__ = 'vacation_used'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    days = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', foreign_keys=[user_id])

    __table_args__ = (
        db.PrimaryKeyConstraint(user_id, year),
        {}
    )


class TimeTracker(db.Model):
    __tablename__ = 'timetracker'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_start = db.Column(db.DateTime, default=datetime.utcnow)
    date_end = db.Column(db.DateTime)
    time_delta = db.Column(db.Time)
    user = db.relationship('User', foreign_keys=[user_id])


class Office(db.Model):
    __tablename__ = 'offices'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
