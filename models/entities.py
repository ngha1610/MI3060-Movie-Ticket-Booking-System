from datetime import datetime

# =========================================================
# ENUM TRẠNG THÁI GHẾ
# =========================================================

class SeatStatus:
    EMPTY = 0
    RESERVED = 1
    BOOKED = 2
    BLOCKED = -1   # Ghế không tồn tại / bị khóa


# =========================================================
# USER DATA
# =========================================================

class UserData:
    def __init__(self, username, password, role, user_id):

        if not username.strip():
            raise ValueError("Username không hợp lệ")

        if not password.strip():
            raise ValueError("Password không hợp lệ")

        self._username = username
        self._password = password

        self._role = role
        self._user_id = user_id

    def get_username(self):
        return self._username

    def check_password(self, password):
        return self._password == password
    
    def get_password(self):
        return self._password

    def get_role(self):
        return self._role

    def get_user_id(self):
        return self._user_id


# =========================================================
# TICKET DATA
# =========================================================

class TicketData:
    def __init__(self, ticket_id, user_id, movie_id, seat_id, status, showtime_id,room_id, price):

        if price < 0:
            raise ValueError("Giá vé không hợp lệ")

        self._ticket_id = ticket_id

        self._user_id = user_id
        self._movie_id = movie_id
        self._seat_id = seat_id

        self._status = status

        self._showtime_id = showtime_id
        self._room_id = room_id

        self._price = price

        # thời gian đặt vé
        self._booking_time = datetime.now()

    def get_ticket_id(self):
        return self._ticket_id
    def get_user_id(self):
        return self._user_id

    def get_movie_id(self):
        return self._movie_id

    def get_seat_id(self):
        return self._seat_id

    def get_status(self):
        return self._status

    def get_showtime_id(self):
        return self._showtime_id

    def get_room_id(self):
        return self._room_id

    def get_price(self):
        return self._price


# =========================================================
# MOVIE DATA
# =========================================================

class MovieData:

    def __init__(
        self,
        movie_id,
        title,
        genre,
        duration,
        description,
        base_price,
        poster_path=""
    ):

        if not title.strip():
            raise ValueError("Tên phim không hợp lệ")

        if duration <= 0:
            raise ValueError("Thời lượng phim không hợp lệ")

        if base_price < 0:
            raise ValueError("Giá vé không hợp lệ")

        self._movie_id = movie_id

        self._title = title
        self._genre = genre

        self._duration = duration

        self._description = description

        self._base_price = base_price

        self._poster_path = poster_path

        # doanh thu phát sinh khi bán vé
        self._revenue = 0

    # =====================================================
    # GETTER
    # =====================================================

    def get_movie_id(self):
        return self._movie_id

    def get_title(self):
        return self._title

    def get_genre(self):
        return self._genre

    def get_duration(self):
        return self._duration

    def get_description(self):
        return self._description

    def get_base_price(self):
        return self._base_price

    def get_poster_path(self):
        return self._poster_path

    def get_revenue(self):
        return self._revenue

    # =====================================================
    # SETTER
    # =====================================================

    def set_title(self, title):

        if title.strip():
            self._title = title

    def set_genre(self, genre):
        self._genre = genre

    def set_duration(self, duration):

        if duration > 0:
            self._duration = duration

    def set_description(self, description):
        self._description = description

    def set_base_price(self, base_price):

        if base_price >= 0:
            self._base_price = base_price

    def set_poster_path(self, poster_path):
        self._poster_path = poster_path

    # =====================================================
    # NGHIỆP VỤ
    # =====================================================

    def add_revenue(self, amount):

        if amount > 0:
            self._revenue += amount

class SeatMatrix:

    def __init__(self, rows: int, cols: int):

        if rows <= 0 or cols <= 0:
            raise ValueError("Kích thước phòng không hợp lệ")

        self._rows = rows
        self._cols = cols

        self._seats = [
            [SeatStatus.EMPTY for _ in range(cols)]
            for _ in range(rows)
        ]

    def get_rows(self):
        return self._rows

    def get_cols(self):
        return self._cols

    def generate_seat_id(self, r, c):

        return f"{chr(65 + r)}{c + 1}"

    def check_status(self, r: int, c: int) -> int:

        if 0 <= r < self._rows and 0 <= c < self._cols:
            return self._seats[r][c]

        return SeatStatus.BLOCKED

    def reserve_seat(self, r: int, c: int) -> bool:

        if (
            0 <= r < self._rows
            and 0 <= c < self._cols
            and self._seats[r][c] == SeatStatus.EMPTY
        ):

            self._seats[r][c] = SeatStatus.RESERVED
            return True

        return False


    def book_seat(self, r: int, c: int) -> bool:

        if (
            0 <= r < self._rows
            and 0 <= c < self._cols
            and (
                self._seats[r][c] == SeatStatus.EMPTY
                or self._seats[r][c] == SeatStatus.RESERVED
            )
        ):

            self._seats[r][c] = SeatStatus.BOOKED
            return True

        return False

    def release_seat(self, r, c):

        if (
            0 <= r < self._rows
            and
            0 <= c < self._cols
        ):

            self._seats[r][c] = SeatStatus.EMPTY

    def get_seats(self):
        return self._seats

    def load_matrix(self, seats):

        self._seats = seats

        self._rows = len(seats)

        self._cols = (
           len(seats[0])
           if seats else 0
        )
        
    # Cần truyền tọa độ r, c để set đúng ghế đó
    def set_seat_status(self, r: int, c: int, status: int):
        if 0 <= r < self._rows and 0 <= c < self._cols:
           self._seats[r][c] = status
           return True
        return False


class Room:

    def __init__(self, room_id, room_name, rows, cols):

        if rows <= 0 or cols <= 0:
            raise ValueError("Kích thước phòng không hợp lệ")

        self._room_id = room_id

        self.room_name = room_name

        self.rows = rows
        self.cols = cols

        self._capacity = rows * cols

    def get_room_id(self):
        return self._room_id

    def get_capacity(self):
        return self._capacity
    
    def get_room_name(self):
        return self.room_name

    def get_rows(self):
        return self.rows

    def get_cols(self):
        return self.cols

class Showtime:

    def __init__(self, showtime_id: str, movie_id: str, start_time: str, room_id: str, room_rows: int, room_cols: int):

        self._showtime_id = showtime_id

        self._movie_id = movie_id

        self._start_time = start_time

        self._room_id = room_id

        self._seat_matrix = SeatMatrix(
            room_rows,
            room_cols
        )
    
    def get_showtime_id(self):
        return self._showtime_id

    def get_movie_id(self):
        return self._movie_id

    def get_room_id(self):
        return self._room_id

    def get_start_time(self):
        return self._start_time

    def get_seat_matrix(self):
        return self._seat_matrix

    def get_available_seats(self) -> int:

        count = 0

        rows = self._seat_matrix.get_rows()
        cols = self._seat_matrix.get_cols()

        for r in range(rows):

            for c in range(cols):

                if (
                    self._seat_matrix.check_status(r, c)
                    == SeatStatus.EMPTY
                ):
                    count += 1

        return count
