#sources
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from helpers.helpers import get_source_title
from flask_mysqldb import MySQL

mysql = MySQL()

sources_bp = Blueprint('sources_bp', __name__)

# sources
@sources_bp.route('/sources')
@login_required
def sources():
    connection = mysql.connection.cursor()

    # Fetch tất cả nguồn thu
    connection.execute("""
        SELECT id, status, card_type, type, sothe, sodu 
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
    source_type = request.form.get('type')
    card_type = request.form.get('card_type') if source_type == 'card' else None
    card_number = request.form.get('sothe') if source_type == 'card' else None
    balance = request.form.get('balance') or 0
    status = request.form.get('status', 1) 

    # Lấy danh sách nguồn thu hiện tại của người dùng
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT type, card_type, sothe 
        FROM nguonthu 
        WHERE NGUOIDUNG_ID = %s
    """, (current_user.id,))
    existing_sources = cur.fetchall()

    # Kiểm tra logic
    if source_type in ['wallet', 'cash', 'bank']:
        for src in existing_sources:
            if src[0] == source_type:
                flash(f"Loại nguồn thu '{get_source_title(source_type)}' đã tồn tại!", "danger")
                return redirect(url_for('sources_bp.sources'))

    # Kiểm tra logic cho thẻ
    if source_type == 'card':
        for src in existing_sources:
            if src[0] == 'card' and src[1] == card_type and src[2] == card_number:
                flash(f"Thẻ '{card_type}' với số thẻ '{card_number}' đã tồn tại!", "danger")
                return redirect(url_for('sources_bp.sources'))

    # Chèn vào cơ sở dữ liệu
    try:
        cur.execute("""
            INSERT INTO nguonthu (NGUOIDUNG_ID, TYPE, card_type, SOTHE, SODU, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (current_user.id, source_type, card_type, card_number,balance, status))
        mysql.connection.commit()
        flash("Nguồn thu đã được thêm thành công!", "info")
    except Exception as e:
        flash(f"Có lỗi xảy ra: {e}", "danger")
    finally:
        cur.close()

    return redirect(url_for('sources_bp.sources'))

# update souce
@sources_bp.route('/update_source', methods=['POST'])
@login_required
def update_source():
    source_id = request.form.get('source_id')
    new_balance = request.form.get('balance') or 0
    new_status = request.form.get('status')
    card_type = request.form.get('card_type')
    card_number = request.form.get('sothe')

    try:
        # Xử lý cập nhật loại thẻ nếu là loại "card"
        cur = mysql.connection.cursor()
        if card_type and card_number:
            cur.execute("""
                UPDATE nguonthu 
                SET SODU = %s, status = %s, card_type = %s, SOTHE = %s 
                WHERE ID = %s AND NGUOIDUNG_ID = %s
            """, (new_balance, new_status, card_type, card_number, source_id, current_user.id))
        else:
            cur.execute("""
                UPDATE nguonthu 
                SET SODU = %s, status = %s 
                WHERE ID = %s AND NGUOIDUNG_ID = %s
            """, (new_balance, new_status, source_id, current_user.id))
        mysql.connection.commit()
        flash("Nguồn thu đã được cập nhật thành công!", "info")
    except Exception as e:
        flash(f"Có lỗi xảy ra: {e}", "danger")
    finally:
        cur.close()

    return redirect(url_for('sources_bp.sources'))

# delete source
@sources_bp.route('/delete_source', methods=['GET'])
@login_required
def delete_source():
    source_id = request.args.get('source_id')

    # Lấy thông tin nguồn thu để kiểm tra
    connection = mysql.connection.cursor()
    connection.execute("SELECT TYPE FROM nguonthu WHERE ID = %s AND NGUOIDUNG_ID = %s", (source_id, current_user.id))
    source = connection.fetchone()

    if not source:
        flash("Nguồn thu không tồn tại hoặc bạn không có quyền truy cập.", "danger")
        return redirect(url_for('sources_bp.sources'))

    if source[0] == 'wallet':  # Không xóa được Ví Finly
        flash("Không thể xóa Ví Finly (nguồn thu mặc định).", "danger")
        return redirect(url_for('sources_bp.sources'))

    # Xóa nguồn thu
    try:
        connection.execute("DELETE FROM nguonthu WHERE ID = %s AND NGUOIDUNG_ID = %s", (source_id, current_user.id))
        mysql.connection.commit()
        flash("Nguồn thu đã được xóa thành công.", "info")
    except Exception as e:
        flash(f"Đã xảy ra lỗi: {e}", "danger")
    finally:
        connection.close()

    return redirect(url_for('sources_bp.sources'))


