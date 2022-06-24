from flask import redirect, url_for, Blueprint
from flask_login import current_user

main = Blueprint('main', __name__)


@main.route('/', methods=['GET'])
def main_page():
    redirect_url = 'dashboard.main_dashboard' if current_user.is_authenticated else 'auth.login_form'
    return redirect(url_for(redirect_url))
