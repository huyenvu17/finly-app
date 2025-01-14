from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_mysqldb import MySQL
import bcrypt

mysql = MySQL()

profile_bp = Blueprint('profile_bp', __name__)

# profile page
@profile_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

# update profile
@profile_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    username = request.form.get('username')
    full_name = request.form.get('full_name')

    if not username or not full_name:
        flash("Vui lòng điền đầy đủ thông tin.", "danger")
        return redirect(url_for('profile_bp.profile'))

    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE nguoidung
            SET USERNAME = %s, HOTEN = %s
            WHERE ID = %s
        """, (username, full_name, current_user.id))
        mysql.connection.commit()
        cur.close()

        # Cập nhật thông tin hiển thị của người dùng
        current_user.username = username
        current_user.hoten = full_name

        flash("Cập nhật thông tin thành công!", "info")
    except Exception as e:
        flash(f"Lỗi khi cập nhật thông tin: {e}", "danger")

    return redirect(url_for('profile_bp.profile'))

# update password
@profile_bp.route('/update_password', methods=['POST'])
@login_required
def update_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if new_password != confirm_password:
        flash("Mật khẩu xác nhận không khớp.", "danger")
        return redirect(url_for('profile_bp.profile'))

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT PASSWORD FROM nguoidung WHERE ID = %s", (current_user.id,))
        stored_password = cur.fetchone()[0]

        if not bcrypt.checkpw(current_password.encode('utf-8'), stored_password.encode('utf-8')):
            flash("Mật khẩu hiện tại không chính xác.", "danger")
            return redirect(url_for('profile_bp.profile'))

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        cur.execute("UPDATE nguoidung SET PASSWORD = %s WHERE ID = %s", (hashed_password.decode('utf-8'), current_user.id))
        mysql.connection.commit()
        cur.close()

        flash("Mật khẩu đã được cập nhật thành công!", "info")
    except Exception as e:
        flash(f"Lỗi khi cập nhật mật khẩu: {e}", "danger")

    return redirect(url_for('profile_bp.profile'))
