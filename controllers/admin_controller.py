from models.entities import SeatStatus
from controllers.movie_controller import MovieController
from controllers.booking_controller import BookingController
from controllers.showtime_controller import ShowtimeController 
from controllers.room_controller import RoomController

# =====================================================
# ADMIN CONTROLLER
# =====================================================

class AdminController:

    def __init__(
        self,
        movie_controller: MovieController,
        booking_controller: BookingController,
        showtime_controller: ShowtimeController,
        room_controller: RoomController
    ):

        self._movie_controller = movie_controller
        self._booking_controller = booking_controller
        self._showtime_controller = showtime_controller
        self._room_controller = room_controller

    # =================================================
    # TÍNH DOANH THU
    # =================================================

    def calculate_revenue(self):
        revenue = 0
        current = self._booking_controller.get_ticket_list().get_head()

        while current is not None:
            ticket = current.get_data()
            status = str(ticket.get_status()).strip().upper()
            
            if status == "BOOKED":
                revenue += ticket.get_price()

            current = current.get_next()

        return revenue
    
    # =================================================
    # ĐẾM PHIM
    # =================================================
    def count_movies(self):
        count = 0
        current = self._movie_controller.get_movie_list().get_head()
        
        while current is not None:
            count += 1
            current = current.get_next()
            
        return count

    # =================================================
    # ĐẾM VÉ
    # =================================================
    def count_tickets(self):
        count = 0
        current = self._booking_controller.get_ticket_list().get_head()
        
        while current is not None:
            count += 1
            current = current.get_next()
            
        return count

    # =================================================
    # TOP PHIM DOANH THU
    # =================================================
    def get_top_movies_by_revenue(self, limit=10):

        movie_revenue = []

        # Khởi tạo doanh thu = 0 cho tất cả phim
        for movie in self._movie_controller.get_movie_data():
            movie_revenue += [[movie.get_movie_id(), 0]]

        # Cộng doanh thu từ các vé đã BOOKED
        current = (
            self._booking_controller
            .get_ticket_list()
            .get_head()
        )

        while current is not None:

            ticket = current.get_data()

            status = str(
                ticket.get_status()
            ).strip().upper()

            if status == "BOOKED":

                movie_id = ticket.get_movie_id()

                # Duyệt tuần tự qua mảng cặp để cập nhật doanh thu
                for pair in movie_revenue:
                    if pair[0] == movie_id:
                        pair[1] += ticket.get_price()
                        break

            current = current.get_next()

        # Gán doanh thu tạm thời cho từng phim
        movies = self._movie_controller.get_movie_data()

        for movie in movies:

            revenue = 0
            # Tìm kiếm tuần tự mã phim để lấy ra doanh thu tổng tương ứng
            for pair in movie_revenue:
                if pair[0] == movie.get_movie_id():
                    revenue = pair[1]
                    break
            movie.set_revenue(revenue)

        # Gọi hàm sắp xếp Bubble Sort đã code tay trong danh sách liên kết
        self._movie_controller.get_movie_list().sort_by_revenue_logic()

        # Sau đó mới lấy dữ liệu đã được sắp xếp ra
        sorted_movies = self._movie_controller.get_movie_data()
        
        top_movies = []
        count = 0

        for movie in sorted_movies:
            if count >= limit:
                break
            top_movies += [movie]
            count += 1

        return top_movies

    # =================================================
    # BÁN VÉ TẠI QUẦY CHO KHÁCH
    # =================================================
    def sell_ticket_at_counter(self, movie, showtime, row, col):
        """
        Gọi xuống booking_controller để tạo vé trực tiếp cho khách tại quầy.
        Trả về ticket_id nếu thành công, False nếu thất bại.
        """
        return self._booking_controller.process_counter_booking(
            movie=movie,
            showtime=showtime,
            row=row,
            col=col
        )
    
    # =================================================
    # THỐNG KÊ TỔNG QUAN
    # =================================================

    def generate_report(self):

        return {

            "total_movies":
            self.count_movies(),

            "total_tickets":
            self.count_tickets(),

            "total_revenue":
            self.calculate_revenue(),

            "top_movies":
            self.get_top_movies_by_revenue()
        }
    # =================================================
    # LẤY DANH SÁCH VÉ ĐANG HOẠT ĐỘNG (ĐỂ HỦY)
    # =================================================
    def get_active_tickets(self):
        all_tickets = self._booking_controller.get_ticket_data()
        active_tickets = []
        
        for t in all_tickets:
            status = str(t.get_status()).strip().upper()
            if status == "BOOKED":
                active_tickets += [t]
                
        return active_tickets
    
    # =================================================
    # XÓA PHIM VÀ PHÒNG CHIẾU (TẦNG QUẢN LÝ TỔNG)
    # =================================================
    def admin_delete_movie(self, movie_id: str) -> bool:
        with self._booking_controller._booking_lock:
            showtimes = self._showtime_controller.get_showtime_data()
            for st in showtimes:
                if st.get_movie_id() == movie_id:
                    return False # Từ chối xóa vì đang có lịch chiếu

            success = self._movie_controller.delete_movie(movie_id)
            
            if success:
                # Gọi bản k có lock vì đang giữ lock rồi
                self._booking_controller._refresh_booking_data_no_lock()
                
            return success
    def admin_delete_room(self, room_id: str) -> bool:
        showtimes = self._showtime_controller.get_showtime_data()
        for st in showtimes:
            if st.get_room_id() == room_id:
                return False # Từ chối xóa

        return self._room_controller.delete_room(room_id)