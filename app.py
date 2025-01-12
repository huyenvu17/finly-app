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

# Quản lý phiên đăng nhập người dùng
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

#login
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

# register
@app.route('/register', methods=['GET', 'POST'])
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

            flash("Đăng ký thành công! Hãy đăng nhập.")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Có lỗi xảy ra trong quá trình đăng ký: {e}", "danger")
            return redirect(url_for('register'))
    return render_template('register.html')

# logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Bạn đã đăng xuất.")
    return redirect(url_for('login'))

# dashboard
@app.route('/')
@login_required
def dashboard():
    # Truy vấn danh sách nguồn thu
    connection = mysql.connection.cursor()
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
        SELECT status, card_type, type, sothe, sodu FROM nguonthu WHERE NGUOIDUNG_ID = %s
    """, [current_user.id])
    all_sources = connection.fetchall()
    # Lấy 3 mục đầu tiên
    top_sources = all_sources[:3]
    sources_types = [(source[0], get_source_title(source[2])) for source in all_sources]
    connection.close()

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    expense_monthly_data = [expense_monthly.get(i, 0) for i in range(1, 13)]
    income_monthly_data = [income_monthly.get(i, 0) for i in range(1, 13)]

    return render_template(
        'dashboard.html',
        request=request,
        username=current_user.username,
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
        sources_types=sources_types
    )

# transactions
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

# add transactions
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

#sources
@app.route('/sources')
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
@app.route('/add_source', methods=['POST'])
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


# categories
@app.route('/categories')
@login_required
def categories():
    return render_template('categories.html', categories=get_categories())

# add category
@app.route('/add_category', methods=['POST'])
@login_required
def add_category():
    # Get data from the form
    cateName = request.form.get('cateName')
    cateType = request.form.get('cateType')

    try:
        # Insert into the database
        connection = mysql.connection.cursor()
        connection.execute("""
            INSERT INTO danhmuc (TEN, TYPE)
            VALUES (%s, %s)
        """, (cateName, cateType))
        mysql.connection.commit()
        connection.close()
    

        flash("Danh mục đã được thêm thành công!", "success")
    except Exception as e:
        flash(f"Có lỗi xảy ra: {e}", "danger")

    return redirect(url_for('categories'))

# contact
@app.route('/contact')
@login_required
def contact():
    return render_template('contact.html')

# profile
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

def get_categories():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM danhmuc")
    categories = cur.fetchall()
    cur.close()
    return categories

def get_source_title(source_type):
    titles = {
        "cash": "Tiền mặt",
        "card": "Thẻ",
        "wallet": "Ví Finly",
        "bank": "Chuyển khoản ngân hàng"
    }
    return titles.get(source_type, "Nguồn thu khác")

def format_number(value):
    return "{:,.0f}".format(value).replace(",", ".")

app.jinja_env.filters['format_number'] = format_number
app.jinja_env.filters['get_source_title'] = get_source_title

if __name__ == '__main__':
    app.run(debug=True)
