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
('minhvule', 'minhvule@gmail.com', '11111', 'Lê Minh Vũ');

-- Lấy ID người dùng vừa thêm để tạo nguồn thu mặc định
INSERT INTO NGUONTHU (NGUOIDUNG_ID, type, card_type, SOTHE, SODU, status)
VALUES
((SELECT ID FROM NGUOIDUNG WHERE USERNAME = 'minhvule'), 'wallet', NULL, NULL, 0, 1);


-- 20 giao dịch trong năm 2024
INSERT INTO GIAODICH (NGUOIDUNG_ID, NGUONTHU_ID, DANHMUC_ID, type, SOTIEN, date, MOTA)
VALUES
-- Giao dịch chi tiêu
(1, 1, 1, 'expense', 150000, '2024-01-05', 'Thanh toán tiền điện'),
(1, 1, 2, 'expense', 200000, '2024-02-10', 'Mua thực phẩm'),
(1, 1, 3, 'expense', 250000, '2024-03-15', 'Mua sắm đầu tháng'),
(1, 1, 4, 'expense', 120000, '2024-04-20', 'Giải trí cuối tuần'),
(1, 1, 5, 'expense', 180000, '2024-05-25', 'Đầu tư nhỏ lẻ'),
(1, 1, 6, 'expense', 150000, '2024-06-12', 'Đóng học phí kỳ 1'),
(1, 1, 1, 'expense', 300000, '2024-07-05', 'Thanh toán tiền nước'),
(1, 1, 2, 'expense', 250000, '2024-08-10', 'Mua thực phẩm cuối tuần'),
(1, 1, 3, 'expense', 400000, '2024-09-15', 'Mua đồ gia dụng'),
(1, 1, 4, 'expense', 210000, '2024-10-01', 'Vé xem phim cho cả nhà'),
-- Giao dịch thu nhập
(1, 1, 7, 'income', 5000000, '2024-01-07', 'Lương tháng 1'),
(1, 1, 8, 'income', 350000, '2024-02-14', 'Trợ cấp từ gia đình'),
(1, 1, 9, 'income', 1200000, '2024-03-19', 'Thưởng quý 1'),
(1, 1, 10, 'income', 200000, '2024-04-25', 'Thu hồi nợ từ bạn bè'),
(1, 1, 7, 'income', 5500000, '2024-05-07', 'Lương tháng 5'),
(1, 1, 8, 'income', 400000, '2024-06-01', 'Trợ cấp cho gia đình'),
(1, 1, 9, 'income', 1200000, '2024-07-10', 'Thưởng giữa năm'),
(1, 1, 10, 'income', 250000, '2024-08-25', 'Thu hồi nợ từ đồng nghiệp'),
(1, 1, 7, 'income', 5000000, '2024-09-07', 'Lương tháng 9'),
(1, 1, 8, 'income', 350000, '2024-10-25', 'Trợ cấp tháng 10');

-- 5 giao dịch trong tháng 1 năm 2025
INSERT INTO GIAODICH (NGUOIDUNG_ID, NGUONTHU_ID, DANHMUC_ID, type, SOTIEN, date, MOTA)
VALUES
(1, 1, 1, 'expense', 200000, '2025-01-05', 'Thanh toán tiền điện đầu năm'),
(1, 1, 2, 'expense', 180000, '2025-01-10', 'Mua thực phẩm đầu tháng'),
(1, 1, 3, 'expense', 250000, '2025-01-15', 'Mua sắm đồ dùng cá nhân'),
(1, 1, 4, 'expense', 120000, '2025-01-20', 'Giải trí đầu năm'),
(1, 1, 7, 'income', 5000000, '2025-01-07', 'Nhận lương tháng 1');
