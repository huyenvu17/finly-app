from flask import Blueprint, render_template, request, current_app 
from flask_login import current_user, login_required
from helpers.helpers import get_source_title
from flask_mysqldb import MySQL
from datetime import datetime

mysql = MySQL()

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/')
@login_required
def dashboard():
    current_date = datetime.now()
    default_year = current_date.year

    # Lấy năm cho Xu hướng Chi tiêu và tháng cho Tổng quan
    selected_year_trend = int(request.args.get('year', default_year))
    default_month_year = f"{current_date.year}-{current_date.month:02d}"  # Mặc định tháng hiện tại
    selected_month_year = request.args.get('month', default_month_year)  # Giá trị từ input type="month"
    selected_year, selected_month = map(int, selected_month_year.split('-'))

    connection = mysql.connection.cursor()
  
    # Truy vấn danh mục
    connection.execute("SELECT ID, TEN FROM danhmuc WHERE type = 'expense'")
    expense_categories = connection.fetchall()
    connection.execute("SELECT ID, TEN FROM danhmuc WHERE type = 'income'")
    income_categories = connection.fetchall()

    # Dữ liệu Tổng quan
    connection.execute("""
        SELECT SUM(SOTIEN)
        FROM giaodich
        WHERE TYPE = 'expense'
          AND NGUOIDUNG_ID = %s
          AND MONTH(date) = %s
          AND YEAR(date) = %s
    """, [current_user.id, selected_month, selected_year])
    total_expense = connection.fetchone()[0] or 0

    connection.execute("""
        SELECT SUM(SOTIEN)
        FROM giaodich
        WHERE TYPE = 'income'
          AND NGUOIDUNG_ID = %s
          AND MONTH(date) = %s
          AND YEAR(date) = %s
    """, [current_user.id, selected_month, selected_year])
    total_income = connection.fetchone()[0] or 0

    # Điều kiện chung
    filters = "WHERE g.NGUOIDUNG_ID = %s AND MONTH(date) = %s AND YEAR(date) = %s"
    params = [current_user.id, selected_month, selected_year]

    # Truy vấn giao dịch chi tiêu
    connection.execute(f"""
        SELECT d.TEN AS DanhMuc, SUM(g.SOTIEN) AS TongSoTien, d.type, d.ID
        FROM giaodich g
        JOIN danhmuc d ON g.DANHMUC_ID = d.ID
        {filters} AND g.TYPE = 'expense'
        GROUP BY g.DANHMUC_ID, d.TEN, d.ID
        ORDER BY TongSoTien DESC
    """, params)
    expense_stats = connection.fetchall()

    # Truy vấn giao dịch thu nhập
    connection.execute(f"""
        SELECT d.TEN AS DanhMuc, SUM(g.SOTIEN) AS TongSoTien, d.type, d.ID
        FROM giaodich g
        JOIN danhmuc d ON g.DANHMUC_ID = d.ID
        {filters} AND g.TYPE = 'income'
        GROUP BY g.DANHMUC_ID, d.TEN, d.ID
        ORDER BY TongSoTien DESC
    """, params)
    income_stats = connection.fetchall()

    # chart 
    # Tính tổng tất cả giao dịch chi tiêu
    total_expense_amount = sum(row[1] for row in expense_stats)

    # Biểu đồ chi tiêu
    chart_expense_data = [
        {
            'category': row[0],
            'percentage': round((row[1] / total_expense_amount) * 100, 2) if total_expense_amount > 0 else 0,
            'type': row[2],
        }
        for row in expense_stats
    ]
    # Tính tổng tất cả giao dịch thu nhập
    total_income_amount = sum(row[1] for row in income_stats)
    # Biểu đồ thu nhập
    chart_income_data = [
        {
            'category': row[0],
            'percentage': round((row[1] / total_income_amount) * 100, 2) if total_income_amount > 0 else 0,
            'type': row[2],
        }
        for row in income_stats
    ]

    # Dữ liệu Xu hướng Chi tiêu
    connection.execute("""
        SELECT MONTH(date) AS month, SUM(SOTIEN) AS total
        FROM giaodich
        WHERE NGUOIDUNG_ID = %s AND TYPE = 'expense' AND YEAR(date) = %s
        GROUP BY MONTH(date)
        ORDER BY MONTH(date)
    """, [current_user.id, selected_year_trend])
    expense_monthly = {row[0]: row[1] for row in connection.fetchall()}

    connection.execute("""
        SELECT MONTH(date) AS month, SUM(SOTIEN) AS total
        FROM giaodich
        WHERE NGUOIDUNG_ID = %s AND TYPE = 'income' AND YEAR(date) = %s
        GROUP BY MONTH(date)
        ORDER BY MONTH(date)
    """, [current_user.id, selected_year_trend])
    income_monthly = {row[0]: row[1] for row in connection.fetchall()}

    # Tạo danh sách đầy đủ 12 tháng
    expense_monthly_data = [expense_monthly.get(i, 0) for i in range(1, 13)]
    income_monthly_data = [income_monthly.get(i, 0) for i in range(1, 13)]

    # Truy vấn danh sách nguồn tiền
    connection.execute("""
        SELECT status, card_type, type, sothe, sodu FROM nguonthu WHERE NGUOIDUNG_ID = %s
    """, [current_user.id])
    all_sources = connection.fetchall()
    # Lấy 3 mục đầu tiên
    top_sources = all_sources[:3]
    sources_types = [(source[0], get_source_title(source[2])) for source in all_sources]
    connection.close()

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    return render_template(
        'dashboard.html',
        request=request,
        username=current_user.username,
        expense_categories=expense_categories,
        income_categories=income_categories,
        selected_year=selected_year,
        selected_month_year=selected_month_year,
        total_expense=total_expense,
        total_income=total_income,
        expense_stats=expense_stats,
        income_stats=income_stats,
        chart_expense_data=chart_expense_data,
        chart_income_data=chart_income_data,
        expense_monthly_data=expense_monthly_data,
        income_monthly_data=income_monthly_data,
        months=months,
        top_sources=top_sources,
        sources_types=sources_types
    )