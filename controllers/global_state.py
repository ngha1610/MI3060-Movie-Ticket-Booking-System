import streamlit as st
from data_structures.file_io import FileIOHandler
from controllers.auth_controller import AuthController
from controllers.movie_controller import MovieController
from controllers.booking_controller import BookingController
from controllers.showtime_controller import ShowtimeController
from controllers.room_controller import RoomController
from controllers.admin_controller import AdminController

# Khởi tạo Global Server State (Chạy 1 lần duy nhất cho toàn bộ web)
@st.cache_resource
def init_global_system():
    io_handler = FileIOHandler()
    auth_ctrl = AuthController(io_handler)
    movie_ctrl = MovieController(io_handler)
    showtime_ctrl = ShowtimeController(io_handler)
    room_ctrl = RoomController(io_handler)
    booking_ctrl = BookingController(io_handler, showtime_ctrl, movie_ctrl)
    admin_ctrl = AdminController(movie_ctrl, booking_ctrl)
    
    return auth_ctrl, movie_ctrl, showtime_ctrl, room_ctrl, booking_ctrl, admin_ctrl