from models.entities import (
    Showtime,
    TicketData,
    UserData,
    MovieData,
    SeatStatus
)
from data_structures.linked_lists import TicketLinkedList
from models.file_io import FileIOHandler
from controllers.showtime_controller import ShowtimeController
from controllers.movie_controller import MovieController
from datetime import datetime
import threading
from controllers.room_controller import RoomController

# =====================================================
# BOOKING CONTROLLER
# =====================================================
class BookingController:
   
    def __init__(
        self,
        io_handler: FileIOHandler,
        showtime_controller: ShowtimeController,
        movie_controller: MovieController,
        room_controller: RoomController
    ):

        self._io_handler = io_handler

        self._showtime_controller = (
            showtime_controller
        )

        self._movie_controller = (
            movie_controller
        )
        self._room_controller = room_controller

        self._ticket_list = (
            TicketLinkedList()
        )

        self._booking_lock = threading.Lock()

        self._io_handler.load_tickets(
            self._ticket_list
        )
        
        self._sync_matrix_from_tickets()

    # =================================================
    # HÀM HỖ TRỢ: TÁCH TỌA ĐỘ GHẾ TỪ CHUỖI (CODE CHAY)
    # =================================================
    def parse_seat_id(self, seat_id: str):
        seat_id = str(seat_id)
        
        # 1. Tách chữ cái (Hàng) và tự ép về mã ASCII in hoa không dùng .upper()
        row = ord(seat_id[0].upper()) - 65
        
        # 2. Tách số (Cột) bằng vòng lặp 
        col_str = ""
        idx = 0
        for char in seat_id:
            if idx > 0: 
                col_str += char
            idx += 1
        col = int(col_str) - 1
        
        return row, col

    # =================================================
    # TẠO MÃ VÉ (ĐÃ SỬA: DUYỆT LINKED LIST TÌM MAX ID CHỐNG TRÙNG)
    # =================================================

    def _generate_ticket_id(self):
        current = self._ticket_list.get_head()
        
        # Nếu danh sách rỗng mã số 1
        if current is None:
            return "T000000001"
            
        max_id = 0
        
        # Duyệt từ đầu đến cuối danh sách để tìm ID lớn nhất
        while current is not None:
            ticket = current.get_data()
            ticket_id = ticket.get_ticket_id()
            
            # Cắt chữ 'T', lấy phần số ép sang kiểu Int
            number = int(ticket_id[1:])
            
            if number > max_id:
                max_id = number
                
            current = current.get_next()
            
        return f"T{max_id + 1:09d}"

    # =================================================
    # ĐẶT VÉ
    # =================================================
  
    # =================================================
    # ĐẶT VÉ 
    # =================================================
    def process_booking(self, user: UserData, movie: MovieData, showtime: Showtime, seats: list) -> list:
        """
        Xử lý đặt nhiều ghế cùng lúc dưới dạng toán tử toàn vẹn (Atomic).
        """
        with self._booking_lock:
            
            self._refresh_booking_data_no_lock()

            # Xem TẤT CẢ các ghế chọn có thực sự trống không
            for row, col in seats:
                available = self._showtime_controller.check_seat_status(showtime.get_showtime_id(), row, col)
                if not available:
                    return [] # Chỉ cần 1 ghế bị chiếm, ngay lập tức hủy toàn bộ tiến trình

            # Khi chắc chắn mọi ghế đều hợp lệ
            generated_ticket_ids = []
            price = movie.get_base_price()
            booking_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            matrix = showtime.get_seat_matrix()
            for row, col in seats:
                matrix.reserve_seat(row, col) # Khóa tạm thời trên RAM (RESERVED)
                seat_id = matrix.generate_seat_id(row, col)
                ticket_id = self._generate_ticket_id()
                
                ticket = TicketData(
                    ticket_id=ticket_id,
                    user_id=user.get_user_id(),
                    movie_id=movie.get_movie_id(),
                    seat_id=seat_id,
                    status="RESERVED",
                    showtime_id=showtime.get_showtime_id(),
                    room_id=showtime.get_room_id(),
                    price=price,
                    booking_time=booking_time_str
                )
                self._ticket_list.add_ticket(ticket)
                generated_ticket_ids += [ticket_id]

            # GHI FILE TICKETS DUY NHẤT 1 LẦN 
            self._io_handler.save_tickets(self._ticket_list)
            return generated_ticket_ids

    # =================================================
    # XÁC NHẬN THANH TOÁN THEO CỤM (BULK CONFIRM)
    # =================================================
    def confirm_bookings_bulk(self, ticket_ids: list) -> bool:
        """
        Xác nhận toàn bộ danh sách vé cùng lúc và chỉ ghi file CSV đúng 1 lần duy nhất ở cuối hàm.
        """
        with self._booking_lock:
            has_changed = False
            
            for ticket_id in ticket_ids:
                node = self._ticket_list.find_ticket(ticket_id)
                if node is None:
                    continue
                    
                ticket = node.get_data()
                if str(ticket.get_status()) != "RESERVED":
                    continue

                row, col = self.parse_seat_id(ticket.get_seat_id())

                # Chuyển trạng thái ghế trên RAM
                booked = self._showtime_controller.book_seat(ticket.get_showtime_id(), row, col)
                if booked:
                    ticket.set_status("BOOKED")
                    has_changed = True

                    # Cộng doanh thu tạm thời trên RAM
                    movie_node = self._movie_controller.search_by_id(ticket.get_movie_id())
                    if movie_node is not None:
                        movie = movie_node.get_data()
                        movie.add_revenue(ticket.get_price())

            # Sau khi vòng lặp xử lý xong hết trên RAM, tiến hành chốt ghi file đúng 1 lần duy nhất!
            if has_changed:
                self._io_handler.save_tickets(self._ticket_list)
                self._io_handler.save_movies(self._movie_controller.get_movie_list())
                return True
                
            return False

    # =================================================
    # ĐẶT VÉ TRỰC TIẾP TẠI QUẦY (BỎ QUA GIỮ CHỖ)
    # =================================================

    def process_counter_booking(self, movie, showtime, row, col):
        
        with self._booking_lock: 
            
            # 1. Kiểm tra trạng thái ghế và đổi trạng thái
            # Kiểm tra ghế trống trước khi đặt
            is_available = self._showtime_controller.check_seat_status(
                showtime.get_showtime_id(), row, col
            )
            if not is_available:
                return False

            # Rồi mới thực hiện đặt ghế
            self._showtime_controller.book_seat(showtime.get_showtime_id(), row, col)
                    
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
                price=movie.get_base_price(),
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

                result += [ticket]

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

            result += [current.get_data()]

            current = (
                current.get_next()
            )

        return result
    
    # =================================================
    # TỰ ĐỘNG QUÉT VÀ HỦY VÉ HẾT HẠN THANH TOÁN
    # =================================================
    def cleanup_unfinished_reservations(self, timeout_minutes: int = 5) -> None:
        
        now = datetime.now()
        
        with self._booking_lock:
            has_changed = False

            current = self._ticket_list.get_head()
            while current is not None:
                ticket = current.get_data()
                
                # Chỉ xử lý những vé đang ở trạng thái giữ chỗ (RESERVED)
                if str(ticket.get_status()) == "RESERVED" and ticket.get_booking_time():
                    try:
                        # Chuyển chuỗi lưu trong vé thành đối tượng datetime để tính toán
                        booking_time = datetime.strptime(ticket.get_booking_time(), "%Y-%m-%d %H:%M:%S")
                        # Tính khoảng thời gian đã trôi qua (phút)
                        elapsed_minutes = (now - booking_time).total_seconds() / 60
                        
                        if elapsed_minutes > timeout_minutes:
                            # 1. Đổi seat_id (VD: "A5") thành chỉ số dòng, cột 
                            row, col = self.parse_seat_id(ticket.get_seat_id())
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
        
        current = self._ticket_list.get_head()
        
        # Thay Dictionary {} bằng Mảng 2 chiều [[id, obj], ...]
        showtime_map = []
        curr_st = self._showtime_controller.get_showtime_list().get_head()
        while curr_st is not None:
            st_obj = curr_st.get_data()
            showtime_map += [[st_obj.get_showtime_id(), st_obj]]
            curr_st = curr_st.get_next()
        
        while current is not None:
            ticket = current.get_data()
            status = str(ticket.get_status())
            
            if status in ["BOOKED", "RESERVED"]:
                try:
                    row, col = self.parse_seat_id(ticket.get_seat_id())
                    
                    # Tìm thủ công trong mảng thay cho showtime_map.get()
                    showtime = None
                    target_st_id = ticket.get_showtime_id()
                    for item in showtime_map:
                        if item[0] == target_st_id:
                            showtime = item[1]
                            break

                    if showtime:
                        matrix = showtime.get_seat_matrix()
                        new_status = SeatStatus.BOOKED if status == "BOOKED" else SeatStatus.RESERVED
                        matrix.set_seat_status(row, col, new_status)
                except Exception:
                    pass
                    
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
            if str(ticket.get_status()) != "BOOKED":
                return False
                
            # Giải phóng ghế thông qua showtime_controller trực tiếp
            row, col = self.parse_seat_id(ticket.get_seat_id())
            
            self._showtime_controller.release_seat(
                ticket.get_showtime_id(), row, col
            )
            
            # Cập nhật trạng thái vé thành CANCELLED
            ticket.set_status("CANCELLED")
            
            movie_node = self._movie_controller.search_by_id(ticket.get_movie_id())
            if movie_node is not None:
                movie = movie_node.get_data()
                movie.add_revenue(-ticket.get_price()) # Trừ đi giá vé
                self._io_handler.save_movies(self._movie_controller.get_movie_list()) # Lưu lại file phim
            # Lưu lại danh sách vé vào file CSV
            self._io_handler.save_tickets(self._ticket_list)
            
            # Đồng bộ lại ma trận hiển thị ghế
            self._sync_matrix_from_tickets() 
        
            return True

    def _refresh_booking_data_no_lock(self):
    # private, dùng nội bộ
            self._ticket_list.clear()
            self._io_handler.load_tickets(self._ticket_list)
            current_st = (
                self._showtime_controller
                .get_showtime_list()
                .get_head()
            )

            while current_st is not None:

                matrix = (
                    current_st
                    .get_data()
                    .get_seat_matrix()
                )

                matrix.reset_all()

                current_st = current_st.get_next()
            self._sync_matrix_from_tickets()

    def refresh_booking_data(self):
    #Dùng TỪ BÊN NGOÀI (UI, các controller khác).
        with self._booking_lock:
            self._refresh_booking_data_no_lock()









