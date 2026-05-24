
import csv
import random
import string
from faker import Faker
from datetime import datetime, timedelta

fake = Faker('vi_VN')

def generate_complex_mock_data():
    print("Bắt đầu sinh dữ liệu siêu thực tế theo chuẩn CGV...")

    # ==========================================
    # 1. SINH DỮ LIỆU USERDATA (10 Admins + 8000 Users)
    # ==========================================
    users = []
    customer_ids = []
    
    # 10 Admins
    for i in range(1, 11):
        username = f"admin_{i:02d}"
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        users.append([username, password, "Admin"])
        
    # 8000 Customers - Sửa lỗi UniquenessException
    for i in range(8000):
        username = f"{fake.user_name()}_{i:04d}"
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        users.append([username, password, "Customer"])
        customer_ids.append(username)

    with open('users.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["username", "password", "role"])
        writer.writerows(users)
    print("Đã sinh xong 8.010 Users với mật khẩu ngẫu nhiên!")

    # ==========================================
    # 2. KHỞI TẠO DANH MỤC 60 PHIM (45 Việt - 15 Ngoại)
    # ==========================================
    # Trọng số suất chiếu: Blockbuster VN (10-12), Blockbuster Ngoại (7-9), Tiêu chuẩn (2-5)
    vietnamese_movies = [
        {"title": "Thỏ ơi!", "genre": "Tâm lý xã hội", "base_price": 110000, "weight": 12},
        {"title": "Nhà Ba Tôi Một Phòng", "genre": "Gia đình", "base_price": 80000, "weight": 4},
        {"title": "Báu vật trời cho", "genre": "Gia đình", "base_price": 90000, "weight": 5},
        {"title": "Mùi phở", "genre": "Gia đình", "base_price": 75000, "weight": 2},
        {"title": "Mai", "genre": "Tâm lý", "base_price": 100000, "weight": 11},
        {"title": "Lật Mặt 8", "genre": "Hành động", "base_price": 100000, "weight": 10},
        {"title": "Nhà Bà Nữ", "genre": "Gia đình", "base_price": 95000, "weight": 9},
        {"title": "Bố Già", "genre": "Gia đình", "base_price": 90000, "weight": 8},
        {"title": "Đất Rừng Phương Nam", "genre": "Gia đình", "base_price": 90000, "weight": 7},
        {"title": "Kẻ Ăn Hồn", "genre": "Kinh dị", "base_price": 90000, "weight": 6},
        {"title": "Quỷ Cẩu", "genre": "Kinh dị", "base_price": 85000, "weight": 5},
        {"title": "Người Vợ Cuối Cùng", "genre": "Tâm lý", "base_price": 95000, "weight": 6},
        {"title": "Chị Chị Em Em 2", "genre": "Tâm lý", "base_price": 85000, "weight": 4},
        {"title": "Siêu Lừa Gặp Siêu Lầy", "genre": "Hài hước", "base_price": 85000, "weight": 5},
        {"title": "Em Và Trịnh", "genre": "Tiểu sử", "base_price": 90000, "weight": 4},
        {"title": "Tiệc Trăng Máu", "genre": "Tâm lý", "base_price": 90000, "weight": 6},
        {"title": "Hai Phượng", "genre": "Hành động", "base_price": 95000, "weight": 7},
        {"title": "Cua Lại Vợ Bầu", "genre": "Hài hước", "base_price": 90000, "weight": 5},
        {"title": "Mắt Biếc", "genre": "Tình cảm", "base_price": 95000, "weight": 6},
        {"title": "Thiên Thần Hộ Mệnh", "genre": "Kinh dị", "base_price": 85000, "weight": 3}
    ]
    
    # Tự động sinh thêm cho đủ 45 phim Việt
    vn_genres = ["Tâm lý", "Hài hước", "Hành động", "Kinh dị", "Gia đình","Tình cảm","Tài liệu"]
    for i in range(25):
        vietnamese_movies.append({
            "title": f"{fake.catch_phrase()}", 
            "genre": random.choice(vn_genres), 
            "base_price": random.choice([75000, 80000, 85000]), 
            "weight": random.randint(2, 4)
        })

    foreign_movies = [
        {"title": "Avatar: Lửa và Tro Tàn", "genre": "Viễn tưởng", "base_price": 140000, "weight": 9},
        {"title": "Tee Yod: Quỷ Ăn Tạng 3", "genre": "Kinh dị", "base_price": 95000, "weight": 7},
        {"title": "Tiểu Yêu Quái Núi Lãng Lãng", "genre": "Hoạt hình", "base_price": 85000, "weight": 5},
        {"title": "Nụ Hôn Bạc Tỷ", "genre": "Tình cảm", "base_price": 90000, "weight": 4},
        {"title": "Yêu Nhầm Bạn Thân", "genre": "Hài hước", "base_price": 90000, "weight": 3},
        {"title": "Dune: Hành Tinh Cát - Phần 2", "genre": "Viễn tưởng", "base_price": 120000, "weight": 8},
        {"title": "Deadpool & Wolverine", "genre": "Hành động", "base_price": 110000, "weight": 9},
        {"title": "Inside Out 2", "genre": "Hoạt hình", "base_price": 95000, "weight": 8},
        {"title": "Godzilla x Kong: Đế Chế Mới", "genre": "Hành động", "base_price": 110000, "weight": 7},
        {"title": "Kung Fu Panda 4", "genre": "Hoạt hình", "base_price": 95000, "weight": 6},
        {"title": "Mickey 17", "genre": "Viễn tưởng", "base_price": 100000, "weight": 5},
        {"title": "Người Nhện: Đa Vũ Trụ", "genre": "Hành động", "base_price": 110000, "weight": 7},
        {"title": "Oppenheimer", "genre": "Tiểu sử", "base_price": 105000, "weight": 4},
        {"title": "Fast & Furious 11", "genre": "Hành động", "base_price": 110000, "weight": 8},
        {"title": "Mission: Impossible 8", "genre": "Hành động", "base_price": 110000, "weight": 6}
    ]

    all_templates = vietnamese_movies + foreign_movies
    movies = []
    movie_objs = {}
    
    for i, template in enumerate(all_templates, 1):
        movie_id = f"M{i:03d}"
        revenue = 0.0
        movies.append([movie_id, template["title"], template["genre"], revenue])
        movie_objs[movie_id] = template

    # ==========================================
    # 3. SINH DỮ LIỆU SHOWTIME (Giờ chiếu chia hết cho 5)
    # ==========================================
    showtimes = []
    showtime_counter = 1
    
    for movie in movies:
        m_id = movie[0]
        weight = movie_objs[m_id]["weight"]
        # Phim hot nhiều suất, phim ít hot ít suất
        num_showtimes = weight * random.randint(3, 6) 
        
        for _ in range(num_showtimes):
            showtime_id = f"ST{showtime_counter:04d}"
            
            # Lịch chiếu rải rác 6 tháng qua
            days_ago = random.randint(1, 180)
            random_time = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
            
            # Làm tròn số phút để chia hết cho 5 (vd: 10, 15, 20... 55)
            minute_rounded = (random.randint(0, 59) // 5) * 5
            random_time = random_time.replace(minute=minute_rounded, second=0, microsecond=0)
            time_str = random_time.strftime("%Y-%m-%d %H:%M")
            
            # Khởi tạo phòng chiếu 9 hàng (A-J), 9 cột (1-9)
            showtimes.append([showtime_id, time_str, m_id, 9, 9])
            showtime_counter += 1

    with open('showtimes.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["showtime_id", "time", "movie_id", "rows", "cols"])
        writer.writerows(showtimes)
    print(f"Đã sinh xong {len(showtimes)} Suất chiếu với giờ chiếu chia hết cho 5!")

    # ==========================================
    # 4. TẠO TẬP KHÁCH HÀNG & SINH VÉ (TICKET DATA)
    # ==========================================
    tickets = []
    booked_seats = {st[0]: set() for st in showtimes}
    
    # Phân bổ tần suất đặt vé cho 8000 users
    booking_tasks = []
    for idx, u_id in enumerate(customer_ids):
        if idx < 400: # VIP
            num_tickets = random.randint(10, 15)
        elif idx < 2400: # Thường xuyên
            num_tickets = random.randint(3, 5)
        else: # Vãng lai
            num_tickets = 1
        booking_tasks.extend([u_id] * num_tickets)
    
    random.shuffle(booking_tasks) 
    row_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J'] 
    
    for user_id in booking_tasks:
        ticket_id = str(random.randint(100000000, 999999999))
        
        st = random.choice(showtimes)
        showtime_id, movie_id = st[0], st[2]
        
        row_char = random.choice(row_letters)
        col_num = random.randint(1, 9)
        seat_id = f"{row_char}{col_num}"
        
        attempts = 0
        while seat_id in booked_seats[showtime_id] and attempts < 10:
            row_char = random.choice(row_letters)
            col_num = random.randint(1, 9)
            seat_id = f"{row_char}{col_num}"
            attempts += 1
            
        if seat_id not in booked_seats[showtime_id]:
            booked_seats[showtime_id].add(seat_id)
            status = random.choices(["Active", "Cancelled"], weights=[0.95, 0.05])[0]
            
            tickets.append([ticket_id, user_id, movie_id, seat_id, status, showtime_id])
            
            # Tính tiền vé và cộng dồn doanh thu
            if status == "Active":
                base_price = movie_objs[movie_id]["base_price"]
                if row_char in ['A', 'B', 'C']:
                    final_price = base_price - 10000
                elif row_char == 'J':
                    final_price = base_price + 20000
                else:
                    final_price = base_price
                    
                for m in movies:
                    if m[0] == movie_id:
                        m[3] += final_price
                        break

    with open('tickets.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["ticket_id", "user_id", "movie_id", "seat_id", "status", "showtime_id"])
        writer.writerows(tickets)

    with open('movies.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["movie_id", "title", "genre", "revenue"])
        writer.writerows(movies)
        
    print(f"Hoàn tất! Đã sinh {len(tickets)} giao dịch vé chuẩn xác.")

if __name__ == "__main__":
    generate_complex_mock_data()

