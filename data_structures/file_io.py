import csv
import json

from models.entities import (
    UserData,
    MovieData,
    TicketData,
    Showtime,
    Room
)


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
            pass

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
            pass

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
            pass

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

        try:
            with open(
                self.showtimes_file,
                mode="r",
                encoding="utf-8"
            ) as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # 1. Xác định kích thước ghế theo ID phòng chiếu
                    room_id = row["room_id"].strip()
                    if room_id == "R06":
                        rows, cols = 15, 20
                    else:
                        rows, cols = 10, 12

                    # 2. Khởi tạo suất chiếu với cấu hình rạp tương ứng
                    showtime = Showtime(
                        showtime_id=row["showtime_id"],
                        movie_id=row["movie_id"],
                        start_time=row["start_time"],
                        room_id=room_id,
                        room_rows=rows,
                        room_cols=cols
                    )

                    # 3. Đọc dữ liệu ghế đã đặt (nếu file CSV có lưu cột seats_matrix)
                    if "seats_matrix" in row and row["seats_matrix"]:
                        try:
                            seats_data = json.loads(row["seats_matrix"])
                            seat_matrix = showtime.get_seat_matrix()
                            
                            # Cập nhật lại các ghế đã có người đặt
                            for r in range(min(rows, len(seats_data))):
                                for c in range(min(cols, len(seats_data[0]))):
                                    seat_matrix._seats[r][c] = seats_data[r][c]
                        except Exception:
                            # Bỏ qua nếu dữ liệu lỗi, dùng lại ma trận ghế trống mặc định
                            pass

                    showtime_list.add_showtime(showtime)

        except FileNotFoundError:
            pass

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
                "room_id",
                "seats_matrix"
            ]

            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames
            )

            writer.writeheader()

            current = showtime_list.get_head()
            while current is not None:
                st = current.get_data()
                seat_matrix = st.get_seat_matrix()
                
                # Mã hóa ma trận ghế sang dạng chuỗi JSON để lưu trữ
                seats_string = json.dumps(seat_matrix._seats)

                writer.writerow({
                    "showtime_id": st.get_showtime_id(),
                    "movie_id": st.get_movie_id(),
                    "start_time": st.get_start_time(),
                    "room_id": st.get_room_id(),
                    "seats_matrix": seats_string
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
                        price=float(row["price"])
                    )
                    ticket_list.add_ticket(ticket)

        except FileNotFoundError:
            pass

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
                "price"
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
                    "price": ticket.get_price()
                })
                current = current.get_next()

    # =====================================================
    # SAVE ALL
    # =====================================================

    def save_all(
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

    def load_all(
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
