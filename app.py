from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_mysqldb import MySQL
import bcrypt
from datetime import timedelta

app = Flask(__name__)
app.config.from_object("config.Config")

# Kết nối MySQL
mysql = MySQL(app)

# Cấu hình Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.remember_cookie_duration = timedelta(days=7)

# Model người dùng
class User(UserMixin):
    def __init__(self, id, username, email, hoten):
        self.id = id
        self.username = username
        self.email = email
        self.hoten = hoten

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
        return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
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
            flash("Đăng nhập thành công!")
            return redirect(url_for('dashboard'))
        else:
            flash("Email hoặc mật khẩu không chính xác.")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        hoten = request.form['hoten']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        connection = mysql.connection.cursor()
        connection.execute("INSERT INTO nguoidung (USERNAME, HOTEN, EMAIL, PASSWORD) VALUES (%s, %s, %s, %s)",
                    (username, hoten, email, hashed_password.decode('utf-8')))
        mysql.connection.commit()
        connection.close()

        flash("Đăng ký thành công! Hãy đăng nhập.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/')
@login_required
def dashboard():
    # Truy vấn danh sách nguồn thu
    connection = mysql.connection.cursor()
    connection.execute("SELECT ID, TIEUDE FROM nguonthu WHERE NGUOIDUNG_ID = %s", [current_user.id])
    sources = connection.fetchall()
    # Truy vấn danh mục
    connection.execute("SELECT ID, TEN FROM danhmuc WHERE type = 'expense'")
    expense_categories = connection.fetchall()
    connection.execute("SELECT ID, TEN FROM danhmuc WHERE type = 'income'")
    income_categories = connection.fetchall()

    # Truy vấn giao dịch
    connection.execute("SELECT SUM(SOTIEN) FROM giaodich WHERE TYPE = 'expense' AND NGUOIDUNG_ID = %s", [current_user.id])
    total_expense = connection.fetchone()[0] or 0 
    
   
    connection.execute("SELECT SUM(SOTIEN) FROM giaodich WHERE TYPE = 'income' AND NGUOIDUNG_ID = %s", [current_user.id])
    total_income = connection.fetchone()[0] or 0 

    # Lấy thống kê tổng số tiền theo danh mục
    connection.execute("""
        SELECT 
            d.TEN AS DanhMuc, 
            SUM(g.SOTIEN) AS TongSoTien,
            d.type as Loai, 
            d.ID
        FROM 
            giaodich g
        JOIN 
            danhmuc d ON g.DANHMUC_ID = d.ID
        WHERE 
            g.NGUOIDUNG_ID = %s
            AND g.TYPE = 'expense'
        GROUP BY 
            g.DANHMUC_ID, d.TEN, d.ID
        ORDER BY 
            TongSoTien DESC
    """, [current_user.id])
    expense_stats = connection.fetchall()

    connection.execute("""
        SELECT 
            d.TEN AS DanhMuc, 
            SUM(g.SOTIEN) AS TongSoTien,
            d.type as Loai, 
            d.ID
        FROM 
            giaodich g
        JOIN 
            danhmuc d ON g.DANHMUC_ID = d.ID
        WHERE 
            g.NGUOIDUNG_ID = %s
            AND g.TYPE = 'income'
        GROUP BY 
            g.DANHMUC_ID, d.TEN, d.ID
        ORDER BY 
            TongSoTien DESC
    """, [current_user.id])
    income_stats = connection.fetchall()

    # chart 
    # Tính tổng tất cả giao dịch
    total_expense_amount = sum(row[1] for row in expense_stats)

    # Chuyển dữ liệu thành danh sách các dict với tỷ lệ phần trăm
    chart_expense_data = [
        {
            'category': row[0],
            'percentage': round((row[1] / total_expense_amount) * 100, 2) if total_expense_amount > 0 else 0,
            'type': row[2],
        }
        for row in expense_stats
    ]
    total_income_amount = sum(row[1] for row in income_stats)
    chart_income_data = [
        {
            'category': row[0],
            'percentage': round((row[1] / total_income_amount) * 100, 2) if total_income_amount > 0 else 0,
            'type': row[2],
        }
        for row in income_stats
    ]


    # Dữ liệu xu hướng chi tiêu
    # Tổng số tiền theo từng tháng cho biểu đồ cột
    connection.execute("""
        SELECT MONTH(date) AS month, SUM(SOTIEN) AS total
        FROM giaodich
        WHERE NGUOIDUNG_ID = %s AND TYPE = 'expense'
        GROUP BY MONTH(date)
        ORDER BY MONTH(date)
    """, [current_user.id])
    expense_monthly = {row[0]: row[1] for row in connection.fetchall()}

    connection.execute("""
        SELECT MONTH(date) AS month, SUM(SOTIEN) AS total
        FROM giaodich
        WHERE NGUOIDUNG_ID = %s AND TYPE = 'income'
        GROUP BY MONTH(date)
        ORDER BY MONTH(date)
    """, [current_user.id])
    income_monthly = {row[0]: row[1] for row in connection.fetchall()}

    # Truy vấn danh sách nguồn tiền
    connection.execute("""
        SELECT tieude, status, card_type, type, sothe, sodu FROM nguonthu WHERE NGUOIDUNG_ID = %s
    """, [current_user.id])
    all_sources = connection.fetchall()

    # Lấy 3 mục đầu tiên
    top_sources = all_sources[:3]

    connection.close()

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    expense_monthly_data = [expense_monthly.get(i, 0) for i in range(1, 13)]
    income_monthly_data = [income_monthly.get(i, 0) for i in range(1, 13)]

    return render_template(
        'dashboard.html',
        request=request,
        username=current_user.username,
        sources=sources,
        expense_categories=expense_categories,
        income_categories=income_categories,
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
    )

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Bạn đã đăng xuất.")
    return redirect(url_for('login'))

@app.route('/add_transaction', methods=['POST'])
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
        return redirect(url_for('dashboard'))

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

    return redirect(url_for('dashboard'))


@app.route('/transactions', methods=['GET'])
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
                           categories=get_categories(),  # Hàm lấy danh mục
                           transaction_type=transaction_type,
                           search_query=search_query)

@app.route('/sources')
@login_required
def sources():
    connection = mysql.connection.cursor()
    connection.execute("SELECT tieude, status, card_type, type, sothe, sodu FROM nguonthu WHERE NGUOIDUNG_ID = %s", [current_user.id])
    sources = connection.fetchall()
    connection.close()
    
    return render_template('sources.html', sources=sources)

@app.route('/add_source', methods=['POST'])
@login_required
def add_source():
    title = request.form['title']
    source_type = request.form['type']
    card_type = request.form.get('card_type')  # Chỉ có giá trị nếu type = card
    status = int(request.form['status'])

    try:
        connection = mysql.connection.cursor()
        connection.execute("""
            INSERT INTO nguonthu (NGUOIDUNG_ID, TIEUDE, TYPE, card_type, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (current_user.id, title, source_type, card_type, status))
        mysql.connection.commit()
        connection.close()
        flash("Nguồn thu đã được thêm thành công!", "success")
    except Exception as e:
        flash(f"Có lỗi xảy ra: {e}", "danger")

    return redirect(url_for('sources'))



@app.route('/contact')
@login_required
def contact():
    return render_template('contact.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

def get_categories():
    cur = mysql.connection.cursor()
    cur.execute("SELECT ID, TEN FROM danhmuc")
    categories = cur.fetchall()
    cur.close()
    return categories

def format_number(value):
    return "{:,.0f}".format(value).replace(",", ".")

app.jinja_env.filters['format_number'] = format_number


if __name__ == '__main__':
    app.run(debug=True)
