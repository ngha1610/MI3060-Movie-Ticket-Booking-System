from datetime import datetime, timedelta
import random
import string
from faker import Faker
from models.entities import UserData, MovieData, Room, Showtime, TicketData

def generate_mock_data():
    print("Đang khởi tạo dữ liệu, vui lòng đợi vài giây...")
    
    # 1. TẠO ROOMS (6 Phòng: 5 phòng thường, 1 Starium)
    rooms = []
    for i in range(1, 6):
        # Phòng thường: 10 hàng, 12 cột = 120 ghế
        rooms.append(Room(f"R0{i}", f"Cinema {i}", 10, 12))
    # Phòng Starium: 15 hàng, 20 cột = 300 ghế
    rooms.append(Room("R06", "Starium", 15, 20))
    
    # 2. TẠO MOVIES (10 Phim hot từ T12/2025 - T5/2026 lấy từ thực tế)
    # 2. TẠO MOVIES (60 Phim chiếu rạp tại Việt Nam - Trải dài 6 tháng)
    # Cấu trúc: (movie_id, title, genre, duration, is_hot)
    movies = []
    movies_info = [
        # --- THÁNG 1 (Giai đoạn Cuối năm / Lễ hội) ---
        ("M001", "Avatar: Fire and Ash", "Khoa học viễn tưởng / Hành động", 190, True),
        ("M002", "Lật Mặt 8: Vòng Xoáy", "Hành động / Tâm lý", 120, True),
        ("M003", "Kẻ Ăn Hồn 2", "Kinh dị / Cổ trang", 115, True),
        ("M004", "Sonic the Hedgehog 3", "Hoạt hình / Hài hước", 105, False),
        ("M005", "Chị Chị Em Em 3", "Tâm lý / Giật gân", 110, False),
        ("M006", "Kraven the Hunter", "Hành động / Siêu anh hùng", 125, False),
        ("M007", "Quỷ Cẩu 2", "Kinh dị / Tâm linh", 105, True),
        ("M008", "Mufasa: The Lion King", "Hoạt hình / Phiêu lưu", 118, True),
        ("M009", "Chuyến Tàu Tử Thần", "Kinh dị / Sinh tồn", 110, False),
        ("M010", "Cô Dâu Hào Môn 2", "Hài hước / Tâm lý", 115, False),

        # --- THÁNG 2 (Giai đoạn Tết Nguyên Đán / Valentine) ---
        ("M011", "Nhà Bà Nữ 2: Kế Nghiệp", "Gia đình / Hài hước", 125, True),
        ("M012", "Cua Lại Vợ Bầu 2", "Tình cảm / Hài hước", 115, True),
        ("M013", "Captain America: Brave New World", "Hành động / Siêu anh hùng", 135, True),
        ("M014", "Nụ Hôn Âm Phủ", "Kinh dị / Tình cảm", 100, False),
        ("M015", "Tấm Cám: Chuyện Chưa Kể 2", "Cổ trang / Thần thoại", 120, False),
        ("M016", "Mai: Ngoại Truyện", "Tâm lý / Tình cảm", 130, True),
        ("M017", "Paddington in Peru", "Gia đình / Hài hước", 105, False),
        ("M018", "The Conjuring: Last Rites", "Kinh dị / Siêu nhiên", 118, True),
        ("M019", "Trạng Tí 2", "Hoạt hình / Cuộc phiêu lưu", 100, False),
        ("M020", "Lỡ Hẹn Với Ngày Xanh", "Tình cảm / Lãng mạn", 110, False),

        # --- THÁNG 3 (Giai đoạn Sau Tết / Bom tấn đầu năm) ---
        ("M021", "Quật Mộ Trùng Ma 2 (Exhuma 2)", "Kinh dị / Bí ẩn", 135, True),
        ("M022", "Mickey 17", "Khoa học viễn tưởng / Tâm lý", 130, True),
        ("M023", "Ma Da: Hồi Sinh", "Kinh dị / Văn hóa", 110, True),
        ("M024", "Thám Tử Lừng Danh Conan: Movie 28", "Hoạt hình / Trinh thám", 110, True),
        ("M025", "Đất Rừng Phương Nam: Khởi Nghĩa", "Lịch sử / Tâm lý", 135, True),
        ("M026", "Án Mạng Trên Sông Hương", "Trinh thám / Giật gân", 115, False),
        ("M027", "The Batman Part II", "Hành động / Tội phạm", 160, True),
        ("M028", "Kính Vạn Hoa: Bản Điện Ảnh", "Gia đình / Phiêu lưu", 110, True),
        ("M029", "Rừng Thế Mạng 2", "Sinh tồn / Giật gân", 100, False),
        ("M030", "Snow White", "Nhạc kịch / Thần thoại", 120, False),

        # --- THÁNG 4 (Giai đoạn Mùa phim Hè sớm) ---
        ("M031", "Fast X: Part 2", "Hành động / Đua xe", 145, True),
        ("M032", "Thanh Gươm Diệt Quỷ: Pháo Đài Vô Cực", "Hoạt hình / Hành động", 120, True),
        ("M033", "Vây Hãm: Trừng Phạt", "Hành động / Tội phạm", 110, True),
        ("M034", "Cám: Ký Ức Đẫm Máu", "Kinh dị / Tâm lý", 115, True),
        ("M035", "Five Nights at Freddy's 2", "Kinh dị / Giật gân", 110, True),
        ("M036", "Hồn Papa Da Con Gái 2", "Hài hước / Gia đình", 105, False),
        ("M037", "The Super Mario Bros. Movie 2", "Hoạt hình / Trẻ em", 100, True),
        ("M038", "Bạch Xuyên: Ám Ảnh", "Tâm lý / Kinh dị", 110, False),
        ("M039", "Mật Vụ Bí Ẩn", "Hành động / Điệp viên", 130, False),
        ("M040", "Minecraft: The Movie", "Phiêu lưu / Hài hước", 105, True),

        # --- THÁNG 5 (Giai đoạn Hè bùng nổ) ---
        ("M041", "Spider-Man: Beyond the Spider-Verse", "Hoạt hình / Siêu anh hùng", 140, True),
        ("M042", "Đồ Đáng Yêu: Phương Anh", "Hành động / Võ thuật", 125, True),
        ("M043", "Doraemon: Nobita và Thế Giới Ngầm", "Hoạt hình / Phiêu lưu", 105, True),
        ("M044", "Tiệc Trăng Máu 2", "Tâm lý / Hài đen", 110, True),
        ("M045", "Scream 7", "Kinh dị / Giật gân", 115, False),
        ("M046", "Superman: Legacy", "Hành động / Siêu anh hùng", 145, True),
        ("M047", "Đảo Độc Đắc 2", "Kinh dị / Sinh tồn", 100, False),
        ("M048", "Kẻ Kiến Tạo 2 (The Creator 2)", "Khoa học viễn tưởng", 135, False),
        ("M049", "Bố Già: Ngoại Truyện", "Gia đình / Tâm lý", 125, True),
        ("M050", "Dune: Messiah", "Khoa học viễn tưởng / Phiêu lưu", 165, True),

        # --- THÁNG 6 (Bom tấn Mùa Hè) ---
        ("M051", "Toy Story 5", "Hoạt hình / Gia đình", 100, True),
        ("M052", "28 Years Later", "Kinh dị / Hậu tận thế", 115, False),
        ("M053", "Người Mắt Dõi Theo 2", "Kinh dị / Tâm linh", 100, False),
        ("M054", "Moana 2", "Hoạt hình / Nhạc kịch", 105, True),
        ("M055", "Chuyện Ma Gần Nhà 2", "Kinh dị / Văn hóa", 105, True),
        ("M056", "The Fantastic Four: First Steps", "Hành động / Siêu anh hùng", 135, True),
        ("M057", "Zootopia 2", "Hoạt hình / Hài hước", 105, True),
        ("M058", "Bông Đẹp Quá Kìa", "Giật gân / Sinh tồn", 105, False),
        ("M059", "Phương Anh Là Mặt Trời Nhỏ", "Tình cảm / Lãng mạn", 145, True),
        ("M060", "Pororo", "Khoa học viễn tưởng / Kinh dị", 120, False)
    ]
    
    
    for movie_id, title, genre, duration, is_hot in movies_info:

    # Giá mặc định
       base_price = 95000

    # Poster mặc định để trống
       poster_path = ""

    # Tạo object phim
       movie = MovieData(
           movie_id,
           title,
           genre,
           duration,
           f"Mô tả phim {title}",
           base_price,
           poster_path
       )

    # Film hot sẽ có doanh thu khởi tạo cao hơn
       if is_hot:
           movie.add_revenue(base_price * 563)

       movies.append(movie)
    # 3. TẠO SHOWTIMES (Trong 6 tháng qua)
    showtimes = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    time_slots = ["09:00", "12:00", "15:00", "18:00", "21:00", "00:00"]
    
    st_counter = 1
    for day_offset in range(180):
        current_date = start_date + timedelta(days=day_offset)
        
        for room in rooms:
            # Chọn ngẫu nhiên 3-5 suất chiếu mỗi ngày cho 1 phòng
            slots_today = random.sample(time_slots, k=random.randint(5, 6))
            for slot in slots_today:
                # Phim hot có tỷ lệ được chọn cao gấp 5 lần
                weights = [3 if is_hot else 1 for _, _, _, _, is_hot in movies_info]
                selected_movie = random.choices(movies, weights=weights, k=1)[0]
                
                st_id = f"ST{st_counter:09d}"
                st_time_str = f"{current_date.strftime('%Y-%m-%d')} {slot}"
                
                showtimes.append(Showtime(
                    st_id, selected_movie.get_movie_id(), st_time_str,
                    room.get_room_id(), room.rows, room.cols
                ))
                st_counter += 1

    # 4. TẠO USERS (8000 Users)
    fake = Faker()

    users = []

# --- 1. SINH TÀI KHOẢN ADMIN (10 người từ ID 1 đến 10) ---
    for i in range(1, 11):
       u_id = f"A{i:09d}"  # Kết quả: U000000001 -> U000000010 (U + 9 chữ số)
    
    # Sinh username ngẫu nhiên chữ thường bằng faker, thêm tiền tố admin_ để bạn dễ test đăng nhập
       username = f"admin_{fake.user_name().lower()}" 
       password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
       users.append(UserData(username, password, "ADMIN", u_id))

# --- 2. SINH TÀI KHOẢN CUSTOMER (8000 người từ ID 11 đến 8010) ---
    for i in range(11, 8011):
       u_id = f"U{i:09d}"  # Kết quả tiếp tục tăng: U000000011 -> U000008010
    
    # Sinh username random bừa, viết thường toàn bộ bằng faker
       username = fake.user_name().lower() 
       password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
       users.append(UserData(username, password, "CUSTOMER", u_id))
        
    # 5. TẠO TICKETS & CẬP NHẬT DOANH THU, GHẾ NGỒI
    tickets = []
    ticket_counter = 1
    
    for user in users:
        # Logic phân bổ người xem:
        # 60% xem 1 lần | 30% xem 2-4 lần | 10% xem 5-8 lần (khách ruột)
        rand_val = random.random()
        if rand_val < 0.6:
            num_tickets = 1
        elif rand_val < 0.9:
            num_tickets = random.randint(2, 4)
        else:
            num_tickets = random.randint(5, 8)
            
        for _ in range(num_tickets):
            st = random.choice(showtimes)
            room = next(r for r in rooms if r.get_room_id() == st.get_room_id())
            movie = next(m for m in movies if m.get_movie_id() == st.get_movie_id())
            
            # Tính giá vé theo ngày và phòng
            st_date = datetime.strptime(st.get_start_time(), '%Y-%m-%d %H:%M')
            is_weekend = st_date.weekday() >= 4 # Thứ 6 (4), T7 (5), CN (6)
            
            if room.room_name == "Starium":
                price = 140000
            else:
                price = 130500 if is_weekend else 95000
                
            # Tìm 1 ghế trống
            matrix = st.get_seat_matrix()
            empty_seats = []
            for r in range(matrix.get_rows()):
                for c in range(matrix.get_cols()):
                    if matrix.check_status(r, c) == SeatStatus.EMPTY:
                        empty_seats.append((r, c))
                        
            if empty_seats:
                # Đặt ghế
                r, c = random.choice(empty_seats)
                matrix.book_seat(r, c)
                seat_id = matrix.generate_seat_id(r, c)
                
                t_id = f"T{ticket_counter:09d}"
                ticket = TicketData(t_id, user._user_id, movie.get_movie_id(), seat_id, "BOOKED", st.get_showtime_id(), room.get_room_id(), price)
                # Đặt booking time lùi về trước giờ chiếu 1 chút cho logic
                ticket.booking_time = st_date - timedelta(hours=random.randint(1, 48))
                
                tickets.append(ticket)
                ticket_counter += 1
                
                # Cập nhật doanh thu cho phim
                movie.add_revenue(price)

    print("\n========== KẾT QUẢ TẠO DỮ LIỆU ==========")
    print(f"Tổng số Users: {len(users):,}")
    print(f"Tổng số Phim: {len(movies)}")
    print(f"Tổng số Phòng chiếu: {len(rooms)}")
    print(f"Tổng số Suất chiếu (6 tháng): {len(showtimes):,}")
    print(f"Tổng số Vé đã bán: {len(tickets):,}")
    
    # In thử top doanh thu phim để kiểm chứng độ hợp lý
    print("\n--- Bảng Xếp Hạng Doanh Thu Phim (Test) ---")
    sorted_movies = sorted(movies, key=lambda m: m.get_revenue(), reverse=True)
    for i, m in enumerate(sorted_movies[:5]):
        print(f"{i+1}. {m._title} ({m._genre}) - {m.get_revenue():,} VND")

    return users, movies, rooms, showtimes, tickets

import csv

def export_to_csv_files(users, movies, rooms, showtimes, tickets):
    print("\nĐang tiến hành xuất dữ liệu ra các file CSV...")

    # 1. Xuất file users.csv
    with open('users.csv', mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Ghi header
        writer.writerow(['user_id', 'username', 'password', 'role'])
        # Ghi data
        for u in users:
            writer.writerow([u._user_id, u.get_username(), u._password, u._role])

    # 2. Xuất file movies.csv
    with open('movies.csv', mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'movie_id',
            'title',
            'genre',
            'duration',
            'description',
            'base_price',
            'poster_path',
            'revenue'
       ])
        for m in movies:
            writer.writerow([m.get_movie_id(), m._title, m._genre, m.get_duration(), m._description, m.get_base_price(), m.get_poster_path(), m.get_revenue()])

    # 3. Xuất file rooms.csv
    with open('rooms.csv', mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['room_id', 'room_name', 'rows', 'cols', 'capacity'])
        for r in rooms:
            writer.writerow([r.get_room_id(), r.room_name, r.rows, r.cols, r.get_capacity()])

    # 4. Xuất file showtimes.csv
    with open('showtimes.csv', mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['showtime_id', 'movie_id', 'start_time', 'room_id'])
        for st in showtimes:
            writer.writerow([st.get_showtime_id(), st.get_movie_id(), st.get_start_time(), st.get_room_id()])

    # 5. Xuất file tickets.csv
    with open('tickets.csv', mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ticket_id', 'user_id', 'movie_id', 'seat_id', 'status', 'showtime_id', 'room_id', 'price', 'booking_time'])
        for t in tickets:
            writer.writerow([
                t.get_ticket_id(), t._user_id, t._movie_id, t._seat_id, 
                t._status, t._showtime_id, t._room_id, t._price, 
                t._booking_time.strftime('%Y-%m-%d %H:%M:%S')
            ])

    print("=========================================================")
    print("[THÀNH CÔNG] Đã sinh ra 5 file CSV trong thư mục dự án:")
    print(" 1. users.csv     (8,000 dòng)")
    print(" 2. movies.csv    (60 dòng)")
    print(" 3. rooms.csv     (6 dòng)")
    print(" 4. showtimes.csv (Hàng ngàn suất chiếu)")
    print(" 5. tickets.csv   (Hàng vạn vé đã bán)")
    print("=========================================================")

# =========================================================
# LỆNH CHẠY: Gọi hàm sinh dữ liệu cũ -> Rồi truyền vào hàm xuất CSV
# =========================================================
if __name__ == "__main__":
    # Lệnh này chỉ chạy khi bạn bấm RUN trực tiếp file này
    users_db, movies_db, rooms_db, showtimes_db, tickets_db = generate_mock_data()
    export_to_csv_files(users_db, movies_db, rooms_db, showtimes_db, tickets_db)