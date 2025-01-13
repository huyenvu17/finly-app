from flask import Blueprint, render_template
from flask_login import login_required

profile_bp = Blueprint('profile_bp', __name__)


@profile_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')