from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from flask_mysqldb import MySQL
from helpers.helpers import get_categories

mysql = MySQL()

transactions_bp = Blueprint('transactions_bp', __name__)

# transactions
@transactions_bp.route('/transactions', methods=['GET'])
@login_required
def transactions():
    # Lấy các tham số lọc và tìm kiếm từ request
    category = request.args.get('category')
    transaction_type = request.args.get('type')
    search_query = request.args.get('search')
    page = int(request.args.get('page', 1))
    items_per_page = 10

    # Câu truy vấn cơ sở dữ liệu
    connection = mysql.connection.cursor()
    query = """
        SELECT g.ID, d.TEN AS category, g.type, g.SOTIEN, g.date, g.MOTA
        FROM giaodich g
        JOIN danhmuc d ON g.DANHMUC_ID = d.ID
        WHERE g.NGUOIDUNG_ID = %s
    """
    params = [current_user.id]

    # Áp dụng lọc theo danh mục
    if category:
        category = int(category)
        query += " AND d.ID = %s"
        params.append(category)

    # Áp dụng lọc theo loại giao dịch (chi tiêu hoặc thu nhập)
    if transaction_type:
        query += " AND g.type = %s"
        params.append(transaction_type)

    # Áp dụng tìm kiếm
    if search_query:
        query += " AND g.MOTA LIKE %s"
        params.append(f"%{search_query}%")

    # Phân trang
    query += " ORDER BY g.date DESC LIMIT %s OFFSET %s"
    params.extend([items_per_page, (page - 1) * items_per_page])

    connection.execute(query, params)
    transactions = connection.fetchall()

    connection.execute("""
        SELECT status, card_type, type, sothe, sodu 
        FROM nguonthu 
        WHERE NGUOIDUNG_ID = %s
    """, [current_user.id])
    sources = connection.fetchall()

    # Lấy tổng số giao dịch để tính số trang
    connection.execute("SELECT COUNT(*) FROM giaodich WHERE NGUOIDUNG_ID = %s", [current_user.id])
    total_transactions = connection.fetchone()[0]
    total_pages = (total_transactions + items_per_page - 1) // items_per_page


    connection.close()

    # Truyền dữ liệu vào template
    return render_template('transactions.html',
                           transactions=transactions,
                           total_pages=total_pages,
                           current_page=page,
                           categories=get_categories(), 
                           transaction_type=transaction_type,
                           search_query=search_query,
                           sources=sources)

# add transactions
@transactions_bp.route('/add_transaction', methods=['POST'])
@login_required
def add_transaction():
    # Lấy dữ liệu từ form
    amount = request.form.get('amount')
    category = request.form.get('category')
    date = request.form.get('date')
    source = request.form.get('source')
    note = request.form.get('note')
    transaction_type = request.form.get('type')  # 'expense' hoặc 'income'

    # Kiểm tra dữ liệu
    if not amount or not category or not date or not source:
        flash("Vui lòng điền đầy đủ thông tin.", "danger")
        return redirect(url_for('dashboard_bp.dashboard'))

    try:
        # Kết nối cơ sở dữ liệu và chèn giao dịch
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO giaodich (NGUOIDUNG_ID, DANHMUC_ID, NGUONTHU_ID, type, SOTIEN, date, MOTA)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (current_user.id, category, source, transaction_type, amount, date, note))
        mysql.connection.commit()
        cur.close()

        flash("Giao dịch đã được thêm thành công!", "success")
    except Exception as e:
        flash(f"Đã xảy ra lỗi: {e}", "danger")

    return redirect(url_for('dashboard_bp.dashboard'))

# update transactions
@transactions_bp.route('/update_transaction', methods=['POST'])
@login_required
def update_transaction():
    transaction_id = request.form.get('transaction_id')
    amount = request.form.get('amount')
    date = request.form.get('date')
    note = request.form.get('note')
    type = request.form.get('type')
    category = request.form.get('category')

    try:
        connection = mysql.connection.cursor()
        connection.execute("""
            UPDATE giaodich
            SET SOTIEN = %s, date = %s, MOTA = %s, type = %s, DANHMUC_ID = %s
            WHERE ID = %s AND NGUOIDUNG_ID = %s
        """, (amount, date, note, type, category, transaction_id, current_user.id))
        mysql.connection.commit()
        flash("Giao dịch đã được cập nhật thành công!", "success")
    except Exception as e:
        flash(f"Có lỗi xảy ra: {e}", "danger")
    finally:
        connection.close()

    return redirect(url_for('transactions'))



