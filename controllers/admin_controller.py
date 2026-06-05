from models.entities import SeatStatus
from controllers.movie_controller import MovieController
from controllers.booking_controller import BookingController


# =====================================================
# ADMIN CONTROLLER
# =====================================================

class AdminController:

    def __init__(
        self,
        movie_controller: MovieController,
        booking_controller: BookingController
    ):

        self._movie_controller = (
            movie_controller
        )

        self._booking_controller = (
            booking_controller
        )

    # =================================================
    # TÍNH DOANH THU
    # =================================================

    def calculate_revenue(self):
        revenue = 0
        current = self._booking_controller.get_ticket_list().get_head()

        while current is not None:
            ticket = current.get_data()
            
            # Ép kiểu status về chuỗi in hoa để tránh lỗi so sánh (Int vs String)
            status = str(ticket.get_status()).strip().upper()
            
            # Chấp nhận cả chữ BOOKED hoặc số 2
            if status in ["BOOKED", "2", "SEATSTATUS.BOOKED"]:
                revenue += ticket.get_price()

            current = current.get_next()

        return revenue
    
    # =================================================
    # ĐẾM PHIM
    # =================================================
    def count_movies(self):
        # Đã sửa: Đếm trực tiếp trên mảng trả về
        return len(self._movie_controller.get_movie_data())

    # =================================================
    # ĐẾM VÉ
    # =================================================
    def count_tickets(self):
        # Đã sửa: Đếm trực tiếp trên mảng trả về
        return len(self._booking_controller.get_ticket_data())

    # =================================================
    # TOP PHIM DOANH THU
    # =================================================
    def get_top_movies_by_revenue(self, limit=10):

        movie_revenue = {}

        # Khởi tạo doanh thu = 0 cho tất cả phim
        for movie in self._movie_controller.get_movie_data():
            movie_revenue[movie.get_movie_id()] = 0

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

            if status in [
                "BOOKED",
                "2",
                "SEATSTATUS.BOOKED"
            ]:

                movie_id = ticket.get_movie_id()

                if movie_id in movie_revenue:
                    movie_revenue[movie_id] += ticket.get_price()

            current = current.get_next()

        # Gán doanh thu tạm thời cho từng phim
        movies = self._movie_controller.get_movie_data()

        for movie in movies:

            revenue = movie_revenue.get(
                movie.get_movie_id(),
                0
            )

            movie._revenue = revenue

        # Sắp xếp giảm dần theo doanh thu
        movies.sort(
            key=lambda m: m.get_revenue(),
            reverse=True
        )

        return movies[:limit]
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
            if status in ["BOOKED", "2", "SEATSTATUS.BOOKED"]:
                active_tickets.append(t)
                
        return active_tickets