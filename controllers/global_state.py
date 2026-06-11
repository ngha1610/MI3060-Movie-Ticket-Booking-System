import streamlit as st
from models.file_io import FileIOHandler
from controllers.auth_controller import AuthController
from controllers.movie_controller import MovieController
from controllers.booking_controller import BookingController
from controllers.showtime_controller import ShowtimeController
from controllers.room_controller import RoomController
from controllers.admin_controller import AdminController

# Thêm decorator để khóa các controller vào RAM vĩnh viễn,
# tránh việc hệ thống bị khởi tạo lại từ đầu mỗi khi Streamlit rerun.
@st.cache_resource
def init_global_system():
    io_handler = FileIOHandler()
    
    auth_ctrl = AuthController(io_handler)
    
    movie_ctrl = MovieController(io_handler)
    
    showtime_ctrl = ShowtimeController(io_handler, movie_ctrl)
    
    room_ctrl = RoomController(io_handler)
    
    booking_ctrl = BookingController(io_handler, showtime_ctrl, movie_ctrl, room_ctrl)
    
    admin_ctrl = AdminController(movie_ctrl, booking_ctrl, showtime_ctrl, room_ctrl)
    
    return auth_ctrl, movie_ctrl, showtime_ctrl, room_ctrl, booking_ctrl, admin_ctrl
