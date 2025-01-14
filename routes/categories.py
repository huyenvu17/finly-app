from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from flask_mysqldb import MySQL
from helpers.helpers import get_categories

mysql = MySQL()

categories_bp = Blueprint('categories_bp', __name__)

# categories
@categories_bp.route('/categories')
@login_required
def categories():
    # Lấy các tham số lọc, tìm kiếm và phân trang
    search_query = request.args.get('search', '').strip()
    category_type = request.args.get('type', '').strip()
    page = int(request.args.get('page', 1))
    items_per_page = 10  # Số mục trên mỗi trang

    offset = (page - 1) * items_per_page

    connection = mysql.connection.cursor()

    # Truy vấn cơ sở dữ liệu với tìm kiếm, lọc và phân trang
    query = """
        SELECT ID, TEN, TYPE 
        FROM danhmuc
        WHERE 1=1
    """
    params = []

    if search_query:
        query += " AND TEN LIKE %s"
        params.append(f"%{search_query}%")
    
    if category_type:
        query += " AND TYPE = %s"
        params.append(category_type)

    query += " ORDER BY ID LIMIT %s OFFSET %s"
    params.extend([items_per_page, offset])

    connection.execute(query, params)
    categories = connection.fetchall()

    # Tính tổng số lượng danh mục
    count_query = """
        SELECT COUNT(*) 
        FROM danhmuc
        WHERE 1=1
    """
    count_params = []

    if search_query:
        count_query += " AND TEN LIKE %s"
        count_params.append(f"%{search_query}%")
    
    if category_type:
        count_query += " AND TYPE = %s"
        count_params.append(category_type)

    connection.execute(count_query, count_params)
    total_items = connection.fetchone()[0]
    total_pages = (total_items + items_per_page - 1) // items_per_page

    connection.close()

    return render_template(
        'categories.html',
        categories=categories,
        search_query=search_query,
        category_type=category_type,
        current_page=page,
        total_pages=total_pages
    )



# add category
@categories_bp.route('/add_category', methods=['POST'])
@login_required
def add_category():
    cateName = request.form.get('cateName')
    cateType = request.form.get('cateType')

    try:
        connection = mysql.connection.cursor()
        connection.execute("""
            INSERT INTO danhmuc (TEN, TYPE)
            VALUES (%s, %s)
        """, (cateName, cateType))
        mysql.connection.commit()
        connection.close()
    

        flash("Danh mục đã được thêm thành công!", "info")
    except Exception as e:
        flash(f"Có lỗi xảy ra: {e}", "danger")

    return redirect(url_for('categories_bp.categories'))

# update category
@categories_bp.route('/update_category', methods=['POST'])
@login_required
def update_category():
    category_id = request.form.get('category_id') 
    category_name = request.form.get('category_name')

    if not category_id or not category_name:
        flash("Thông tin danh mục không hợp lệ.", "danger")
        return redirect(url_for('categories_bp.categories'))

    connection = mysql.connection.cursor()

    try:
        # Cập nhật tên danh mục
        connection.execute("""
            UPDATE danhmuc 
            SET TEN = %s 
            WHERE ID = %s
        """, (category_name, category_id))
        mysql.connection.commit()

        flash("Danh mục đã được cập nhật thành công.", "info")
    except Exception as e:
        flash(f"Có lỗi xảy ra: {e}", "danger")
    finally:
        connection.close()

    return redirect(url_for('categories_bp.categories'))


# delete category
@categories_bp.route('/delete_category', methods=['POST'])
@login_required
def delete_category():
    category_id = request.form.get('category_id')

    if not category_id:
        flash("Danh mục không hợp lệ.", "danger")
        return redirect(url_for('categories_bp.categories'))

    connection = mysql.connection.cursor()

    # Kiểm tra danh mục có liên kết với giao dịch nào không
    connection.execute("SELECT COUNT(*) FROM giaodich WHERE DANHMUC_ID = %s", (category_id,))
    count = connection.fetchone()[0]

    if count > 0:
        flash("Không thể xóa danh mục vì có giao dịch liên quan.", "danger")
    else:
        # Xóa danh mục
        connection.execute("DELETE FROM danhmuc WHERE ID = %s", (category_id,))
        mysql.connection.commit()
        flash("Danh mục đã được xóa thành công.", "info")

    connection.close()
    return redirect(url_for('categories_bp.categories'))


