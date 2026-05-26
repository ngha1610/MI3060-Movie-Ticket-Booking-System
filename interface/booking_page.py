import streamlit as st

from services.booking_service import BookingService

from utils.csv_handler import CSVHandler

from datastructures.seat_matrix import SeatMatrix


booking = BookingService()


SHOWTIME_FILE = (

    "data/showtimes.csv"

)


def booking_page():

    if (

        "user"

        not in

        st.session_state

    ):

        st.error(

            "Phải đăng nhập"

        )

        return

    movie = (

        st.session_state

        ["booking"]

    )

    st.title(

        "Đặt vé"

    )

    st.write(

        movie["title"]

    )

    showtimes = (

        CSVHandler.load(

            SHOWTIME_FILE

        )
    )

    movie_showtimes = []

    for show in showtimes:

        if (

            show["movie_id"]

            == movie

            ["movie_id"]

        ):

            movie_showtimes.append(

                show

            )

    if len(

        movie_showtimes

    ) == 0:

        st.warning(

            "Chưa có suất"

        )

        return

    selected = (

        st.selectbox(

            "Suất chiếu",

            movie_showtimes,

            format_func=

            lambda x:

            x["time"]

        )
    )

    rows = int(

        selected["rows"]

    )

    cols = int(

        selected["cols"]

    )

    seat = SeatMatrix(

        rows,

        cols

    )

    st.write(

        "Ghế"

    )

    for r in range(rows):

        cols_ui = (

            st.columns(

                cols

            )
        )

        for c in range(cols):

            seat_id = (

                chr(65+r)

                +

                str(c+1)

            )

            with cols_ui[c]:

                st.button(

                    seat_id

                )

    seat_id = (

        st.text_input(

            "Chọn ghế"

        )
    )

    if st.button(

        "Thanh toán"

    ):

        booking.book_ticket(

            st.session_state

            ["user"]

            ["username"],

            movie

            ["movie_id"],

            seat_id,

            selected

            ["showtime_id"]

        )

        st.success(

            "Đặt thành công"

        )
