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
        # Đã sửa: Gọi thuật toán sắp xếp (Bubble Sort) tự code ở tầng Data Structure
        self._movie_controller.sort_movies_by_revenue()
        
        # Sau khi mảng đã được sắp xếp, lấy dữ liệu ra
        sorted_movies = self._movie_controller.get_movie_data()

        # Trả về số lượng theo limit
        return sorted_movies[:limit]
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
