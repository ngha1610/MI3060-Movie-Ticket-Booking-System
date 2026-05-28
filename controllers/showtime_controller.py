from models.entities import (
    Showtime,
    SeatStatus
)

from data_structures.linked_lists import (
    ShowtimeLinkedList
)

from data_structures.file_io import (
    FileIOHandler
)

class ShowtimeController:

    def __init__(
        self,
        io_handler: FileIOHandler
    ):

        self._io_handler = io_handler

        self._showtime_list = (
            ShowtimeLinkedList()
        )

        self._io_handler.load_showtimes(
            self._showtime_list
        )
    def generate_showtime_id(self):
        current = self._showtime_list.get_head()
        if current is None: 
            return "S000000001"
            
        max_id = 0
        while current is not None:
            st_id = current.get_data().get_showtime_id()
            try:
                num = int(st_id[1:])
                if num > max_id: 
                    max_id = num
            except ValueError: 
                pass
            current = current.get_next()
            
        # Đưa return ra ngoài thẳng hàng với lệnh while
        return f"S{max_id + 1:09d}"
        
    # =================================================
    # ADD SHOWTIME (ĐÃ FIX: TỰ TÍNH END_TIME QUA MOVIE_CONTROLLER)
    # =================================================

    def add_showtime(
        self,
        st: Showtime,
        movie_controller  # Truyền thêm movie_controller vào đây để mượn data phim
    ) -> bool:

        from datetime import datetime, timedelta

        existed = (
            self.find_showtime(
                st.get_showtime_id()
            )
        )

        if existed:
            return False

        # 1. TÍNH END_TIME CHO CA CHIẾU MỚI (ĐANG MUỐN THÊM)
        # Vì hàm tìm kiếm của m trả về Node (theo liên kết đơn), ta phải .get_data() để lấy MovieData
        movie_node_new = movie_controller.search_by_id(st.get_movie_id())
        duration_new = 120  # Mặc định rạp phim là 120 phút nếu lỡ không tìm thấy phim
        
        if movie_node_new:
            movie_new = movie_node_new.get_data()
            duration_new = movie_new.get_duration() # Đảm bảo MovieData có hàm lấy thời lượng này

        format_str = "%Y-%m-%d %H:%M"
        
        # Parse chuỗi start_time của ca mới thành đối tượng datetime để cộng trừ
        if isinstance(st.get_start_time(), str):
            start_new = datetime.strptime(st.get_start_time(), format_str)
        else:
            start_new = st.get_start_time()
            
        # Thời gian kết thúc = Bắt đầu + Thời lượng phim
        end_new = start_new + timedelta(minutes=duration_new)

        # Duyệt danh sách ca chiếu cũ để check trùng
        current = (
            self._showtime_list
            .get_head()
        )

        while current is not None:
            old_st = current.get_data()

            # Kiểm tra nếu trùng phòng chiếu
            if old_st.get_room_id() == st.get_room_id():
                
                # 2. TÍNH END_TIME CHO CA CHIẾU CŨ (ĐANG CÓ TRÊN HỆ THỐNG)
                movie_node_old = movie_controller.search_by_id(old_st.get_movie_id())
                duration_old = 120
                if movie_node_old:
                    movie_old = movie_node_old.get_data()
                    duration_old = movie_old.get_duration()

                # Parse start_time của ca cũ
                if isinstance(old_st.get_start_time(), str):
                    start_old = datetime.strptime(old_st.get_start_time(), format_str)
                else:
                    start_old = old_st.get_start_time()
                    
                end_old = start_old + timedelta(minutes=duration_old)

                # Thuật toán chồng lấn thời gian (Overlapping)
                if (start_new < end_old) and (end_new > start_old):
                    return False  # Bị trùng khung giờ chiếu trong cùng 1 phòng -> Từ chối!

            current = current.get_next()

        # Nếu vượt qua hết vòng lặp => Phòng trống lịch hoàn toàn
        self._showtime_list.add_showtime(st)
        self._io_handler.save_showtimes(self._showtime_list)
        return True

    # =================================================
    # UPDATE SHOWTIME
    # =================================================

    def update_showtime(
        self,
        showtime_id,
        new_start_time
    ) -> bool:

        node = (
            self.find_showtime(
                showtime_id
            )
        )

        if node is None:
            return False

        st = node.get_data()

        st._start_time = new_start_time

        self._io_handler.save_showtimes(
            self._showtime_list
        )

        return True

    # =================================================
    # DELETE SHOWTIME
    # =================================================

    def delete_showtime(
        self,
        showtime_id: str,
        ticket_controller=None
    ) -> bool:

        # nếu đã có vé thì không cho xóa
        if ticket_controller is not None:

            tickets = (
                ticket_controller
                .get_ticket_data()
            )

            for ticket in tickets:

                if (
                    ticket.get_showtime_id()
                    ==
                    showtime_id
                ):
                    return False

        success = (
            self._showtime_list
            .remove_showtime(
                showtime_id
            )
        )

        if success:

            self._io_handler.save_showtimes(
                self._showtime_list
            )

        return success

    # =================================================
    # FIND SHOWTIME
    # =================================================

    def find_showtime(
        self,
        showtime_id: str
    ):

        return (
            self._showtime_list
            .find_showtime(
                showtime_id
            )
        )

    # =================================================
    # CHECK SEAT STATUS
    # =================================================

    def check_seat_status(
        self,
        showtime_id: str,
        row: int,
        col: int
    ) -> bool:

        node = (
            self.find_showtime(
                showtime_id
            )
        )

        if node is None:
            return False

        matrix = (
            node.get_data()
            .get_seat_matrix()
        )

        return (
            matrix.check_status(
                row,
                col
            )
            ==
            SeatStatus.EMPTY
        )

    # =================================================
    # BOOK SEAT
    # =================================================

    def book_seat(
        self,
        showtime_id: str,
        row: int,
        col: int
    ) -> bool:

        node = (
            self.find_showtime(
                showtime_id
            )
        )

        if node is None:
            return False

        matrix = (
            node.get_data()
            .get_seat_matrix()
        )

        success = (
            matrix.book_seat(
                row,
                col
            )
        )

        if success:

            self._io_handler.save_showtimes(
                self._showtime_list
            )

        return success

    # =================================================
    # RELEASE SEAT
    # =================================================

    def release_seat(
        self,
        showtime_id: str,
        row: int,
        col: int
    ) -> bool:

        node = (
            self.find_showtime(
                showtime_id
            )
        )

        if node is None:
            return False

        matrix = (
            node.get_data()
            .get_seat_matrix()
        )

        matrix.release_seat(
            row,
            col
        )

        self._io_handler.save_showtimes(
            self._showtime_list
        )

        return True

    # =================================================
    # GET SHOWTIME LIST
    # =================================================

    def get_showtime_list(self):

        return self._showtime_list

    # =================================================
    # GET SHOWTIME DATA
    # =================================================

    def get_showtime_data(self):

        result = []

        current = (
            self._showtime_list
            .get_head()
        )

        while current is not None:

            result.append(
                current.get_data()
            )

            current = (
                current.get_next()
            )

        return result
    
    def change_seat_status_by_admin(self, showtime_id: str, row: int, col: int, new_status: int) -> bool:
        node = self.find_showtime(showtime_id)
        if node is None:
            return False
        
        matrix = node.get_data().get_seat_matrix()
        success = matrix.set_seat_status(row, col, new_status)
    
        if success:
            self._io_handler.save_showtimes(self._showtime_list)
        return success





