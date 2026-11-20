# MergeSort Cutoff

## 1. Giới thiệu

Thí nghiệm tìm giá trị CUTOFF phù hợp cho thuật toán MergeSort kết hợp Insertion Sort

## 2. Cấu trúc dự án

- `src/main/java/`: Mã nguồn Java.
- `phan_tich/`: Script Python phân tích kết quả.
- `du_lieu/`: Dữ liệu mẫu.
- `ket_qua/`: Dữ liệu CSV, bảng thống kê và biểu đồ.
- `bao_cao/`: Báo cáo thực nghiệm.

## 3. Môi trường thực nghiệm

- CPU: Intel Core i7-10610U @ 1.80GHz, RAM: 16GB.
- Hệ điều hành: Windows 64-bit.
- Java: JDK 21.0.11.

## 4. Phương pháp thực nghiệm

- CUTOFF: 1, 2, 3, 5, 7, 10, 15, 20, 30, 50.
- Dữ liệu: Random, Sorted, Nearly Sorted, Reversed.
- Kích thước mảng: 10.000, 100.000, 1.000.000.
- Số lần đo: 40 / 30 / 10 lần tương ứng với từng kích thước.
- Có warm-up JVM, xáo trộn thứ tự CUTOFF và đo bằng `System.nanoTime()`.

## 5. Kết quả

Xem thư mục `ket_qua/` và báo cáo trong `bao_cao/`.

## 6. Tác giả

- Họ và tên: Tống Mỹ Quyên
- Mã sinh viên: 25021966
- Lớp: 2627I_UET.CS1058_8
