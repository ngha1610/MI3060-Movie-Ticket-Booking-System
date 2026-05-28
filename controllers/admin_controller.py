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

        current = (
            self._booking_controller
            .get_ticket_list()
            .get_head()
        )

        while current is not None:

            ticket = current.get_data()

            # chỉ tính vé đã đặt thành công
            if (
               ticket.get_status() 
               == SeatStatus.BOOKED
            ):

                revenue += (
                    ticket.get_price()
                )

            current = (
                current.get_next()
            )

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

    def get_top_movies_by_revenue(
        self,
        limit=5
    ):

        movies = (
            self._movie_controller
            .get_movie_data()
        )

        sorted_movies = sorted(
            movies,
            key=lambda movie:
            movie.get_revenue(),
            reverse=True
        )

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
