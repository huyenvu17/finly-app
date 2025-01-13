from flask import Blueprint, render_template
from flask_login import login_required

contact_bp = Blueprint('contact_bp', __name__)

@contact_bp.route('/contact')
@login_required
def contact():
    return render_template('contact.html')
