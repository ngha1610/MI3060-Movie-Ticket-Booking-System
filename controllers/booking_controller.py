from models.entities import (
    Showtime,
    TicketData,
    UserData,
    MovieData
)
from data_structures.linked_lists import TicketLinkedList
from data_structures.file_io import FileIOHandler
from controllers.showtime_controller import ShowtimeController
from controllers.movie_controller import MovieController
from datetime import datetime
import threading

# =====================================================
# BOOKING CONTROLLER
# =====================================================
_booking_lock = threading.Lock()
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
        
        self._sync_matrix_from_tickets()

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
  
    def process_booking(self, user: UserData, movie: MovieData, showtime: Showtime, row: int, col: int) -> bool:
        with _booking_lock:
        # 1. Kiểm tra ghế còn trống không (chỉ chấp nhận trạng thái EMPTY)
            self._io_handler.load_showtimes(
                self._showtime_controller.get_showtime_list(),
                self._movie_controller.get_room_list() 
            )

            # Kiểm tra ghế còn trống không
            available = self._showtime_controller.check_seat_status(showtime.get_showtime_id(), row, col)
            
            # Không print gì ở đây cả, chỉ return False
            if not available:
                return False

            # 2. KHÓA GHẾ (Chuyển trạng thái sang RESERVED thay vì BOOKED)
            matrix = showtime.get_seat_matrix()
            reserved = matrix.reserve_seat(row, col)

            if not reserved:
                return False

            # Cập nhật thay đổi ma trận ghế xuống file
            self._io_handler.save_showtimes(
                self._showtime_controller.get_showtime_list()
            )

            # 3. Tạo seat id
            seat_id = matrix.generate_seat_id(row, col)

            # 4. Lấy giá vé
            price = movie.get_base_price()

            # 5. Tạo ticket với trạng thái khóa (RESERVED)
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
                "RESERVED",  # <-- Đổi từ BOOKED thành RESERVED

                showtime_id=
                showtime.get_showtime_id(),

                room_id=
                showtime.get_room_id(),

                price=
                price,
                booking_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            # 6. Thêm ticket và lưu file
            self._ticket_list.add_ticket(
                ticket
            )

            self._io_handler.save_tickets(
                self._ticket_list
            )

            return True
    
    # =================================================
    # XÁC NHẬN THANH TOÁN & HOÀN TẤT ĐẶT VÉ
    # =================================================

    def confirm_booking(self, ticket_id: str) -> bool:

        # 1. Tìm vé trong danh sách liên kết đơn
        node = self._ticket_list.find_ticket(ticket_id)
        if node is None:
            return False

        ticket = node.get_data()

        # Chỉ xác nhận nếu vé hiện tại đang ở trạng thái khóa tạm thời (RESERVED)
        if ticket.get_status() != "RESERVED":
            return False

        # 2. Giải mã seat_id (Ví dụ: "B3") thành tọa độ row, col để xử lý ma trận
        seat_id = ticket.get_seat_id()
        row = ord(seat_id[0].upper()) - 65
        col = int(seat_id[1:]) - 1

        # 3. Chuyển trạng thái ghế từ RESERVED sang BOOKED trong ma trận
        # Hàm book_seat của showtime_controller sẽ tự động save_showtimes luôn
        booked = (
            self._showtime_controller
            .book_seat(
                ticket.get_showtime_id(),
                row,
                col
            )
        )
        if not booked:
            return False

        # 4. Cập nhật trạng thái vé thành BOOKED và lưu file tickets.csv
        ticket.set_status("BOOKED")
        self._io_handler.save_tickets(self._ticket_list)

        # 5. Ghi nhận doanh thu cho phim sau khi tiền đã về túi
        movie_node = (
            self._movie_controller
            .search_by_id(ticket.get_movie_id())
        )
        
        if movie_node is not None:
            movie = movie_node.get_data()
            
            # Gọi hàm add_revenue đã viết sẵn trong MovieData
            movie.add_revenue(ticket.get_price())
            
            # Lưu lại danh sách phim đã cập nhật doanh thu vào file movies.csv
            self._io_handler.save_movies(
                self._movie_controller.get_movie_list()
            )

        return True
   
    # =================================================
    # ĐẶT VÉ TRỰC TIẾP TẠI QUẦY (BỎ QUA GIỮ CHỖ)
    # =================================================

    def process_counter_booking(self, movie, showtime, row, col):
        from models.entities import TicketData, SeatStatus
        with self._booking_lock: 
            
            # 1. Kiểm tra trạng thái ghế và đổi trạng thái
            # Nếu có người khác đang mua online vừa nhanh tay hơn chiếm mất, hàm này sẽ trả về False
            success = self._showtime_controller.change_seat_status_by_admin(
                showtime.get_showtime_id(), row, col, SeatStatus.BOOKED
            )
            
            if not success:
                return False  # Trả về thất bại ngay lập tức vì ghế đã bị mua mất

            # 2. Các bước sinh mã vé và lưu file tiếp theo...
            ticket_id = self._generate_ticket_id()
            booking_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            new_ticket = TicketData(
                ticket_id=ticket_id,
                user_id="U_WALKIN",
                movie_id=movie.get_movie_id(),
                seat_id=f"{chr(65 + row)}{col + 1}",
                status="BOOKED",
                showtime_id=showtime.get_showtime_id(),
                room_id=showtime.get_room_id(),
                price=movie.get_price(),
                booking_time=booking_time_str
            )

            self._ticket_list.add_ticket(new_ticket)
            self._io_handler.save_tickets(self._ticket_list)

            return ticket_id
    

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
    
    # =================================================
    # TỰ ĐỘNG QUÉT VÀ HỦY VÉ HẾT HẠN THANH TOÁN
    # =================================================
    def cleanup_unfinished_reservations(self, timeout_minutes: int = 5) -> None:
        from datetime import datetime
        now = datetime.now()
        has_changed = False
        
        current = self._ticket_list.get_head()
        while current is not None:
            ticket = current.get_data()
            
            # Chỉ xử lý những vé đang ở trạng thái giữ chỗ (RESERVED)
            if ticket.get_status() == "RESERVED" and ticket.get_booking_time():
                try:
                    # Chuyển chuỗi lưu trong vé ngược lại thành đối tượng datetime để tính toán
                    booking_time = datetime.strptime(ticket.get_booking_time(), "%Y-%m-%d %H:%M:%S")
                    # Tính khoảng thời gian đã trôi qua (phút)
                    elapsed_minutes = (now - booking_time).total_seconds() / 60
                    
                    if elapsed_minutes > timeout_minutes:
                        # 1. Đổi seat_id (VD: "A5") thành chỉ số dòng, cột tương tự hàm cancel_booking của bạn
                        seat_id = ticket.get_seat_id()
                        row = ord(seat_id[0].upper()) - 65
                        col = int(seat_id[1:]) - 1
                        
                        # 2. Giải phóng ghế trong ma trận suất chiếu về trạng thái EMPTY
                        self._showtime_controller.release_seat(ticket.get_showtime_id(), row, col)
                        
                        # 3. Chuyển trạng thái vé thành CANCELLED
                        ticket.set_status("CANCELLED")
                        has_changed = True
                except ValueError:
                    # Bỏ qua nếu chuỗi thời gian bị lỗi định dạng
                    pass
                    
            current = current.get_next()
            
        # Nếu có sự thay đổi (có vé bị hủy), ghi lại vào file CSV để đồng bộ dữ liệu
        if has_changed:
            self._io_handler.save_tickets(self._ticket_list)

    def _sync_matrix_from_tickets(self):
        from models.entities import SeatStatus
        current = self._ticket_list.get_head()
        
        while current is not None:
            ticket = current.get_data()
            status = ticket.get_status()
            
            if status in ["BOOKED", "RESERVED"]:
                try:
                    # Bóc tách tọa độ
                    seat_id = ticket.get_seat_id()
                    row = ord(seat_id[0].upper()) - 65
                    col = int(seat_id[1:]) - 1
                    
                    # Dùng hàm của showtime_controller để ép lại trạng thái ghế
                    new_status = SeatStatus.BOOKED if status == "BOOKED" else SeatStatus.RESERVED
                    self._showtime_controller.change_seat_status_by_admin(
                        ticket.get_showtime_id(), row, col, new_status
                    )
                except (ValueError, IndexError, TypeError):
                    pass # Bỏ qua nếu dữ liệu vé cũ bị lỗi
                    
            current = current.get_next()
    # =================================================
    # ADMIN HỦY VÉ
    # =================================================
    def admin_cancel_ticket(self, ticket_id: str) -> bool:
        # Dùng lock nội bộ của BookingController để đảm bảo an toàn đa luồng
        with self._booking_lock:
            ticket_node = self._ticket_list.find_ticket(ticket_id)
            if not ticket_node:
                return False
                
            ticket = ticket_node.get_data()
            
            # Chỉ cho phép hủy nếu vé đang ở trạng thái BOOKED
            if ticket.get_status() != "BOOKED":
                return False
                
            # Giải phóng ghế thông qua showtime_controller trực tiếp
            seat_id = ticket.get_seat_id()
            row = ord(seat_id[0].upper()) - 65
            col = int(seat_id[1:]) - 1
            
            self._showtime_controller.release_seat(
                ticket.get_showtime_id(), row, col
            )
            
            # Cập nhật trạng thái vé thành CANCELLED
            ticket.set_status("CANCELLED")
            
            # Lưu lại danh sách vé vào file CSV
            self._io_handler.save_tickets(self._ticket_list)
            
            # Đồng bộ lại ma trận hiển thị ghế
            self._sync_matrix_from_tickets() 
        
            return True













