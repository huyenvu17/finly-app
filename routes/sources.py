#sources
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from helpers.helpers import get_source_title
from flask_mysqldb import MySQL

mysql = MySQL()

sources_bp = Blueprint('sources_bp', __name__)

@sources_bp.route('/sources')
@login_required
def sources():
    connection = mysql.connection.cursor()

    # Fetch tất cả nguồn thu
    connection.execute("""
        SELECT status, card_type, type, sothe, sodu 
        FROM nguonthu 
        WHERE NGUOIDUNG_ID = %s
    """, [current_user.id])
    sources = connection.fetchall()

    # Lấy danh sách các loại nguồn thu từ sources
    existing_types = [source[2] for source in sources]  # Lấy cột `type` từ mỗi dòng

    # Kiểm tra nếu đã tồn tại cash hoặc bank
    disable_cash = 'cash' in existing_types
    disable_bank = 'bank' in existing_types

    connection.close()

    return render_template(
        'sources.html',
        sources=sources,  # Truyền danh sách nguồn thu
        disable_cash=disable_cash,  # Truyền trạng thái disabled cho cash
        disable_bank=disable_bank   # Truyền trạng thái disabled cho bank
    )


# add source
@sources_bp.route('/add_source', methods=['POST'])
@login_required
def add_source():
    try:
        # Get data from the form
        source_type = request.form.get('type')
        card_type = request.form.get('card_type') if source_type == 'card' else None
        card_number = request.form.get('sothe') if source_type == 'card' else None
        balance = float(request.form.get('sodu', 0))  # Initial balance
        status = 1 if request.form.get('status') == 'on' else 0  # Checkbox xử lý giá trị

        # Insert into the database
        connection = mysql.connection.cursor()
        connection.execute("""
            INSERT INTO nguonthu (NGUOIDUNG_ID, TYPE, card_type, SOTHE, SODU, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (current_user.id, source_type, card_type, card_number, balance, status))
        mysql.connection.commit()

        flash("Nguồn thu đã được thêm thành công!", "success")
    except Exception as e:
        flash(f"Có lỗi xảy ra: {e}", "danger")
    finally:
        connection.close()

    return redirect(url_for('sources'))