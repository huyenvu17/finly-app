# Finly App
Finly là ứng dụng quản lý tài chính cá nhân cho phép người dùng quản lý việc thu chi và theo dõi xu hướng chi tiêu.

## Chức năng
- Đăng ký/ Đăng nhập
- Quản lý giao dịch chi tiêu/thu nhập
- Quản lý nguồn thu
- Quản lý danh mục
- Quản lý hồ sơ
- Thống kê giao dịch theo phân loại theo tháng
- Thống kê xu hướng chi tiêu theo năm
- Liên hệ

## Ngôn ngữ sử dung
- Backend:
    - Python
    - Flask
- Frontend:
    - HTML, CSS, Javascript
    - Bootstrap
- Database:
    - MySQL

## Hướng dẫn cài đặt

1. **Tải source code từ github:**
    ```bash
    git clone https://github.com/huyenvu17/finly-app.git
    cd finly-app
    ```

2. **Cài đặt cơ sở dữ liệu:**
    - Đảm bảo MySQL đã được cài đặt trên thiết bị. Nếu chưa có, có thể tải từ [MySQL Downloads](https://dev.mysql.com/downloads/).
    - Sử dụng phần mềm thao tác với cơ sở dữ liệu như MySQL Workbench
    - Tạo database mới:
        ```sql
        CREATE DATABASE finly_db;
        ```
    - Chạy script trong file 
        ```sql
        static/sql/finly.sql
        ```

3. **Cài đặt phần mềm cần thiết**
    1. Python
    - Kiểm tra Python đã được cài đặt hay chưa, sử dụng lệnh:
    ```bash
    python --version
    ```
    - Nếu chưa cài đặt Python, tải phiên bản mới nhất từ [Python.org](https://www.python.org/downloads/).
    2. MySQL


4. **Tạo môi trường ảo:**
    ```bash
    python -m venv venv
    source venv/bin/activate    # Trên Linux/MacOS
    venv\Scripts\activate       # Trên Windows
    ```

5. **Tải các dependencies cần thiết được liệt kê trong requirements.txt:**
    ```bash
    pip install -r requirements.txt
    ```

6. **Cập nhật cấu hình**
    ```bash
    Cập nhật thông tin tài khoản MySQL server (MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD) tại /config.py
    ```

7. **Chạy ứng dụng:**
    ```bash
    python app.py
    ```

8. **Truy cập ứng dụng:**
    ```bash
    Mở trình duyệt và truy cập `http://localhost:5000`.
    ```

## Người thực hiện

- Vũ Ngọc Huyền   - 23210228
- Lê Hàn Trúc Chi - 23210200


## Tài liệu tham khảo
- https://flask.palletsprojects.com/en/stable
- https://www.tutorialspoint.com/flask/index.htm

## Quyền sử dụng
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.