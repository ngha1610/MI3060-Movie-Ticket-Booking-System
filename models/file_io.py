import csv
import json
import sys
import ast

csv.field_size_limit(2147483647)

from models.entities import UserData, MovieData, TicketData, Showtime, Room

class FileIOHandler:

    def __init__(self, base_path="data/"):

        self.base_path = base_path

        self.users_file = f"{base_path}users.csv"
        self.movies_file = f"{base_path}movies.csv"
        self.rooms_file = f"{base_path}rooms.csv"
        self.showtimes_file = f"{base_path}showtimes.csv"
        self.tickets_file = f"{base_path}tickets.csv"

    # =====================================================
    # USER
    # =====================================================

    def load_users(self, table):

        try:
            with open(
                self.users_file,
                mode="r",
                encoding="utf-8"
            ) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    user = UserData(
                        username=row["username"],
                        password=row["password"],
                        role=row["role"],
                        user_id=row["user_id"]
                    )
                    table.insert(
                        user.get_username(),
                        user
                    )
        except FileNotFoundError:
            print(
                f"[WARNING] "
                f"{self.users_file} chưa tồn tại"
            )

    def save_users(self, table):

        with open(
            self.users_file,
            mode="w",
            newline="",
            encoding="utf-8"
        ) as f:

            fieldnames = [
                "user_id",
                "username",
                "password",
                "role"
            ]

            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames
            )

            writer.writeheader()

            for bucket in table.get_table():
                if bucket is None:
                    continue

                current = bucket
                visited = False

                while True:
                    if current == bucket and visited:
                        break

                    visited = True
                    user = current.get_data()

                    writer.writerow({
                        "user_id": user.get_user_id(),
                        "username": user.get_username(),
                        "password": user.get_password(),
                        "role": user.get_role()
                    })

                    current = current.get_next()

    # =====================================================
    # UI CONFIG
    # =====================================================

    def load_ui_config(self):
        config = {"SLIDER": [], "LIST": []}
        try:
            with open(f"{self.base_path}ui_config.csv", mode="r", encoding="utf-8") as f:
                for line in f:
                    clean_line = line.strip()
                    
                    parts = []
                    temp_str = ""
                    for char in clean_line:
                        if char == "|":
                            parts += [temp_str]
                            temp_str = ""
                        else:
                            temp_str += char
                    parts += [temp_str]
                    
                    count_parts = 0
                    for _ in parts: count_parts += 1

                    if count_parts > 0:
                        key = parts[0]
                        if key == "SLIDER" or key == "LIST":
                            idx = 1
                            while idx < count_parts:
                                if parts[idx] != "":
                                    config[key] += [parts[idx]]
                                idx += 1
        except FileNotFoundError:
            print(f"[WARNING] ui_config.csv chưa tồn tại")
        return config

    def save_ui_config(self, slider_titles, list_titles):
        with open(f"{self.base_path}ui_config.csv", mode="w", encoding="utf-8") as f:
            # Ghi dòng SLIDER
            f.write("SLIDER")
            for title in slider_titles:
                f.write(f"|{title}")
            f.write("\n")
            
            # Ghi dòng LIST
            f.write("LIST")
            for title in list_titles:
                f.write(f"|{title}")
            f.write("\n")

    # =====================================================
    # MOVIES
    # =====================================================

    def load_movies(self, movie_list):

        try:
            with open(
                self.movies_file,
                mode="r",
                encoding="utf-8"
            ) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    movie = MovieData(
                        movie_id=row["movie_id"],
                        title=row["title"],
                        genre=row["genre"],
                        duration=int(row["duration"]),
                        description=row["description"],
                        base_price=float(row["base_price"]),
                        poster_path=row["poster_path"]
                    )
                    movie_list.add_movie(movie)

        except FileNotFoundError:
            print(
                f"[WARNING] "
                f"{self.movies_file} chưa tồn tại"
            )

    def save_movies(self, movie_list):

        with open(
            self.movies_file,
            mode="w",
            newline="",
            encoding="utf-8"
        ) as f:

            fieldnames = [
                "movie_id",
                "title",
                "genre",
                "duration",
                "description",
                "base_price",
                "poster_path"
            ]

            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames
            )

            writer.writeheader()

            current = movie_list.get_head()
            while current is not None:
                movie = current.get_data()
                writer.writerow({
                    "movie_id": movie.get_movie_id(),
                    "title": movie.get_title(),
                    "genre": movie.get_genre(),
                    "duration": movie.get_duration(),
                    "description": movie.get_description(),
                    "base_price": movie.get_base_price(),
                    "poster_path": movie.get_poster_path()
                })
                current = current.get_next()

    # =====================================================
    # ROOMS
    # =====================================================

    def load_rooms(self, room_list):

        try:
            with open(
                self.rooms_file,
                mode="r",
                encoding="utf-8"
            ) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    room = Room(
                        room_id=row["room_id"],
                        room_name=row["room_name"],
                        rows=int(row["rows"]),
                        cols=int(row["cols"])
                    )
                    room_list.add_room(room)

        except FileNotFoundError:
            print(
                f"[WARNING] "
                f"{self.rooms_file} chưa tồn tại"
            )

    def save_rooms(self, room_list):

        with open(
            self.rooms_file,
            mode="w",
            newline="",
            encoding="utf-8"
        ) as f:

            fieldnames = [
                "room_id",
                "room_name",
                "rows",
                "cols"
            ]

            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames
            )

            writer.writeheader()

            current = room_list.get_head()
            while current is not None:
                room = current.get_data()
                writer.writerow({
                    "room_id": room.get_room_id(),
                    "room_name": room.get_room_name(),
                    "rows": room.get_rows(),
                    "cols": room.get_cols()
                })
                current = current.get_next()

    # =====================================================
    # SHOWTIMES
    # =====================================================

    def load_showtimes(self, showtime_list):
        
        # 1. ĐỌC DỮ LIỆU PHÒNG TRƯỚC (Lấy số Hàng và Cột)
        room_list_data = [] 
        try:
            with open(self.rooms_file, mode="r", encoding="utf-8") as rf:
                r_reader = csv.DictReader(rf)
                for r_row in r_reader:
                    room_list_data += [[r_row["room_id"], int(r_row["rows"]), int(r_row["cols"])]]
        except FileNotFoundError:
            pass
            
        # 2. SAU ĐÓ MỚI MỞ FILE SUẤT CHIẾU RA ĐỌC
        try:
            with open(
                self.showtimes_file,
                mode="r",
                encoding="utf-8"
            ) as f:
                reader = csv.DictReader(f)
            
                for row in reader:
                    # Xác định kích thước ghế theo ID phòng chiếu
                    room_id_raw = row.get("room_id", "")
                    room_id = str(room_id_raw).strip() if room_id_raw else "R01" 
                    
                    # Đặt giá trị mặc định trước 
                    rows, cols = 10, 12

                    # Tìm kiếm tuần tự trong mảng 2 chiều
                    for r_data in room_list_data:
                        if r_data[0] == room_id:
                            rows = r_data[1]
                            cols = r_data[2]
                            break

                    # Khởi tạo suất chiếu với cấu hình rạp tương ứng
                    showtime = Showtime(
                        showtime_id=row["showtime_id"],
                        movie_id=row["movie_id"],
                        start_time=row["start_time"],
                        room_id=room_id,
                        room_rows=rows,
                        room_cols=cols
                    )

                    # Đọc dữ liệu ghế đã đặt (nếu file CSV có lưu cột seats_matrix)
                    if "seats_matrix" in row and row["seats_matrix"]:
                        try:
                            raw_data = row["seats_matrix"]

                            seats_data = ast.literal_eval(raw_data)

                            while isinstance(seats_data, str):
                                seats_data = ast.literal_eval(seats_data)

                            if isinstance(seats_data, list):
                                seat_matrix = showtime.get_seat_matrix()
                                seat_matrix.load_matrix(seats_data)

                        except Exception as e:
                            pass

                    showtime_list.add_showtime(showtime)

        except FileNotFoundError:
            print(
                f"[WARNING] "
                f"{self.showtimes_file} chưa tồn tại"
            )

    def save_showtimes(self, showtime_list):

        with open(
            self.showtimes_file,
            mode="w",
            newline="",
            encoding="utf-8"
        ) as f:

            fieldnames = [
                "showtime_id",
                "movie_id",
                "start_time",
                "room_id"
            ]

            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames
            )

            writer.writeheader()

            current = showtime_list.get_head()
            while current is not None:
                st = current.get_data()
                
                writer.writerow({
                    "showtime_id": st.get_showtime_id(),
                    "movie_id": st.get_movie_id(),
                    "start_time": st.get_start_time(),
                    "room_id": st.get_room_id()
                })

                current = current.get_next()

    # =====================================================
    # TICKETS
    # =====================================================

    def load_tickets(self, ticket_list):

        try:
            with open(
                self.tickets_file,
                mode="r",
                encoding="utf-8"
            ) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ticket = TicketData(
                        ticket_id=row["ticket_id"],
                        user_id=row["user_id"],
                        movie_id=row["movie_id"],
                        seat_id=row["seat_id"],
                        status=row["status"],
                        showtime_id=row["showtime_id"],
                        room_id=row["room_id"],
                        price=float(row["price"]),
                        booking_time=row.get("booking_time") or None
                    )
                    ticket_list.add_ticket(ticket)

        except FileNotFoundError:
            print(
                f"[WARNING] "
                f"{self.tickets_file} chưa tồn tại"
            )

    def save_tickets(self, ticket_list):

        with open(
            self.tickets_file,
            mode="w",
            newline="",
            encoding="utf-8"
        ) as f:

            fieldnames = [
                "ticket_id",
                "user_id",
                "movie_id",
                "seat_id",
                "status",
                "showtime_id",
                "room_id",
                "price",
                "booking_time"
            ]

            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames
            )

            writer.writeheader()

            current = ticket_list.get_head()
            while current is not None:
                ticket = current.get_data()
                writer.writerow({
                    "ticket_id": ticket.get_ticket_id(),
                    "user_id": ticket.get_user_id(),
                    "movie_id": ticket.get_movie_id(),
                    "seat_id": ticket.get_seat_id(),
                    "status": ticket.get_status(),
                    "showtime_id": ticket.get_showtime_id(),
                    "room_id": ticket.get_room_id(),
                    "price": ticket.get_price(),
                    "booking_time": ticket.get_booking_time() or ""
                })
                current = current.get_next()

    # =====================================================
    # SAVE ALL
    # =====================================================

    def saveData(
        self,
        users,
        movies,
        rooms,
        showtimes,
        tickets
    ):
        self.save_users(users)
        self.save_movies(movies)
        self.save_rooms(rooms)
        self.save_showtimes(showtimes)
        self.save_tickets(tickets)

    # =====================================================
    # LOAD ALL
    # =====================================================

    def loadData(
        self,
        users,
        movies,
        rooms,
        showtimes,
        tickets
    ):
        self.load_users(users)
        self.load_movies(movies)
        self.load_rooms(rooms)
        self.load_showtimes(showtimes)
        self.load_tickets(tickets)