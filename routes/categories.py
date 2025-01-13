from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from flask_mysqldb import MySQL
from helpers.helpers import get_categories

mysql = MySQL()

categories_bp = Blueprint('categories_bp', __name__)

# categories
@categories_bp.route('/categories')
@login_required
def categories():
    return render_template('categories.html', categories=get_categories())

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

    return redirect(url_for('categories'))
