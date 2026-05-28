from models.entities import (
    Showtime,
    TicketData,
    UserData,
    MovieData
)

from data_structures.linked_lists import (
    TicketLinkedList
)

from data_structures.file_io import (
    FileIOHandler
)

from controllers.showtime_controller import (
    ShowtimeController
)
from controllers.movie_controller import MovieController

# =====================================================
# BOOKING CONTROLLER
# =====================================================

class BookingController:

    def __init__(
        self,
        io_handler: FileIOHandler,
        showtime_controller: ShowtimeController,
        movie_controller: MovieController
    ):

        self._io_handler = io_handler

        self._showtime_controller = (
            showtime_controller
        )

        self._movie_controller = (
            movie_controller
        )

        self._ticket_list = (
            TicketLinkedList()
        )

        self._io_handler.load_tickets(
            self._ticket_list
        )

    # =================================================
    # TẠO MÃ VÉ (ĐÃ SỬA: DUYỆT LINKED LIST TÌM MAX ID CHỐNG TRÙNG)
    # =================================================

    def _generate_ticket_id(self):

        current = self._ticket_list.get_head()
        
        # Nếu chưa có vé nào được đặt
        if current is None:
            return "T000000001"

        max_id_num = 0

        # Duyệt dọc theo danh sách liên kết đơn để tìm mã lớn nhất
        while current is not None:
            ticket = current.get_data()
            ticket_id_str = ticket.get_ticket_id()  # Định dạng dạng "T000000042"
            
            try:
                # Cắt bỏ chữ 'T' ở đầu và ép kiểu sang số int để so sánh
                id_num = int(ticket_id_str[1:])
                if id_num > max_id_num:
                    max_id_num = id_num
            except ValueError:
                pass
                
            current = current.get_next()

        return f"T{max_id_num + 1:09d}"

    # =================================================
    # ĐẶT VÉ
    # =================================================

    def process_booking(self, user: UserData, movie: MovieData, showtime: Showtime, row: int, col: int, movie_controller) -> bool:

        # kiểm tra ghế còn trống không
        available = (
            self._showtime_controller
            .check_seat_status(
                showtime.get_showtime_id(),
                row,
                col
            )
        )

        if not available:
            return False

        # book ghế trong seat matrix
        booked = (
            self._showtime_controller
            .book_seat(
                showtime.get_showtime_id(),
                row,
                col
            )
        )

        if not booked:
            return False

        # tạo seat id
        seat_id = (
            showtime
            .get_seat_matrix()
            .generate_seat_id(row, col)
        )

        # giá vé
        price = movie.get_base_price()

        # tạo ticket
        ticket = TicketData(

            ticket_id=
            self._generate_ticket_id(),

            user_id=
            user.get_user_id(),

            movie_id=
            movie.get_movie_id(),

            seat_id=
            seat_id,

            status=
            "BOOKED",

            showtime_id=
            showtime.get_showtime_id(),

            room_id=
            showtime.get_room_id(),

            price=
            price
        )

        # cộng doanh thu phim
        movie.add_revenue(price)

        # thêm ticket
        self._ticket_list.add_ticket(
            ticket
        )

        # lưu file
        self._io_handler.save_tickets(
            self._ticket_list
        )
        # Tăng doanh thu cho phim
        current_revenue = movie.get_revenue()
        movie.set_revenue(current_revenue + price)
        
        # Mượn movie_controller để lưu lại doanh thu
        self._io_handler.save_movies(self._movie_controller.get_movie_list())
        return True

   

    # =================================================
    # HỦY VÉ
    # =================================================

    def cancel_booking(
        self,
        user_id: str,
        ticket_id: str
    ) -> bool:

        node = (
            self._ticket_list
            .find_ticket(ticket_id)
        )

        if node is None:
            return False

        ticket = node.get_data()

        # chỉ chủ vé mới được hủy
        if (
            ticket.get_user_id()
            != user_id
        ):
            return False

        # vé đã hủy trước đó
        if (
            ticket.get_status()
            == "CANCELLED"
        ):
            return False

        # chuyển seat_id -> row col
        seat_id = (
            ticket.get_seat_id()
        )

        row = (
            ord(seat_id[0]) - 65
        )

        col = (
            int(seat_id[1:]) - 1
        )

        # trả ghế về EMPTY
        self._showtime_controller.release_seat(
            ticket.get_showtime_id(),
            row,
            col
        )

        # cập nhật trạng thái vé
        ticket.set_status(
            "CANCELLED"
        )

        # lưu file
        self._io_handler.save_tickets(
            self._ticket_list
        )

        return True

    # =================================================
    # LỊCH SỬ ĐẶT VÉ
    # =================================================

    def get_booking_history(
        self,
        user_id: str
    ):

        result = []

        current = (
            self._ticket_list.get_head()
        )

        while current is not None:

            ticket = (
                current.get_data()
            )

            if (
                ticket.get_user_id()
                == user_id
            ):

                result.append(ticket)

            current = (
                current.get_next()
            )

        return result

    # =================================================
    # TÌM VÉ
    # =================================================

    def find_ticket(
        self,
        ticket_id: str
    ):

        return (
            self._ticket_list
            .find_ticket(ticket_id)
        )

    # =================================================
    # IN THÔNG TIN VÉ
    # =================================================

    def generate_ticket_info(
        self,
        ticket_id: str
    ) -> str:

        node = (
            self._ticket_list
            .find_ticket(ticket_id)
        )

        if node is None:

            return (
                "Không tìm thấy vé"
            )

        t = node.get_data()

        return (
            f"Mã vé: {t.get_ticket_id()} | "
            f"Ghế: {t.get_seat_id()} | "
            f"Phòng: {t.get_room_id()} | "
            f"Trạng thái: {t.get_status()} | "
            f"Giá: {t.get_price():,.0f} VNĐ"
        )

    # =================================================
    # LẤY DANH SÁCH VÉ
    # =================================================

    def get_ticket_list(self):

        return self._ticket_list

    # =================================================
    # LẤY DỮ LIỆU VÉ
    # =================================================

    def get_ticket_data(self):

        result = []

        current = (
            self._ticket_list.get_head()
        )

        while current is not None:

            result.append(
                current.get_data()
            )

            current = (
                current.get_next()
            )

        return result




