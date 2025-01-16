-- Tạo cơ sở dữ liệu
DROP DATABASE IF EXISTS finly_db;
CREATE DATABASE finly_db;
USE finly_db;

-- Bảng NGUOIDUNG
CREATE TABLE NGUOIDUNG (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    USERNAME VARCHAR(50) NOT NULL UNIQUE,
    EMAIL VARCHAR(100) NOT NULL UNIQUE,
    PASSWORD VARCHAR(100) NOT NULL,
    HOTEN VARCHAR(100) NOT NULL
);

-- Bảng NGUONTHU
CREATE TABLE NGUONTHU (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    NGUOIDUNG_ID INT NOT NULL,
    type ENUM('cash', 'card', 'wallet', 'bank') NOT NULL,
    card_type ENUM('ATM', 'Master', 'Visa') NULL,
    SOTHE VARCHAR(20) NULL,
    SODU DECIMAL(15, 2) DEFAULT 0,
    status TINYINT(1) DEFAULT 1,
    FOREIGN KEY (NGUOIDUNG_ID) REFERENCES NGUOIDUNG(ID) ON DELETE CASCADE
);

-- Bảng DANHMUC
CREATE TABLE DANHMUC (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    TEN VARCHAR(50) NOT NULL UNIQUE,
    type ENUM('expense', 'income') NOT NULL
);

-- Thêm danh mục mặc định
INSERT INTO DANHMUC (TEN, type)
VALUES 
('Điện - Nước - Gas', 'expense'),
('Ăn uống', 'expense'),
('Mua sắm', 'expense'),
('Giải trí', 'expense'),
('Đầu tư', 'expense'),
('Học tập', 'expense'),
('Lương', 'income'),
('Trợ cấp', 'income'),
('Thưởng', 'income'),
('Thu hồi nợ', 'income');

-- Bảng GIAODICH
CREATE TABLE GIAODICH (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    NGUOIDUNG_ID INT NOT NULL,
    NGUONTHU_ID INT,
    DANHMUC_ID INT NOT NULL,
    type ENUM('income', 'expense') NOT NULL,
    SOTIEN DECIMAL(15, 2) NOT NULL,
    date DATE NULL,
    MOTA TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (NGUOIDUNG_ID) REFERENCES NGUOIDUNG(ID) ON DELETE CASCADE,
    FOREIGN KEY (NGUONTHU_ID) REFERENCES NGUONTHU(ID) ON DELETE SET NULL,
    FOREIGN KEY (DANHMUC_ID) REFERENCES DANHMUC(ID) ON DELETE RESTRICT
);

-- Thêm người dùng và nguồn thu mặc định
INSERT INTO NGUOIDUNG (USERNAME, EMAIL, PASSWORD, HOTEN)
VALUES
('test', 'test@gmail.com', '$2b$12$3wLTNfEb2YELcpCFchUcFO6sw6bke2ecIEfFhRQxfNZXuWtqL2aFe', 'Alex Nguyễn');

-- Lấy ID người dùng vừa thêm để tạo nguồn thu mặc định
INSERT INTO NGUONTHU (NGUOIDUNG_ID, type, card_type, SOTHE, SODU, status)
VALUES
((SELECT ID FROM NGUOIDUNG WHERE USERNAME = 'test'), 'wallet', NULL, NULL, 0, 1);


-- Thêm giao dịch chi tiêu và thu nhập cho năm 2024
INSERT INTO GIAODICH (NGUOIDUNG_ID, NGUONTHU_ID, DANHMUC_ID, type, SOTIEN, date, MOTA)
VALUES
-- Tháng 1
(1, 1, 1, 'expense', 8000000, '2024-01-05', 'Thanh toán tiền điện'),
(1, 1, 2, 'expense', 4000000, '2024-01-10', 'Mua thực phẩm hàng ngày'),
(1, 1, 3, 'expense', 3000000, '2024-01-15', 'Mua đồ gia dụng'),
(1, 1, 4, 'expense', 2000000, '2024-01-20', 'Giải trí cuối tuần'),
(1, 1, 7, 'income', 9000000, '2024-01-07', 'Lương tháng 1'),
(1, 1, 8, 'income', 4000000, '2024-01-14', 'Trợ cấp gia đình'),
(1, 1, 9, 'income', 3000000, '2024-01-25', 'Thưởng quý 1'),

-- Tháng 2
(1, 1, 1, 'expense', 7000000, '2024-02-05', 'Hóa đơn tiền nước'),
(1, 1, 2, 'expense', 5000000, '2024-02-10', 'Mua thực phẩm cuối tuần'),
(1, 1, 3, 'expense', 3000000, '2024-02-15', 'Mua quần áo mới'),
(1, 1, 4, 'expense', 2000000, '2024-02-20', 'Xem phim cuối tuần'),
(1, 1, 7, 'income', 8000000, '2024-02-07', 'Lương tháng 2'),
(1, 1, 8, 'income', 4000000, '2024-02-14', 'Trợ cấp tháng 2'),
(1, 1, 9, 'income', 3000000, '2024-02-25', 'Thưởng lễ'),

-- Tháng 3
(1, 1, 1, 'expense', 9000000, '2024-03-05', 'Tiền điện tháng 3'),
(1, 1, 2, 'expense', 4000000, '2024-03-10', 'Thực phẩm hàng tuần'),
(1, 1, 3, 'expense', 3000000, '2024-03-15', 'Mua sắm gia đình'),
(1, 1, 4, 'expense', 2000000, '2024-03-20', 'Giải trí cuối tuần'),
(1, 1, 7, 'income', 9000000, '2024-03-07', 'Lương tháng 3'),
(1, 1, 8, 'income', 4000000, '2024-03-14', 'Trợ cấp gia đình'),
(1, 1, 9, 'income', 3000000, '2024-03-25', 'Thưởng tháng 3'),

-- Tháng 4
(1, 1, 1, 'expense', 8000000, '2024-04-05', 'Tiền điện tháng 4'),
(1, 1, 2, 'expense', 5000000, '2024-04-10', 'Mua thực phẩm hàng ngày'),
(1, 1, 3, 'expense', 4000000, '2024-04-15', 'Mua đồ gia dụng mới'),
(1, 1, 4, 'expense', 3000000, '2024-04-20', 'Vé xem phim cuối tuần'),
(1, 1, 7, 'income', 10000000, '2024-04-07', 'Lương tháng 4'),
(1, 1, 8, 'income', 5000000, '2024-04-14', 'Hỗ trợ gia đình'),
(1, 1, 9, 'income', 4000000, '2024-04-25', 'Thưởng lễ'),

-- Tháng 5
(1, 1, 1, 'expense', 10000000, '2024-05-05', 'Tiền điện tháng 5'),
(1, 1, 2, 'expense', 4000000, '2024-05-10', 'Mua thực phẩm cuối tháng'),
(1, 1, 3, 'expense', 5000000, '2024-05-15', 'Mua đồ gia dụng mới'),
(1, 1, 4, 'expense', 3000000, '2024-05-20', 'Xem phim cuối tuần'),
(1, 1, 7, 'income', 10000000, '2024-05-07', 'Lương tháng 5'),
(1, 1, 8, 'income', 4000000, '2024-05-14', 'Trợ cấp gia đình tháng 5'),
(1, 1, 9, 'income', 3000000, '2024-05-25', 'Thưởng lễ tháng 5'),

-- Tháng 6
(1, 1, 1, 'expense', 8000000, '2024-06-05', 'Tiền điện tháng 6'),
(1, 1, 2, 'expense', 6000000, '2024-06-10', 'Thực phẩm cuối tuần'),
(1, 1, 3, 'expense', 3000000, '2024-06-15', 'Mua đồ gia dụng mới'),
(1, 1, 4, 'expense', 4000000, '2024-06-20', 'Xem phim cuối tuần'),
(1, 1, 7, 'income', 9000000, '2024-06-07', 'Lương tháng 6'),
(1, 1, 8, 'income', 5000000, '2024-06-14', 'Trợ cấp gia đình tháng 6'),
(1, 1, 9, 'income', 3000000, '2024-06-25', 'Thưởng tháng 6'),

-- Tháng 7
(1, 1, 1, 'expense', 8000000, '2024-07-05', 'Tiền điện tháng 7'),
(1, 1, 2, 'expense', 4000000, '2024-07-10', 'Mua thực phẩm hàng tuần'),
(1, 1, 3, 'expense', 5000000, '2024-07-15', 'Mua đồ gia dụng'),
(1, 1, 4, 'expense', 2000000, '2024-07-20', 'Giải trí cuối tuần'),
(1, 1, 7, 'income', 9000000, '2024-07-07', 'Lương tháng 7'),
(1, 1, 8, 'income', 4000000, '2024-07-14', 'Trợ cấp tháng 7'),
(1, 1, 9, 'income', 3000000, '2024-07-25', 'Thưởng tháng 7'),

-- Tháng 8
(1, 1, 1, 'expense', 9000000, '2024-08-05', 'Tiền điện tháng 8'),
(1, 1, 2, 'expense', 4000000, '2024-08-10', 'Mua thực phẩm hàng tuần'),
(1, 1, 3, 'expense', 3000000, '2024-08-15', 'Mua đồ gia dụng mới'),
(1, 1, 4, 'expense', 3000000, '2024-08-20', 'Xem phim cuối tuần'),
(1, 1, 7, 'income', 10000000, '2024-08-07', 'Lương tháng 8'),
(1, 1, 8, 'income', 5000000, '2024-08-14', 'Trợ cấp gia đình tháng 8'),
(1, 1, 9, 'income', 4000000, '2024-08-25', 'Thưởng tháng 8'),

-- Tháng 9
(1, 1, 1, 'expense', 7000000, '2024-09-05', 'Tiền điện tháng 9'),
(1, 1, 2, 'expense', 5000000, '2024-09-10', 'Mua thực phẩm hàng ngày'),
(1, 1, 3, 'expense', 4000000, '2024-09-15', 'Mua đồ gia dụng mới'),
(1, 1, 4, 'expense', 3000000, '2024-09-20', 'Giải trí cuối tuần'),
(1, 1, 7, 'income', 10000000, '2024-09-07', 'Lương tháng 9'),
(1, 1, 8, 'income', 5000000, '2024-09-14', 'Trợ cấp gia đình tháng 9'),
(1, 1, 9, 'income', 4000000, '2024-09-25', 'Thưởng tháng 9'),

-- Tháng 10
(1, 1, 1, 'expense', 9000000, '2024-10-05', 'Tiền điện tháng 10'),
(1, 1, 2, 'expense', 4000000, '2024-10-10', 'Mua thực phẩm cuối tháng'),
(1, 1, 3, 'expense', 4000000, '2024-10-15', 'Mua đồ gia dụng mới'),
(1, 1, 4, 'expense', 3000000, '2024-10-20', 'Giải trí cuối tuần'),
(1, 1, 7, 'income', 10000000, '2024-10-07', 'Lương tháng 10'),
(1, 1, 8, 'income', 5000000, '2024-10-14', 'Trợ cấp gia đình tháng 10'),
(1, 1, 9, 'income', 4000000, '2024-10-25', 'Thưởng tháng 10'),

-- Tháng 11
(1, 1, 1, 'expense', 8000000, '2024-11-05', 'Tiền điện tháng 11'),
(1, 1, 2, 'expense', 5000000, '2024-11-10', 'Mua thực phẩm cuối tuần'),
(1, 1, 3, 'expense', 3000000, '2024-11-15', 'Mua đồ gia dụng mới'),
(1, 1, 4, 'expense', 2000000, '2024-11-20', 'Xem phim cuối tuần'),
(1, 1, 7, 'income', 10000000, '2024-11-07', 'Lương tháng 11'),
(1, 1, 8, 'income', 5000000, '2024-11-14', 'Trợ cấp gia đình tháng 11'),
(1, 1, 9, 'income', 4000000, '2024-11-25', 'Thưởng tháng 11'),

-- Tháng 12
(1, 1, 1, 'expense', 10000000, '2024-12-05', 'Tiền điện tháng 12'),
(1, 1, 2, 'expense', 6000000, '2024-12-10', 'Mua thực phẩm cuối tháng'),
(1, 1, 3, 'expense', 4000000, '2024-12-15', 'Mua đồ gia dụng mới'),
(1, 1, 4, 'expense', 3000000, '2024-12-20', 'Giải trí cuối tuần'),
(1, 1, 7, 'income', 10000000, '2024-12-07', 'Lương tháng 12'),
(1, 1, 8, 'income', 5000000, '2024-12-14', 'Trợ cấp gia đình tháng 12'),
(1, 1, 9, 'income', 4000000, '2024-12-25', 'Thưởng tháng 12');


-- Thêm giao dịch trong tháng 1 năm 2025
INSERT INTO GIAODICH (NGUOIDUNG_ID, NGUONTHU_ID, DANHMUC_ID, type, SOTIEN, date, MOTA)
VALUES
(1, 1, 1, 'expense', 200000, '2025-01-05', 'Thanh toán tiền điện đầu năm'),
(1, 1, 2, 'expense', 180000, '2025-01-10', 'Mua thực phẩm đầu tháng'),
(1, 1, 3, 'expense', 250000, '2025-01-15', 'Mua sắm đồ dùng cá nhân'),
(1, 1, 4, 'expense', 120000, '2025-01-20', 'Giải trí đầu năm'),
(1, 1, 7, 'income', 5000000, '2025-01-07', 'Nhận lương tháng 1');
