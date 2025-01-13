from flask import Flask, redirect, url_for, request
from flask_login import LoginManager, current_user
from flask_mysqldb import MySQL
from datetime import timedelta
from mixin.user import User
from routes.auth import auth_bp
from routes.contact import contact_bp
from routes.dashboard import dashboard_bp
from routes.profile import profile_bp
from routes.sources import sources_bp
from routes.transactions import transactions_bp
from routes.categories import categories_bp
from helpers.helpers import get_source_title, format_number

app = Flask(__name__)
app.config.from_object("config.Config")

# Kết nối MySQL
mysql = MySQL(app)

# Cấu hình Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.remember_cookie_duration = timedelta(days=7)


@login_manager.user_loader
def load_user(user_id):
    connection = mysql.connection.cursor()
    connection.execute("SELECT * FROM nguoidung WHERE ID = %s", (user_id,))
    user = connection.fetchone()
    connection.close()
    if user:
        return User(id=user[0], username=user[1], email=user[2], hoten=user[4])
    return None

@app.before_request
def redirect_authenticated_users():
    if current_user.is_authenticated and request.endpoint in ['login', 'register']:
        return redirect(url_for('dashboard_bp.dashboard'))

# Khai báo module blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(contact_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(sources_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(categories_bp)


app.jinja_env.filters['format_number'] = format_number
app.jinja_env.filters['get_source_title'] = get_source_title

if __name__ == '__main__':
    app.run(debug=True)
