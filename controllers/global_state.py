import streamlit as st
from data_structures.file_io import FileIOHandler
from controllers.auth_controller import AuthController
from controllers.movie_controller import MovieController
from controllers.booking_controller import BookingController
from controllers.showtime_controller import ShowtimeController
from controllers.room_controller import RoomController
from controllers.admin_controller import AdminController

# Dùng cache_resource để khóa các controller vào RAM vĩnh viễn
def init_global_system():
    print("=== BẮT ĐẦU KHỞI CHẠY HỆ THỐNG RIÊNG BIỆT ===")
    io_handler = FileIOHandler()
    
    print("1. Đang nạp bộ điều khiển tài khoản...")
    auth_ctrl = AuthController(io_handler)
    
    print("2. Đang nạp bộ điều khiển kho phim...")
    movie_ctrl = MovieController(io_handler)
    
    print("3. Đang nạp bộ điều khiển suất chiếu...")
    showtime_ctrl = ShowtimeController(io_handler)
    
    print("4. Đang nạp bộ điều khiển phòng chiếu...")
    room_ctrl = RoomController(io_handler)
    
    print("5. Đang nạp bộ điều khiển đặt vé (Chú ý chỗ này)...")
    booking_ctrl = BookingController(io_handler, showtime_ctrl, movie_ctrl, room_ctrl)
    
    print("6. Đang nạp bộ điều khiển quản trị viên...")
    admin_ctrl = AdminController(movie_ctrl, booking_ctrl)
    
    print("=== KHỞI TẠO TẤT CẢ CONTROLLER THÀNH CÔNG! ===")
    return auth_ctrl, movie_ctrl, showtime_ctrl, room_ctrl, booking_ctrl, admin_ctrl

# Ở file app.py, khi muốn dùng dữ liệu, cậu chỉ cần gọi:
# auth_ctrl, movie_ctrl, showtime_ctrl, room_ctrl, booking_ctrl, admin_ctrl = init_global_system()