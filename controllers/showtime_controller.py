from models.entities import Showtime, SeatStatus
from data_structures.linked_lists import ShowtimeLinkedList
from models.file_io import FileIOHandler

class ShowtimeController:

    def __init__(
        self,
        io_handler: FileIOHandler,
        movie_controller
    ):

        self._io_handler = io_handler
        self._movie_controller = movie_controller
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
                num_str = ""
                idx = 0
                for char in st_id:
                    if idx > 0: 
                        num_str += char
                    idx += 1
                    
                num = int(num_str)
                if num > max_id: 
                    max_id = num
            except ValueError: 
                pass
            current = current.get_next()
            
        return f"S{max_id + 1:09d}"
        
    # =================================================
    # ADD SHOWTIME 
    # =================================================

    def add_showtime(
        self,
        st: Showtime
    ) -> bool:

        from datetime import datetime, timedelta

        existed = (
            self.find_showtime(
                st.get_showtime_id()
            )
        )

        if existed:
            return False

        movie_node_new = self._movie_controller.search_by_id(st.get_movie_id())
        duration_new = 120  # Mặc định rạp phim là 120 phút nếu lỡ không tìm thấy phim
        
        if movie_node_new:
            movie_new = movie_node_new.get_data()
            duration_new = movie_new.get_duration() # Đảm bảo MovieData có hàm lấy thời lượng này

        format_str = "%Y-%m-%d %H:%M"
        
        
        # 1. Validate và Parse ngày giờ an toàn
        try:
            if isinstance(st.get_start_time(), str):
                start_new = datetime.strptime(st.get_start_time(), format_str)
            else:
                start_new = st.get_start_time()
        except ValueError:
            # Nếu Admin nhập sai định dạng, hàm trả về False để UI báo lỗi
            return False  
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
                movie_node_old = self._movie_controller.search_by_id(old_st.get_movie_id())
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

        st.set_start_time(new_start_time)

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
                    status = str(
                    ticket.get_status()
                ).strip().upper()

                    if status in ["BOOKED", "RESERVED"]:
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

        return matrix.book_seat(
                row,
                col
            )

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

            result += [current.get_data()]

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
    
    # =================================================
    # LẤY DANH SÁCH PHIM & SUẤT CHIẾU THEO NGÀY
    # =================================================
    def get_schedule_by_date(self, target_date: str):
        daily_schedule = []
        
        current = self._showtime_list.get_head()

        while current is not None:
            st = current.get_data()
            # Nếu suất chiếu khớp với ngày khách chọn
            if self.extract_date(st) == target_date:
                movie_id = st.get_movie_id()
                
                found_group = None

                # Tìm xem phim đã tồn tại trong danh sách chưa
                for group in daily_schedule:
                    if group[0].get_movie_id() == movie_id:
                        found_group = group
                        break
                
                # Nếu chưa có thì tạo nhóm mới
                if found_group is None:
                    movie_node = self._movie_controller.search_by_id(movie_id)
                    if movie_node is not None:
                        found_group = [
                            movie_node.get_data(),
                            []
                        ]
                        daily_schedule += [found_group]
                
                # Thêm suất chiếu vào nhóm phim tương ứng
                if found_group is not None:
                    found_group[1] += [st]
                    
            current = current.get_next()
        return daily_schedule
    # =================================================
    # HÀM HỖ TRỢ TÁCH NGÀY GIỜ CHO GIAO DIỆN
    # =================================================
    def extract_date(self, showtime):
        """Tách lấy ngày từ object Showtime"""
        start = str(showtime.get_start_time())
        date_str = ""
        for char in start:
            if char == " ":  # Gặp khoảng trắng thì dừng (chỉ lấy phần trước khoảng trắng)
                break
            date_str += char
        return date_str

    def extract_time(self, showtime):
        """Tách lấy giờ từ object Showtime"""
        start = str(showtime.get_start_time())
        time_str = ""
        found_space = False
        for char in start:
            if found_space:
                time_str += char
            elif char == " ": # Bắt đầu lấy ký tự từ sau khoảng trắng
                found_space = True
        return time_str

    def get_unique_sorted_dates(self, showtimes_list):
        """Lọc trùng và Sắp xếp mảng Ngày (Bubble Sort)"""
        # 1. Lấy tất cả các ngày
        raw_dates = []
        for s in showtimes_list:
            raw_dates += [self.extract_date(s)]
            
        # 2. Lọc trùng (Thay cho set)
        unique_dates = []
        for d in raw_dates:
            is_duplicate = False
            for u in unique_dates:
                if u == d:
                    is_duplicate = True
                    break
            if not is_duplicate and d != "":
                unique_dates += [d]
                
        # 3. Thuật toán sắp xếp nổi bọt (Thay cho sorted)
        n = len(unique_dates)
        for i in range(n):
            for j in range(0, n - i - 1):
                if unique_dates[j] > unique_dates[j + 1]:
                    # Hoán đổi vị trí
                    temp = unique_dates[j]
                    unique_dates[j] = unique_dates[j + 1]
                    unique_dates[j + 1] = temp
                    
        return unique_dates

    def get_unique_sorted_times(self, showtimes_list):
        """Lọc trùng và Sắp xếp mảng Giờ (Bubble Sort)"""
        raw_times = []
        for s in showtimes_list:
            raw_times += [self.extract_time(s)]
            
        unique_times = []
        for t in raw_times:
            is_duplicate = False
            for u in unique_times:
                if u == t:
                    is_duplicate = True
                    break
            if not is_duplicate and t != "":
                unique_times += [t]
                
        n = len(unique_times)
        for i in range(n):
            for j in range(0, n - i - 1):
                if unique_times[j] > unique_times[j + 1]:
                    temp = unique_times[j]
                    unique_times[j] = unique_times[j + 1]
                    unique_times[j + 1] = temp
                    
        return unique_times
    
    # =================================================
    # LẤY DANH SÁCH SUẤT CHIẾU THEO MÃ PHIM (BỊ THIẾU)
    # =================================================
    def get_showtimes_by_movie(self, movie_id: str):
        """Gọi xuống danh sách liên kết đơn để lọc suất chiếu theo mã phim"""
        return self._showtime_list.find_by_movie(movie_id)
    
    # =================================================
    # TÌM SUẤT CHIẾU CHÍNH XÁC THEO NGÀY GIỜ
    # =================================================
    def find_exact_showtime(self, movie_id: str, target_date: str, target_time: str):
        # Bắt đầu duyệt từ đầu danh sách liên kết
        current = self._showtime_list.get_head()
        
        while current is not None:
            st = current.get_data()
            
            # 1. Kiểm tra có đúng ID phim không
            if st.get_movie_id() == movie_id:
                
                # 2. Dùng hàm extract_date và extract_time đã code tay lúc nãy để lấy chuỗi
                st_date = self.extract_date(st)
                st_time = self.extract_time(st)
                
                # 3. Trùng cả ngày và giờ thì chốt luôn suất chiếu này
                if st_date == target_date and st_time == target_time:
                    return st
                    
            # Nhảy sang Node tiếp theo
            current = current.get_next()
            
        # Duyệt hết danh sách mà không thấy thì trả về None
        return None