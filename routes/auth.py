from flask import Blueprint, render_template, request, redirect, url_for, request, flash 
from flask_login import login_user, logout_user, login_required
from flask_mysqldb import MySQL
import bcrypt
from mixin.user import User

mysql = MySQL()

auth_bp = Blueprint('auth_bp', __name__)

#login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        connection = mysql.connection.cursor()  
        connection.execute("SELECT ID, PASSWORD, USERNAME, HOTEN FROM nguoidung WHERE EMAIL = %s", [email])
        user = connection.fetchone()
        connection.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
            login_user(User(id=user[0], username=user[2], email=email, hoten=user[3]))
            flash("Đăng nhập thành công!", "info")
            return redirect(url_for('dashboard_bp.dashboard'))
        else:
            flash("Email hoặc mật khẩu không chính xác.", "danger")
    return render_template('login.html')

# register
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        hoten = request.form['hoten']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            connection = mysql.connection.cursor()
            # Thêm người dùng mới vào bảng nguoidung
            connection.execute("""
                INSERT INTO nguoidung (USERNAME, HOTEN, EMAIL, PASSWORD) 
                VALUES (%s, %s, %s, %s)
            """, (username, hoten, email, hashed_password.decode('utf-8')))
            mysql.connection.commit()

            # Lấy ID người dùng vừa được thêm
            user_id = connection.lastrowid

            # Thêm ví mặc định cho người dùng mới
            connection.execute("""
                INSERT INTO nguonthu (NGUOIDUNG_ID, type, SOTHE, SODU, status) 
                VALUES (%s, %s, NULL, 0, 1)
            """, (user_id, 'wallet'))
            mysql.connection.commit()
            connection.close()

            flash("Đăng ký thành công! Hãy đăng nhập.", "info")
            return redirect(url_for('auth_bp.login'))
        except Exception as e:
            flash(f"Có lỗi xảy ra trong quá trình đăng ký: {e}", "danger")
            return redirect(url_for('auth_bp.register'))
    return render_template('register.html')

# logout
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Bạn đã đăng xuất.", "info")
    return redirect(url_for('auth_bp.login'))