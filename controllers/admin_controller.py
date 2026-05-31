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

        count = 0

        current = (
            self._movie_controller
            .get_movie_list()
            .get_head()
        )

        while current is not None:

            count += 1

            current = (
                current.get_next()
            )

        return count

    # =================================================
    # ĐẾM VÉ
    # =================================================

    def count_tickets(self):

        count = 0

        current = (
            self._booking_controller
            .get_ticket_list()
            .get_head()
        )

        while current is not None:

            count += 1

            current = (
                current.get_next()
            )

        return count

 # =================================================
    # TOP PHIM DOANH THU
    # =================================================

    def get_top_movies_by_revenue(self, limit=5):
        movies = self._movie_controller.get_movie_data()
        
        # B1: Khởi tạo bảng tạm để tự động tính lại tiền dựa trên 17 nghìn vé thực tế
        movie_revenues = {m.get_movie_id(): 0 for m in movies}
        
        # B2: Quét toàn bộ kho vé để cộng dồn tiền cho từng phim
        current_ticket = self._booking_controller.get_ticket_list().get_head()
        while current_ticket is not None:
            ticket = current_ticket.get_data()
            status = str(ticket.get_status()).strip().upper()
            
            if status in ["BOOKED", "2", "SEATSTATUS.BOOKED"]:
                m_id = ticket.get_movie_id()
                if m_id in movie_revenues:
                    movie_revenues[m_id] += ticket.get_price()
                    
            current_ticket = current_ticket.get_next()
            
        # B3: Cập nhật doanh thu thực tế vào danh sách phim
        for m in movies:
            m._revenue = movie_revenues.get(m.get_movie_id(), 0)
            
        # B4: Sắp xếp từ cao xuống thấp
        sorted_movies = sorted(movies, key=lambda movie: movie.get_revenue(), reverse=True)

        return sorted_movies[:limit]
    
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
