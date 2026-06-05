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
  
    # =================================================
    # ĐẶT VÉ (ĐÃ TỐI ƯU: XÓA LỆNH LOAD_SHOWTIMES GÂY RÁC)
    # =================================================
    def process_booking(self, user: UserData, movie: MovieData, showtime: Showtime, seats: list) -> list:
        """
        Xử lý đặt nhiều ghế cùng lúc dưới dạng toán tử toàn vẹn (Atomic).
        """
        with self._booking_lock:
            # 1. ĐỒNG BỘ TRÊN RAM: Làm sạch và nạp lại vé từ tickets.csv để cập nhật sơ đồ ghế mới nhất
            from data_structures.linked_lists import TicketLinkedList
            self._ticket_list = TicketLinkedList()
            self._io_handler.load_tickets(self._ticket_list)
               
            self._sync_matrix_from_tickets()
            
            # 2. BƯỚC KIỂM TRA TRƯỚC (CHECK PHASE): Xem TẤT CẢ các ghế chọn có thực sự trống không
            for row, col in seats:
                available = self._showtime_controller.check_seat_status(showtime.get_showtime_id(), row, col)
                if not available:
                    return [] # Chỉ cần 1 ghế bị chiếm, ngay lập tức hủy toàn bộ tiến trình

            # 3. BƯỚC THỰC THI (EXECUTE PHASE): Khi chắc chắn mọi ghế đều hợp lệ
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
                generated_ticket_ids.append(ticket_id)

            # 4. GHI FILE TICKETS DUY NHẤT 1 LẦN (Tuyệt đối KHÔNG ghi file showtimes tĩnh!)
            self._io_handler.save_tickets(self._ticket_list)
            return generated_ticket_ids

    # =================================================
    # VŨ KHÍ SIÊU TỐC: XÁC NHẬN THANH TOÁN THEO CỤM (BULK CONFIRM)
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
                if ticket.get_status() != "RESERVED":
                    continue

                seat_id = ticket.get_seat_id()
                row = ord(seat_id[0].upper()) - 65
                col = int(seat_id[1:]) - 1

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
        
        # 🛡️ BỘ KHỬ VÒNG LẶP: Lưu địa chỉ các Node vé đã duyệt qua trên RAM
        visited_nodes = set()

        showtime_map = {}
        curr_st = self._showtime_controller.get_showtime_list().get_head()
        while curr_st is not None:
            st_obj = curr_st.get_data()
            showtime_map[st_obj.get_showtime_id()] = st_obj
            curr_st = curr_st.get_next()
        
        while current is not None:
            # Nếu địa chỉ Node này đã tồn tại trong Set -> Linked List đang bị lặp vòng tròn ngầm
            if id(current) in visited_nodes:
                print("⚠️ [PHÁT HIỆN] Cấu trúc Danh sách liên kết vé bị lặp vòng! Đã tự động ngắt lệnh break để cứu Web.")
                break
            visited_nodes.add(id(current)) # Ghi nhớ Node đã xử lý
            
            ticket = current.get_data()
            status = ticket.get_status()
            
            # Chỉ đồng bộ các vé có trạng thái đã đặt hoặc đang giữ chỗ
            if status in ["BOOKED", "RESERVED"]:
                try:
                    seat_id = ticket.get_seat_id()
                    row = ord(seat_id[0].upper()) - 65
                    col = int(seat_id[1:]) - 1
                    
                    # Tìm đúng suất chiếu tĩnh trên RAM và đổi trạng thái ghế đó thành BOOKED/RESERVED
                    showtime = showtime_map.get(
                        ticket.get_showtime_id()
                    )

                    if showtime:
                        matrix = showtime.get_seat_matrix()
                        new_status = SeatStatus.BOOKED if status == "BOOKED" else SeatStatus.RESERVED
                        matrix.set_seat_status(row, col, new_status)
                except (ValueError, IndexError, TypeError):
                    pass # Bỏ qua nếu dòng vé đó bị lỗi định dạng chuỗi, không làm sập cả hệ thống
                    
            current = current.get_next()
            
        # ❌ TUYỆT ĐỐI KHÔNG CÓ LỆNH SAVE_SHOWTIMES Ở ĐÂY VÌ SHOWTIMES LÀ FILE TĨNH!
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

    def refresh_booking_data(self):
        """Hàm làm mới ma trận ghế siêu tốc bằng cách nạp lại duy nhất file tickets.csv"""
        with self._booking_lock:
            # Tạo danh sách liên kết vé mới tinh để nạp sạch dữ liệu từ ổ cứng lên RAM
            from data_structures.linked_lists import TicketLinkedList
            self._ticket_list = TicketLinkedList()
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

                for r in range(matrix.get_rows()):
                    for c in range(matrix.get_cols()):
                        from models.entities import SeatStatus

                        matrix.set_seat_status(
                            r,
                            c,
                            SeatStatus.EMPTY
                        )

                current_st = current_st.get_next()
            self._sync_matrix_from_tickets()











