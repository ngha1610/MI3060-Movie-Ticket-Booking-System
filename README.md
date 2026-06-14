# HỆ THỐNG ĐẶT VÉ XEM PHIM
Bài tập lớn cuối kì 20252
Cấu trúc dữ liệu & Giải thuật
MI3060 - 169307 - HUST
## 1. Thông tin nhóm sinh viên
* Hồ Hồng Anh - 202419024
* Vũ Phương Anh - 202419026
* Lê Thị Lan Anh - 202419032
* Phạm Thị Ngọc Ánh - 202419034
* Nguyễn Như Nguyệt Hà - 202419052
## 2. Kiến trúc hệ thống
* Presentation Layer: file app.py, ui_components.py
* Business Logic Layer: folder controllers
* Data Structure Layer: folder data_structures
* Data Model Layer: folder models
* Bộ dữ liệu cơ sở: folder data
* Mã nguồn kiểm thử tự động: 4 file benchmark.py
* Bộ dữ liệu kiểm thử: folder DATA_TEST
* Class Diagram
## 3. Hướng dẫn sử dụng mã nguồn

### 3.1. Trải nghiệm trực tiếp (Live Demo)

Giảng viên có thể trải nghiệm toàn bộ giao diện và các chức năng của hệ thống thông qua phiên bản đã được triển khai trực tuyến mà không cần cài đặt mã nguồn.

> **Link Demo:** *(Cập nhật đường dẫn deploy của nhóm tại đây)*

---

### 3.2. Yêu cầu môi trường

Để chạy chương trình trên máy tính cá nhân, cần chuẩn bị:

* Python 3.10 hoặc mới hơn
* Git (khuyến nghị)
* Visual Studio Code hoặc IDE hỗ trợ Python
* Hệ điều hành Windows 10/11 (khuyến nghị)

Hệ thống không sử dụng cơ sở dữ liệu SQL mà lưu trữ dữ liệu bằng các tệp CSV.

---

### 3.3. Tải mã nguồn

Clone repository:

```bash
git clone https://github.com/ngha1610/MI3060-Movie-Ticket-Booking-System.git
```

Hoặc tải trực tiếp file ZIP từ GitHub rồi giải nén.

Sau đó mở thư mục dự án bằng Visual Studio Code hoặc IDE bất kỳ.

---

### 3.4. Cài đặt thư viện

Nếu có file `requirements.txt`, cài đặt toàn bộ thư viện bằng:

```bash
pip install -r requirements.txt
```

Nếu chưa có `requirements.txt`, có thể cài trực tiếp:

```bash
pip install streamlit
```

Trong trường hợp thiếu thư viện khác, cài đặt bằng:

```bash
pip install <tên_thư_viện>
```

---

### 3.5. Khởi chạy chương trình

Tại thư mục gốc của dự án, chạy:

```bash
streamlit run app.py
```

Sau khi thực thi, Streamlit sẽ tự động mở trình duyệt và hiển thị giao diện hệ thống.

---

### 3.6. Hướng dẫn sử dụng

Hệ thống hỗ trợ hai nhóm người dùng:

#### Đối với khách hàng

Người dùng có thể:

* Đăng ký tài khoản
* Đăng nhập
* Xem danh sách phim
* Tìm kiếm phim
* Xem thông tin chi tiết phim
* Chọn suất chiếu
* Chọn vị trí ghế
* Đặt vé
* Thanh toán
* Xem lịch sử đặt vé

#### Đối với quản trị viên

Quản trị viên có thể:

* Quản lý phim
* Thêm phim mới
* Chỉnh sửa thông tin phim
* Xóa phim
* Quản lý phòng chiếu
* Quản lý suất chiếu
* Quản lý người dùng
* Theo dõi doanh thu hệ thống
* Cập nhật dữ liệu

Mọi thay đổi sẽ được lưu trực tiếp vào các tệp dữ liệu trong thư mục `data/`.

---

### 3.7. Cấu trúc dự án

Dự án được thiết kế theo mô hình phân lớp nhằm tách biệt giao diện, xử lý nghiệp vụ và dữ liệu.

```
MI3060-Movie-Ticket-Booking-System/
│
├── app.py
├── ui_components.py
├── controllers/
├── models/
├── data_structures/
├── data/
├── DATA_TEST/
├── Class Diagram/
├── benchmark_1register.py
├── benchmark_2login.py
├── benchmark_admin.py
├── benchmark_customer.py
└── README.md
```

#### `data_structures/`

Đây là phần trọng tâm của đồ án.

Nhóm tự cài đặt các cấu trúc dữ liệu phục vụ việc quản lý hệ thống, không sử dụng các cấu trúc dữ liệu nâng cao có sẵn của Python ngoài các kiểu dữ liệu cơ bản.

Các cấu trúc dữ liệu được sử dụng để:

* Quản lý danh sách phim
* Quản lý người dùng
* Tra cứu dữ liệu
* Lưu lịch sử đặt vé
* Tối ưu tốc độ tìm kiếm và cập nhật dữ liệu

Giảng viên có thể kiểm tra trực tiếp các thao tác như:

* Insert
* Delete
* Search
* Update
* Traverse

được cài đặt trong các file thuộc thư mục này.

---

#### `controllers/`

Đây là lớp xử lý nghiệp vụ (Business Logic).

Các module trong thư mục này thực hiện:

* Xử lý đăng nhập
* Xử lý đăng ký
* Đặt vé
* Kiểm tra ghế trống
* Kiểm tra lịch chiếu
* Thêm/Sửa/Xóa dữ liệu
* Điều phối dữ liệu giữa giao diện và các cấu trúc dữ liệu

---

#### `models/`

Định nghĩa các lớp đối tượng theo hướng đối tượng (OOP).

Bao gồm các lớp như:

* User
* Admin
* Customer
* Movie
* Showtime
* Ticket
* Room

Các lớp này mô tả dữ liệu và thuộc tính của từng thực thể trong hệ thống.

---

#### `app.py`

Là điểm khởi chạy của hệ thống.

Chịu trách nhiệm:

* Khởi tạo ứng dụng Streamlit
* Điều hướng giữa các màn hình
* Quản lý Session State
* Điều phối luồng hiển thị

---

#### `ui_components.py`

Chứa các thành phần giao diện dùng chung.

Ví dụ:

* Hiển thị sơ đồ ghế
* Các bảng dữ liệu
* Các thành phần giao diện được tái sử dụng nhiều lần

---

#### `data/`

Lưu trữ toàn bộ dữ liệu của hệ thống dưới dạng CSV.

Bao gồm:

* users.csv
* movies.csv
* rooms.csv
* showtimes.csv
* tickets.csv

Khi chương trình chạy, dữ liệu sẽ được nạp từ các file này và cập nhật ngược lại sau khi người dùng thực hiện các thao tác.

---

#### `DATA_TEST/`

Chứa bộ dữ liệu phục vụ kiểm thử và đánh giá chương trình với nhiều trường hợp dữ liệu khác nhau.

---

#### `Class Diagram/`

Chứa sơ đồ lớp mô tả kiến trúc hướng đối tượng của toàn bộ hệ thống.

Giảng viên có thể tham khảo để hiểu nhanh mối quan hệ giữa các lớp trước khi đọc mã nguồn.

---

### 3.8. Benchmark đánh giá thuật toán

Để đánh giá hiệu năng của các cấu trúc dữ liệu và thuật toán, nhóm xây dựng bốn chương trình benchmark độc lập.

Các chương trình này chạy bằng Python và không phụ thuộc giao diện Streamlit.

#### Benchmark đăng ký

```bash
python benchmark_1register.py
```

Đánh giá thời gian xử lý khi thêm số lượng lớn người dùng mới vào hệ thống.

---

#### Benchmark đăng nhập

```bash
python benchmark_2login.py
```

Đánh giá tốc độ tìm kiếm và xác thực tài khoản, qua đó kiểm chứng hiệu quả của cấu trúc dữ liệu được sử dụng.

---

#### Benchmark quản trị viên

```bash
python benchmark_admin.py
```

Đo thời gian thực hiện các thao tác:

* Thêm dữ liệu
* Chỉnh sửa dữ liệu
* Xóa dữ liệu
* Cập nhật dữ liệu hàng loạt

---

#### Benchmark khách hàng

```bash
python benchmark_customer.py
```

Đo hiệu năng của các thao tác:

* Tìm kiếm phim
* Chọn suất chiếu
* Đặt vé
* Xử lý các thao tác của người dùng

---

### 3.9. Một số lưu ý

* Không thay đổi cấu trúc thư mục của dự án.
* Không đổi tên các file CSV trong thư mục `data/`.
* Luôn chạy chương trình từ thư mục gốc của dự án.
* Nếu chỉnh sửa trực tiếp các file CSV, cần đảm bảo đúng định dạng dữ liệu để chương trình có thể đọc được.
* Trường hợp phát sinh lỗi thiếu thư viện, chỉ cần cài đặt thư viện tương ứng bằng `pip`.

---

### 3.10. Hướng dẫn chấm điểm mã nguồn

Để thuận tiện trong quá trình đánh giá, nhóm đề xuất cho cô thứ tự đọc mã nguồn như sau:

1. Đọc **README.md** để nắm tổng quan dự án.
2. Tham khảo **Class Diagram/** để hiểu kiến trúc hướng đối tượng.
3. Kiểm tra **data_structures/** để đánh giá phần cài đặt cấu trúc dữ liệu và thuật toán.
4. Kiểm tra **controllers/** để theo dõi luồng xử lý nghiệp vụ.
5. Kiểm tra **models/** để đánh giá thiết kế hướng đối tượng.
6. Chạy **app.py** để trải nghiệm giao diện và các chức năng của hệ thống.
7. Chạy các file **benchmark** để đánh giá hiệu năng của chương trình trên các tập dữ liệu lớn.

Việc tổ chức dự án theo mô hình phân lớp giúp mã nguồn dễ theo dõi, thuận tiện cho việc kiểm thử, bảo trì và mở rộng trong tương lai.

