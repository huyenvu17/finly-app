from flask_mysqldb import MySQL

mysql = MySQL()

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
