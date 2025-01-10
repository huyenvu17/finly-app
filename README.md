# Finly App
Finly là ứng dụng quản lý tài chính cá nhân cho phép người dùng quản lý việc thu chi và theo dõi xu hướng chi tiêu.

## Chức năng
- Đăng ký/ Đăng nhập
- Quản lý giao dịch chi tiêu/thu nhập (xem, thêm, xóa, sửa giao dịch)
- Quản lý nguồn tiền (xem, thêm, xóa, sửa nguồn tiền)
- Thống kê giao dịch theo phân loại
- Thống kê xu hướng chi tiêu
- Quản lý hồ sơ (Cập nhật hồ sơ, thay đổi mật khẩu)
- Liên hệ

## Hướng dẫn cài đặt

1. **Tải source code từ github: **
    ```bash
    git clone https://github.com/huyenvu17/finly-app.git
    ```

2. **Đi đến đường dẫn thư mục: **
    ```bash
    cd finly-app
    ```

3. **Tạo môi trường ảo: **
    ```bash
    python -m venv venv
    ```

4. **Kích hoạt môi trường ảo: **
    - Trên Windows:
      ```bash
      venv\Scripts\activate
      ```
    - Trên macOS/Linux:
      ```bash
      source venv/bin/activate
      ```

5. **Tải các dependencies cần thiết được liệt kê trong requirements.txt:**
    ```bash
    pip install -r requirements.txt
    ```

6. **Khởi động ứng dụng:**
    ```bash
    python app.py
    ```

## Người thực hiện

- Vũ Ngọc Huyền   - 23210228
- Lê Hàn Trúc Chi - 23210200


## Tài liệu tham khảo
- https://flask.palletsprojects.com/en/stable
- https://www.tutorialspoint.com/flask/index.htm

## Quyền sử dụng
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.