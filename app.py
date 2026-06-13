# Import thư viện
import streamlit as st
import pandas as pd
import random
import streamlit.components.v1 as components
import time

# Import các thành phần của hệ thống
from models.entities import SeatStatus, MovieData
from models.file_io import FileIOHandler
from controllers.auth_controller import AuthController
from controllers.movie_controller import MovieController
from controllers.booking_controller import BookingController
from controllers.showtime_controller import ShowtimeController
from controllers.room_controller import RoomController
from controllers.admin_controller import AdminController

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN WEB
# ==========================================
# Thiết lập các thông số cơ bản cho trang web hiển thị trên trình duyệt
st.set_page_config(
    page_title="Sunnyx Cinema | Classic & Modern",
    page_icon="🌞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. KHỞI TẠO SESSION STATE
# ==========================================
# Session state dùng để lưu trạng thái tạm thời của người dùng
# Trong suốt quá trình sử dụng web, dữ liệu sẽ không bị mất sau mỗi lần streamlit rerun

# Trạng thái hiển thị quảng cáo
if 'ad_closed' not in st.session_state:
    st.session_state.ad_closed = False

# Trạng thái xác thực đã đăng nhập hay chưa
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False

# Phân quyền người dùng hiện tại
if 'user_role' not in st.session_state:
    st.session_state.user_role = 'guest'

# Tên đăng nhập
if 'username' not in st.session_state:
    st.session_state.username = ''

# Lữu trữ đối tượng UserData để truy xuất thông tin chi tiết
if 'user_obj' not in st.session_state:
    st.session_state.user_obj = None 

# Trạng thái bước thanh toán
if 'payment_step' not in st.session_state:
    st.session_state.payment_step = False

# Trang hiện tại
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

#Phim đang được chọn
if 'selected_movie' not in st.session_state:
    st.session_state.selected_movie = ''

# Mảng lưu trữ các ghế đang chọn
if 'selected_seats' not in st.session_state:
    st.session_state.selected_seats = []

# Mảng lưu trữ cấu hình danh sách phim trên bảng trượt
if 'config_slider' not in st.session_state:
    st.session_state.config_slider= []

# Mảng lữu trữ cấu hình danh sách phim hiển thị ở sảnh chính
if 'config_list' not in st.session_state:
    st.session_state.config_list = []

# ==========================================
# 3. KHỞI TẠO HỆ THỐNG
# ==========================================
# Chỉ nạp dữ liệu từ file CSV đúng 1 lần duy nhất khi mở ứng dụng.
# Các Controller sẽ được lưu vào Session State để tái sử dụng ở những lần Streamlit rerun tiếp theo.

if 'system_initialized' not in st.session_state:

    # Import hàm khởi tạo toàn bộ hệ thống
    # Hàm này sẽ tạo các Controller và nạp dữ liệu từ file CSV vào RAM
    from controllers.global_state import init_global_system

        # Khởi tạo các Bộ điều khiển (Controller) của hệ thống:
        # - AuthController: quản lý đăng nhập, đăng ký
        # - MovieController: quản lý phim
        # - ShowtimeController: quản lý suất chiếu
        # - RoomController: quản lý phòng chiếu
        # - BookingController: quản lý đặt vé
        # - AdminController: quản lý các chức năng dành cho quản trị viên
    (    
        auth_ctrl, 
        movie_ctrl, 
        showtime_ctrl, 
        room_ctrl, 
        booking_ctrl, 
        admin_ctrl
    ) = init_global_system()
     
    # Lưu toàn bộ vào Session State để lưu giữ trạng thái 
    st.session_state.auth_ctrl = auth_ctrl
    st.session_state.movie_ctrl = movie_ctrl
    st.session_state.showtime_ctrl = showtime_ctrl
    st.session_state.room_ctrl = room_ctrl
    st.session_state.booking_ctrl = booking_ctrl
    st.session_state.admin_ctrl = admin_ctrl

    # Đánh dấu hệ thống đã được khởi tạo
    # Những lần rerun tiếp theo sẽ bỏ qua khối lệnh này
    st.session_state.system_initialized = True

# Gọi lại các biến từ Session State ra để giao diện giao tiếp với hệ thống
auth_controller = st.session_state.auth_ctrl
movie_controller = st.session_state.movie_ctrl
showtime_controller = st.session_state.showtime_ctrl
room_controller = st.session_state.room_ctrl
booking_controller = st.session_state.booking_ctrl
admin_controller = st.session_state.admin_ctrl

# ==========================================
# 4. CHUYỂN TRANG & POPUP QUẢNG CÁO
# ==========================================
# Import hàm phụ trợ giao diện từ file bên ngoài
from ui_components import navigate_to, show_advertisement, create_premium_movie_card, show_popcorn_effect

# ==========================================
# 5. CSS DÀNH CHO GIAO DIỆN (VINTAGE STYLE)
# ==========================================
# Định dạng phông chữ, màu sắc, hiệu ứng thẻ phim và đồng bộ hóa kích thước ma trận ghế
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Courier+Prime:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Courier Prime', monospace; }
    h1, h2, h3, h4, h5, h6, .marquee-text, .hero-title, .movie-title { font-family: 'Playfair Display', serif !important; }
    .stApp { background-color: #F4EFE6; color: #3A2E2A; }
    header { background: transparent !important; }
    button[title="View sidebar"] { background-color: #5C161B !important; color: #D4AF37 !important; border: 2px solid #D4AF37 !important; border-radius: 5px !important; top: 15px; left: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.3); }
    button[title="View sidebar"] svg { fill: #D4AF37 !important; }
    .bg-decoration { position: fixed; z-index: 0; opacity: 0.05; pointer-events: none; animation: spin 30s linear infinite; }
    @keyframes spin { 100% { transform: rotate(360deg); } }
    .gear-1 { top: -50px; left: -50px; font-size: 250px; color: #5C161B; }
    .gear-2 { bottom: -80px; right: -50px; font-size: 300px; color: #D4AF37; }
    .gear-3 { top: 40%; left: -80px; font-size: 150px; color: #3A2E2A; animation: spin 20s linear infinite reverse;}
    .vintage-marquee { background-color: #2A080A; border: 4px dotted #D4AF37; padding: 20px 30px; text-align: center; margin-bottom: 30px; box-shadow: 0 10px 20px rgba(92, 22, 27, 0.4), inset 0 0 20px rgba(0,0,0,0.8); border-radius: 8px; position: relative; z-index: 10; }
    .marquee-text { font-size: 3rem; font-weight: 900; margin: 0; letter-spacing: 6px; color: #FFF2C8; text-shadow: 0 0 5px #D4AF37, 0 0 15px #D4AF37, 0 0 30px #E7A310; text-transform: uppercase; }
    .marquee-sub { color: #D4AF37; font-size: 1rem; letter-spacing: 3px; border-top: 1px solid #D4AF37; padding-top: 5px; margin-top: 5px; display: inline-block;}
    .vintage-ticket { background-color: #FDFBF7; border: 2px dashed #B89947; padding: 25px; border-radius: 12px; box-shadow: 5px 5px 15px rgba(0,0,0,0.08); position: relative; margin-bottom: 30px; z-index: 10; }
    .vintage-ticket::before, .vintage-ticket::after { content: ''; position: absolute; top: 50%; transform: translateY(-50%); width: 30px; height: 30px; background-color: #F4EFE6; border-radius: 50%; border: 2px dashed #B89947; }
    .vintage-ticket::before { left: -16px; border-left-color: transparent; border-top-color: transparent; border-bottom-color: transparent; transform: translateY(-50%) rotate(45deg);}
    .vintage-ticket::after { right: -16px; border-right-color: transparent; border-top-color: transparent; border-bottom-color: transparent; transform: translateY(-50%) rotate(-45deg);}
    .ticket-title { color: #5C161B; font-weight: 900; font-size: 1.5rem; text-transform: uppercase; text-align: center; border-bottom: 2px solid #5C161B; padding-bottom: 10px; margin-bottom: 20px;}
    .stSelectbox > div > div { background-color: #F4EFE6 !important; border: 1px solid #B89947 !important; border-radius: 4px; color: #3A2E2A !important; font-family: 'Courier Prime', monospace;}
    .stButton > button[kind="primary"] { background-color: #5C161B; color: #D4AF37 !important; font-family: 'Playfair Display', serif; font-weight: 800; font-size: 1.1rem; letter-spacing: 1px; border: 2px solid #D4AF37; transition: all 0.3s; padding: 10px 0; border-radius: 4px; box-shadow: 2px 2px 0px #D4AF37; }
    .stButton > button[kind="primary"]:hover { background-color: #731C22; transform: translate(2px, 2px); box-shadow: 0px 0px 0px #D4AF37; }
    .stButton > button[kind="secondary"] { background-color: #E8DCC4; color: #5C161B !important; font-family: 'Playfair Display', serif; font-weight: 700; border: 1px solid #B89947; transition: all 0.2s; border-radius: 4px; }
    .stButton > button[kind="secondary"]:hover { background-color: #D4AF37; color: white !important;}
    .movie-card-container > div > div > div[data-testid="stVerticalBlock"] { background: #FDFBF7 !important; padding: 0 !important; border-radius: 8px; border: 1px solid #D4AF37; box-shadow: 3px 3px 10px rgba(0,0,0,0.1); transition: transform 0.3s; height: 100%; margin-bottom: 20px; z-index: 10; position: relative; }
    .movie-card-container > div > div > div[data-testid="stVerticalBlock"]:hover { transform: translateY(-5px); box-shadow: 5px 5px 15px rgba(92,22,27,0.3); border-color: #5C161B;}
    .img-wrapper { width: 100%; aspect-ratio: 2 / 3; overflow: hidden; border-bottom: 2px solid #D4AF37; padding: 5px; background: #FFF;}
    .img-wrapper img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.5s; border-radius: 4px;}
    .movie-card-container > div > div > div[data-testid="stVerticalBlock"]:hover .img-wrapper img { transform: scale(1.05); }
    .content-container { padding: 15px; text-align: center; }
    .movie-title { font-size: 1.1rem !important; font-weight: 900 !important; color: #5C161B !important; text-transform: uppercase; margin-bottom: 10px !important; line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 2.8rem;}
    .movie-info-text { font-size: 0.85rem; color: #555; margin: 0 0 5px 0; border-bottom: 1px dotted #CCC; padding-bottom: 5px;}
    .seat-screen { background: #5C161B; text-align: center; color: #D4AF37; font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 900; padding: 10px; border-radius: 4px; margin-bottom: 30px; letter-spacing: 8px; border: 2px double #D4AF37; box-shadow: inset 0 0 10px rgba(0,0,0,0.5);}
    
    /* Ép tất cả các nút (cả trống, đang chọn, và đã bán) chung 1 form kích thước */
    .stButton > button {
        padding: 0px !important;
        min-height: 38px !important;
        border-radius: 4px;
        transition: all 0.2s ease-in-out;
    }
    
    /* Xuyên thủng vào lớp thẻ <p> bên trong nút để chữ không bị tràn */
    .stButton > button p {
        white-space: nowrap !important;
        word-break: keep-all !important;
        font-size: 0.75rem !important; 
        letter-spacing: -0.5px !important; 
        margin: 0 !important;
    }   

    /* 1. GHẾ TRỐNG */
    .stButton > button[kind="secondary"] {
        background-color: #E8DCC4; 
        color: #5C161B !important; 
        border: 1px solid #B89947;
    }

    /* 2. GHẾ ĐANG CHỌN */
    .stButton > button[kind="primary"] {
        background-color: #5C161B !important; 
        color: #D4AF37 !important; 
        border: 2px solid #D4AF37 !important;
        box-shadow: none !important; 
        transform: none !important;
    }

    /* 3. GHẾ ĐÃ BÁN - Chuyển sang màu Xám*/
    .stButton > button:disabled {
        background-color: #9E9E9E !important; 
        color: #E0E0E0 !important; 
        border: 1px solid #757575 !important; 
        cursor: not-allowed !important; 
        opacity: 0.8 !important;
    } 

</style>
""", unsafe_allow_html=True)

# Các họa tiết trang trí nền
st.markdown('<div class="bg-decoration gear-1">⚙</div><div class="bg-decoration gear-2">⚙</div><div class="bg-decoration gear-3">⚙</div>', unsafe_allow_html=True)

# ==========================================
# 6. QUẢN LÝ PHIÊN HOẠT ĐỘNG (ĐĂNG NHẬP / ĐĂNG KÝ)
# ==========================================
# Thanh Sidebar dùng để người dùng tương tác, xác thực và điều hướng
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #5C161B; font-family: \"Playfair Display\", serif;'>PHÒNG VÉ</h2>", unsafe_allow_html=True)
    
    if not st.session_state.is_logged_in:
        st.info("Vui lòng Đăng nhập")
        tab_login, tab_register = st.tabs(["Đăng nhập", "Đăng Ký"])
        
        # Đăng nhập
        with tab_login:
            with st.form("login_form"):
                st.markdown("<small>*(Gợi ý: Tài khoản `admin` - Pass `123`)*</small>", unsafe_allow_html=True)
                username_input = st.text_input("Tên người dùng (Username)")
                password_input = st.text_input("Mật khẩu (Password)", type="password")
                submitted = st.form_submit_button("XÁC NHẬN", type="primary")
                
                if submitted:
                    if username_input == "" or password_input == "": 
                        st.error("Thiếu thông tin!")
                    else:
                        # Giao tiếp với AuthController để tìm kiếm dữ liệu quả bảng băm
                        role = auth_controller.login(username_input, password_input)
                        if role != "FAILED":
                            st.session_state.is_logged_in = True
                            st.session_state.username = username_input
                            st.session_state.user_obj = auth_controller.get_current_user() # Load User Data object
                            
                            # Điều hướng theo phân quyền
                            if role == "ADMIN":
                                st.session_state.user_role = "admin"
                                st.session_state.current_page = "admin_dash"
                            else:
                                st.session_state.user_role = "customer"
                                st.session_state.current_page = "home"
                            st.rerun()
                        else:
                            st.error("Thông tin không chính xác!")
        # Đăng ký
        with tab_register:
            with st.form("register_form"):
                st.markdown("<small>*(Lưu ý: Mật khẩu phải chứa ít nhất 6 ký tự)*</small>", unsafe_allow_html=True)
                new_username = st.text_input("Tên người dùng mới")
                new_password = st.text_input("Mật khẩu", type="password")
                confirm_password = st.text_input("Xác nhận mật khẩu", type="password")
                reg_submitted = st.form_submit_button("ĐĂNG KÝ", type="primary")
                if reg_submitted:
                    success = auth_controller.register(new_username, new_password, confirm_password)
                    if success:
                        st.success("Đăng ký thành công! Sang tab Đăng Nhập để vào.")
                    else:
                        st.error("Lỗi đăng ký! Tên người dùng đã tồn tại hoặc mật khẩu chưa đạt.")
    else:
        # Giao diện khi đã đăng nhập
        st.success(f"Kính chào quý khách **{st.session_state.username}**.")
        st.caption(f"Hạng: {st.session_state.user_role.upper()}")
        
        if st.session_state.user_role == 'customer':
            if st.button("Sảnh Chính", use_container_width=True):
                st.session_state.selected_seats = [] # RESET GHẾ
                navigate_to("home")
            if st.button("Vé Của Tôi", use_container_width=True): navigate_to("history")
            st.divider()
        
        if st.button("ĐĂNG XUẤT", use_container_width=True):
            auth_controller.logout()
            st.session_state.is_logged_in = False
            st.session_state.user_role = 'guest'
            st.session_state.username = ''
            st.session_state.user_obj = None
            st.session_state.current_page = 'home'
            st.session_state.selected_seats = []
            st.rerun()

# ==========================================
# 7. KHUNG GIAO DIỆN CHÍNH
# ==========================================
st.markdown("""
<div class="vintage-marquee">
    <div class="marquee-text">SUNNYX CINEMA</div>
    <div class="marquee-sub">EST. 1926 • CLASSIC VINTAGE CINEMA</div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------
# A. GIAO DIỆN QUẢN TRỊ VIÊN
# ------------------------------------------
if st.session_state.user_role == 'admin' and st.session_state.get('current_page') != 'booking':
    st.markdown("<h2 style='color:#5C161B;'>PHÒNG ĐIỀU HÀNH KỸ THUẬT</h2>", unsafe_allow_html=True)
    st.info("Khu vực dành riêng cho Quản lý (Admin).")
    
    # Bảng điều khiển
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tổng Doanh thu", f"{admin_controller.calculate_revenue():,.0f} đ")
    c2.metric("Vé xuất ra", f"{admin_controller.count_tickets()} vé")
    c3.metric("Phim trình chiếu", f"{admin_controller.count_movies()} cuộn")

    # Áp dụng thuật toán tìm kiếm/duyệt tuần tự để đếm Node
    all_users = auth_controller.get_all_users()
    total_users = 0
    for u in all_users:
        total_users +=1

    c4.metric("Thành viên hệ thống", f"{total_users} người")
    st.divider()
    
    # Các Tab chức năng của Admin
    tab_manage, tab_showtime,tab_room, tab_display, tab_top, tab_offline, tab_tickets = st.tabs([
        "Quản Lý Phim", "Quản Lý Suất Chiếu", "Quản Lý Phòng", "Cấu Hình Giao Diện", "Top Doanh Thu", "Bán Vé Tại Quầy", "Quản Lý Vé"])
    
    # ==========================================
    # TAB 1: QUẢN LÝ KHO PHIM (THÊM / SỬA / XÓA)
    # ==========================================
    with tab_manage:
        manage_action = st.radio("Chọn thao tác:", ["Thêm Phim Mới", "Cập Nhật Phim", "Xóa Phim"], horizontal=True)
        st.write("---")
        
        # Load danh sách phim hiện tại
        all_movies = movie_controller.get_movie_data()

        # Tạo mảng tên phim
        movie_titles = []
        if all_movies:
            for m in all_movies:
                movie_titles += [m.get_title()]
        
        # --- THÊM PHIM ---
        if manage_action == "Thêm Phim Mới":
            with st.form("add_movie_form"):
                st.subheader("Thêm Tác Phẩm Mới")
                new_title = st.text_input("Tên phim (*)")
                new_genre = st.text_input("Thể loại (*)")
                
                col1, col2 = st.columns(2)
                new_duration = col1.number_input("Thời lượng (phút)", min_value=1, value=120)
                new_price_text = col2.text_input(
                    "Giá vé cơ bản (VNĐ)",
                    value="85000"
                )
                
                new_poster = st.text_input("Link ảnh Poster (URL)")
                new_desc = st.text_area("Mô tả tóm tắt nội dung")
                
                if st.form_submit_button("THÊM VÀO KHO", type="primary"):
                    if not new_title.strip() or not new_genre.strip():
                        st.error("Vui lòng điền đầy đủ Tên phim và Thể loại!")
                    else:
                        try:
                            new_price = int(new_price_text)

                            if not (1000 <= new_price <= 10000000):
                                st.error(
                                    "Giá vé không hợp lệ! Phải nằm trong khoảng 1,000 - 10,000,000 VNĐ."
                                )

                            else:
                                new_id = movie_controller.generate_movie_id()
                                price_int = int(new_price_text)
                                new_movie = MovieData(
                                    movie_id=new_id,
                                    title=new_title,
                                    genre=new_genre,
                                    duration=new_duration,
                                    description=new_desc,
                                    base_price=price_int,
                                    poster_path=new_poster
                                )
                        

                                try:
                                    # Chèn Node mới vào danh sách liên kết
                                    if movie_controller.add_movie(new_movie):
                                        st.toast(f"Đã thêm phim '{new_title}' thành công!")
                                        st.success(f"Thêm phim '{new_title}' thành công! Hệ thống đang tải lại...")
                                        time.sleep(1) 
                                        st.rerun()
                                    else:
                                        st.error("Lỗi hệ thống khi lưu phim!")
                                except ValueError as e:
                                    # Bắt đúng lỗi "Tên phim này đã tồn tại trong hệ thống!" từ MovieController ném lên
                                    st.error(f"Lỗi: {e}")
                        except ValueError:
                            st.error(
                                "Giá vé phải là số nguyên từ 1 đến 10.000.000 VNĐ."
                            )  

        # --- CẬP NHẬT PHIM ---
        elif manage_action == "Cập Nhật Phim":
            if not all_movies:
                st.warning("Kho rỗng. Chưa có phim nào để cập nhật.")
            else:
                selected_movie_title = st.selectbox("Chọn phim cần sửa:", movie_titles)
                selected_movie = None
                for m in all_movies:
                    if m.get_title() == selected_movie_title:
                        selected_movie = m
                        break

                
                if selected_movie:
                    with st.form("update_movie_form"):
                        st.subheader(f"Chỉnh sửa: {selected_movie_title}")
                        upd_title = st.text_input("Tên phim", value=selected_movie.get_title())
                        upd_genre = st.text_input("Thể loại", value=selected_movie.get_genre())
                        
                        col1, col2 = st.columns(2)
                        upd_duration = col1.number_input("Thời lượng (phút)", min_value=1, value=selected_movie.get_duration())
                        current_price = max(1, min(int(selected_movie.get_base_price()), 10_000_000))

                        upd_price_text = col2.text_input(
                            "Giá vé (VNĐ)",
                            value=str(current_price)
                        )
                        
                        upd_poster = st.text_input("Link ảnh Poster", value=selected_movie.get_poster_path())
                        upd_desc = st.text_area("Mô tả", value=selected_movie.get_description())
                        
                        if st.form_submit_button("LƯU THAY ĐỔI", type="primary"):

                            # BƯỚC 1: Xử lý riêng việc chuyển đổi giá — nguồn ValueError thứ nhất
                            try:
                                upd_price = int(upd_price_text)
                            except ValueError:
                                st.error("Giá vé phải là số nguyên hợp lệ.")
                                upd_price = None

                            # BƯỚC 2: Chỉ tiếp tục nếu giá hợp lệ
                            if upd_price is not None:
                                if not (1000 <= upd_price <= 10_000_000):
                                    st.error("Giá vé không hợp lệ! Phải nằm trong khoảng 1,000 - 10,000,000 VNĐ.")
                                else:
                                    # BƯỚC 3: Xử lý riêng lỗi từ controller — nguồn ValueError thứ hai
                                    try:
                                        if movie_controller.update_movie(
                                            movie_id=selected_movie.get_movie_id(),
                                            title=upd_title,
                                            genre=upd_genre,
                                            duration=upd_duration,
                                            description=upd_desc,
                                            base_price=upd_price,
                                            poster_path=upd_poster
                                        ):
                                            st.toast("Đã cập nhật thông tin phim!")
                                            st.success("Bản ghi đã được cập nhật thành công! Đang tải lại...")
                                            time.sleep(1)
                                            st.rerun()
                                        else:
                                            st.error("Có lỗi xảy ra khi lưu.")
                                    except ValueError as e:
                                        # Bây giờ chỉ bắt đúng lỗi từ controller, hiển thị đúng nội dung
                                        st.error(f"Lỗi: {e}")

                                                    

        # --- XÓA PHIM ---
        elif manage_action == "Xóa Phim":
            if not all_movies:
                st.warning("Kho rỗng. Không có phim để xóa.")
            else:
                del_movie_title = st.selectbox("Chọn phim muốn xoá:", movie_titles)
                
                # Dò tìm Object phim thủ công
                del_movie = None
                for m in all_movies:
                    if m.get_title() == del_movie_title:
                        del_movie = m
                        break
                
                if del_movie:
                    st.error(f"Cảnh báo: Bạn sắp xóa cuộn phim **{del_movie_title}**. Thao tác này không thể hoàn tác.")
                    if st.button("XÁC NHẬN XÓA", type="primary"):
                        if admin_controller.admin_delete_movie(del_movie.get_movie_id()):
                            st.toast("Đã xóa phim khỏi hệ thống!")
                            st.warning(f"Đã dọn dẹp '{del_movie_title}' khỏi kho! Đang làm mới danh sách...")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Không thể xóa! Phim này đang có suất chiếu hoạt động hoặc khách đã mua vé.")

    # ==========================================
    # TAB 2: QUẢN LÝ SUẤT CHIẾU (THÊM / XÓA)
    # ==========================================
    with tab_showtime:
        st_action = st.radio("Chọn thao tác:", ["Thêm Suất Chiếu Mới", "Xóa Suất Chiếu"], horizontal=True, key="st_action_radio")
        st.write("---")

        all_movies = movie_controller.get_movie_data()
        all_showtimes = showtime_controller.get_showtime_data()

        # --- THÊM SUẤT CHIẾU ---
        if st_action == "Thêm Suất Chiếu Mới":
            if not all_movies:
                st.warning("Kho rỗng. Vui lòng vào Tab 'Quản Lý Phim' để thêm phim trước khi tạo suất chiếu.")
            else:
                movie_titles = ["-- Chọn phim --"]
                for m in all_movies:
                    movie_titles += [m.get_title()]

                with st.form("add_showtime_form"):
                    st.subheader("Lên Lịch Chiếu Mới")
                    sel_movie_title = st.selectbox("1. Chọn Tác Phẩm", movie_titles)

                    # --- GỌI ROOM CONTROLLER ĐỂ LẤY DANH SÁCH PHÒNG THỰC TẾ ---
                    all_rooms = room_controller.get_room_data()
                    room_options = []
                    if all_rooms:
                        for r in all_rooms:
                            room_options += [r.get_room_id() + " - " + r.get_room_name()]
                    else:
                        room_options += ["Chưa có phòng"]

                    c1, c2 = st.columns(2)
                    with c1:
                        new_date = st.text_input("2. Ngày chiếu (YYYY-MM-DD)", placeholder="VD: 2026-06-01")
                        selected_room_str = st.selectbox("4. Chọn Phòng Chiếu", room_options)
                    with c2:
                        new_time = st.text_input("3. Giờ chiếu (HH:MM)", placeholder="VD: 19:30")

                    if st.form_submit_button("TẠO SUẤT CHIẾU", type="primary"):
                        if sel_movie_title == "-- Chọn phim --":
                            st.error("Vui lòng chọn phim!")
                        elif not new_date.strip() or not new_time.strip():
                            st.error("Vui lòng nhập đầy đủ ngày và giờ chiếu!")
                        else:
                            # Tìm kiếm phim qua Controller
                            movie_node = movie_controller.search_by_title(sel_movie_title)
                            selected_movie_id = movie_node.get_data().get_movie_id() if movie_node else None

                            # Tách ID và tìm phòng chiếu qua Controller
                            room_id_extracted = selected_room_str.split(" - ")[0]
                            room_node = room_controller.find_room(room_id_extracted)

                            if room_node and selected_movie_id:
                                room = room_node.get_data()
                                # Nối chuỗi ngày giờ
                                start_time_str = f"{new_date.strip()} {new_time.strip()}"
                                # Tạo ID suất chiếu mới tự động
                                new_st_id = showtime_controller.generate_showtime_id()

                                # Khởi tạo đối tượng Showtime
                                from models.entities import Showtime
                                new_showtime = Showtime(
                                    showtime_id=new_st_id,
                                    movie_id=selected_movie_id,
                                    start_time=start_time_str,
                                    room_id=room.get_room_id(), 
                                    room_rows=room.get_rows(),   
                                    room_cols=room.get_cols()
                                )

                                # Cập nhật vào danh sách liên kết (Đã bao gồm thuật toán kiểm tra trùng thời gian)
                                if showtime_controller.add_showtime(new_showtime):
                                    st.toast("Đã lên lịch chiếu thành công!")
                                    st.success("Thêm suất chiếu mới thành công! Hệ thống đang tải lại...")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Lỗi: Khung giờ bị trùng hoặc sai định dạng ngày giờ (YYYY-MM-DD HH:MM). Vui lòng kiểm tra lại!")
                            else:
                                st.error("Không tìm thấy phòng chiếu hoặc phim. Vui lòng kiểm tra lại!")
        # --- XÓA SUẤT CHIẾU ---
        elif st_action == "Xóa Suất Chiếu":
            if not all_showtimes:
                st.warning("Hiện chưa có suất chiếu nào trên hệ thống.")
            else:
                st_options = ["-- Chọn suất chiếu cần xóa --"]
                st_mapping_list = [] # Sử dụng mảng cặp thay thế cho Dictionary

                # Dùng vòng lặp dò thông tin chi tiết từng suất chiếu để Admin dễ chọn
                for st_obj in all_showtimes:
                    m_node = movie_controller.search_by_id(st_obj.get_movie_id())
                    m_title = m_node.get_data().get_title() if m_node else "Phim không xác định"

                    st_date = showtime_controller.extract_date(st_obj)
                    st_time = showtime_controller.extract_time(st_obj)
                    
                    # Tạo nhãn hiển thị cho Dropdown
                    display_str = f"{m_title} | {st_date} - {st_time} | Phòng: {st_obj.get_room_id()}"
                    
                    st_options = st_options + [display_str]
                    st_mapping_list = st_mapping_list + [[display_str, st_obj.get_showtime_id()]]

                with st.form("del_showtime_form"):
                    st.subheader("Dọn Dẹp Lịch Chiếu")
                    sel_st_str = st.selectbox("Danh sách các suất chiếu hiện tại:", st_options)

                    st.error("Lưu ý: Chỉ có thể xóa suất chiếu khi chưa có khách hàng nào đặt vé!")
                    if st.form_submit_button("XÓA SUẤT CHIẾU NÀY", type="primary"):
                        if sel_st_str == "-- Chọn suất chiếu cần xóa --":
                            st.warning("Vui lòng chọn suất chiếu hợp lệ!")
                        else:
                            # Thuật toán tìm kiếm tuần tự thủ công để lấy ra ID suất chiếu
                            target_st_id = None
                            for pair in st_mapping_list:
                                if pair[0] == sel_st_str:
                                    target_st_id = pair[1]
                                    break
                            
                            if showtime_controller.delete_showtime(target_st_id, booking_controller):
                                st.toast("Đã hủy suất chiếu thành công!")
                                st.warning("Đã dọn dẹp thành công suất chiếu! Đang làm mới...")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Lỗi: Không thể xóa! Suất chiếu này đã có khách hàng mua vé.")
    
        # ==========================================
        # TAB 3: QUẢN LÝ PHÒNG CHIẾU (CRUD)
        # ==========================================
        with tab_room:
            room_action = st.radio("Chọn thao tác hạ tầng:", ["Thêm Phòng Mới", "Cập Nhật Tên Phòng", "Xóa Phòng Chiếu"], horizontal=True)
            st.write("---")
            
            # Tải danh sách phòng thực tế từ cơ sở dữ liệu
            all_rooms = room_controller.get_room_data()
            
            # --- 1. THÊM PHÒNG CHIẾU MỚI ---
            if room_action == "Thêm Phòng Mới":
                with st.form("add_room_form"):
                    st.subheader("Xây Dựng Phòng Chiếu Mới")
                    r_id = st.text_input("Mã phòng chiếu (*)", placeholder="VD: R05")
                    r_name = st.text_input("Tên định danh phòng (*)", placeholder="VD: Phòng Chiếu 5")
                    
                    c1, c2 = st.columns(2)
                    r_rows = c1.number_input("Cấu hình số Hàng ghế", min_value=1, value=10, step=1)
                    r_cols = c2.number_input("Cấu hình số Cột ghế", min_value=1, value=12, step=1)
                    
                    st.caption("Sức chứa mặc định của phòng sẽ tự động tính toán bằng: Hàng x Cột")
                    
                    if st.form_submit_button("KHỞI TẠO PHÒNG CHIẾU", type="primary"):
                        if not r_id.strip() or not r_name.strip():
                            st.error("Vui lòng điền đầy đủ Mã phòng và Tên phòng chiếu!")
                        else:
                            from models.entities import Room
                            # Khởi tạo đối tượng Room theo đúng thực thể mẫu
                            new_room_obj = Room(
                                room_id=r_id.strip(),
                                room_name=r_name.strip(),
                                rows=int(r_rows),
                                cols=int(r_cols)
                            )
                            
                            if room_controller.add_room(new_room_obj):
                                st.toast("Khởi tạo phòng chiếu thành công!")
                                st.success(f"Đã thêm '{r_name}' vào hệ thống! Đang đồng bộ hóa dữ liệu...")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Khởi tạo thất bại: Mã phòng hoặc Tên phòng chiếu này đã tồn tại trên hệ thống!")

            # --- 2. CẬP NHẬT TÊN PHÒNG CHIẾU ---
            elif room_action == "Cập Nhật Tên Phòng":
                if not all_rooms:
                    st.warning("Rạp đang trống. Chưa có phòng chiếu nào để chỉnh sửa.")
                else:
                    # Tạo danh sách lựa chọn cho dropdown
                    room_options = []
                    for r in all_rooms:
                        room_options += [f"{r.get_room_id()} - {r.get_room_name()}"]
                        
                    selected_room_str = st.selectbox("Chọn phòng chiếu cần thay đổi:", room_options)
                    room_id_extracted = selected_room_str.split(" - ")[0]
                    
                    with st.form("update_room_form"):
                        st.subheader("Chỉnh Sửa Định Danh Phòng")
                        new_room_name = st.text_input("Nhập tên mới cho phòng chiếu:")
                        
                        if st.form_submit_button("LƯU THAY ĐỔI", type="primary"):
                            if not new_room_name.strip():
                                st.error("Tên phòng chiếu mới không được để trống!")
                            else:
                                if room_controller.update_room (room_id_extracted, new_room_name.strip()):
                                    st.toast("Đã cập nhật tên phòng chiếu!")
                                    st.success("Thay đổi thông tin phòng thành công! Đang tải lại dữ liệu...")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Cập nhật thất bại: Tên phòng mới bị trùng với một phòng chiếu khác đang hoạt động!")

            # --- 3. XÓA PHÒNG CHIẾU KHỎI HỆ THỐNG ---
            elif room_action == "Xóa Phòng Chiếu":
                if not all_rooms:
                    st.warning("Rạp đang trống. Không có phòng để xóa.")
                else:
                    room_options = []
                    for r in all_rooms:
                        room_options += [f"{r.get_room_id()} - {r.get_room_name()}"]
                        
                    selected_del_str = st.selectbox("Chọn phòng chiếu muốn xóa:", room_options)
                    extracted_del_id = selected_del_str.split(" - ")[0]
                    
                    st.error(f"Cảnh báo: Bạn chuẩn bị dỡ bỏ phòng `{selected_del_str}`. Thao tác xóa không thể phục hồi.")
                    st.caption("Hệ thống sẽ từ chối xóa nếu phòng chiếu này đang có lịch trình suất chiếu vận hành.")
                    
                    if st.button("XÁC NHẬN GỠ BỎ PHÒNG", type="primary"):
                        if admin_controller.admin_delete_room(extracted_del_id):
                            st.toast("Đã dọn dẹp phòng chiếu thành công!")
                            st.warning("Đã gỡ bỏ phòng chiếu! Hệ thống đang làm mới...")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Hành động bị từ chối: Không thể xóa phòng này vì đang có các suất chiếu hoạt động gắn liền với nó!")
    
    # ==========================================
    # TAB 4: TÙY CHỈNH GIAO DIỆN (UI CONFIG)
    # ==========================================
    with tab_display:
        st.subheader("Cấu Hình Phim Hiển Thị Ở Sảnh Chính")
        st.info("Tùy chọn những cuộn phim nào sẽ được phô diễn ra ngoài giao diện khách hàng.")
        
        all_movies = movie_controller.get_movie_data()

        all_titles = []
        if all_movies:
            for m in all_movies:
                all_titles += [m.get_title()]
        
        with st.form("display_config_form"):
            new_slider = st.multiselect("Chọn phim chạy trên Bảng Trượt (Tối đa 3):", options=all_titles, default=st.session_state.config_slider if st.session_state.config_slider else all_titles[:3])
            new_list = st.multiselect("Chọn phim xuất hiện ở Danh sách Tác Phẩm (Tối đa 8):", options=all_titles, default=st.session_state.config_list if st.session_state.config_list else all_titles[:8])
            
            if st.form_submit_button("LƯU CẤU HÌNH HIỂN THỊ", type="primary"):
                if len(new_slider) > 3:
                    st.error("Bảng trượt chỉ chứa được tối đa 3 tác phẩm!")
                elif len(new_list) > 8:
                    st.error("Danh sách bên dưới chỉ chứa được tối đa 8 tác phẩm!")
                else:
                    st.session_state.config_slider = new_slider
                    st.session_state.config_list = new_list

                    # Ghi dữ liệu
                    try:
                        movie_controller.save_ui_config(new_slider, new_list)
                        st.success("Đã lưu cấu hình! Bạn có thể về Sảnh Chính để xem thay đổi. ")
                    except Exception as e:
                        st.error(f"Lỗi ghi cấu hình: {e}")

    # ==========================================
    # TAB 5: THỐNG KÊ DOANH THU
    # ==========================================
    with tab_top: 
        # Controller thực thi thuật toán sắp xếp nổi bọt (Bubble Sort) trên cấu trúc Linked List
        top_movies = admin_controller.get_top_movies_by_revenue()

        if top_movies:
            for m in top_movies:
                st.markdown(f"**{m.get_title()}** | Sinh lời: <span style='color:#5C161B; font-weight:bold;'>{m.get_revenue():,.0f} đ</span>", unsafe_allow_html=True)
                st.caption(f"Thể loại: {m.get_genre()} | Thời lượng: {m.get_duration()} phút")
                st.divider()
        else:
            st.write("Chưa có dữ liệu phim.")

    # ==========================================
    # TAB 6: BÁN VÉ TẠI QUẦY (OFFLINE MODE)
    # ==========================================
    with tab_offline:
        st.subheader("QUẦY BÁN VÉ TRỰC TIẾP (OFFLINE)")
        st.info("Nhân viên xuất vé cho khách mua trực tiếp tại rạp. ")
        
        
        all_movies = movie_controller.get_movie_data()
        all_showtimes = showtime_controller.get_showtime_data()

        # Phân nhánh luồng tìm kiếm theo trải nghiệm người dùng 
        booking_mode = st.radio(
            "Bạn muốn tìm lịch chiếu theo cách nào?", 
            ["Chọn Phim trước", "Chọn Ngày trước"], 
            horizontal=True,
            key="admin_mode_radio"
        )

        qb1, qb2, qb3, qb4 = st.columns([2, 1, 1, 1])
        selected_fast_movie = None 

        # --- LUỒNG TÌM KIẾM 1: LỌC THEO TÁC PHẨM ---
        if booking_mode == "Chọn Phim trước":
            with qb1:
                # 1. Tạo mảng tên phim thủ công
                movie_titles = ["-- Chọn phim --"]
                if all_movies:
                    for m in all_movies:
                        movie_titles += [m.get_title()]
                else:
                    movie_titles = ["Hiện chưa có phim"]
                    
                selected_title = st.selectbox("1. Chọn Cuộn Phim", movie_titles, key="admin_luong1_movie_sel")
                
            if selected_title not in ["-- Chọn phim --", "Hiện chưa có phim"]:
                selected_fast_movie = selected_title
                
                # Truy vấn dữ liệu qua bộ điều khiển (Sử dụng Tìm kiếm tuần tự)
                movie_node = movie_controller.search_by_title(selected_title)
                if movie_node:
                    selected_movie_id = movie_node.get_data().get_movie_id()
                    movie_shows = showtime_controller.get_showtimes_by_movie(selected_movie_id)
                else:
                    movie_shows = []
                        
                available_dates = showtime_controller.get_unique_sorted_dates(movie_shows)
                
                with qb2:
                    selected_date = st.selectbox("2. Ngày Chiếu", ["-- Chọn ngày --"] + available_dates if available_dates else ["Chưa có lịch"], key="luong1_date_sel")
                    
                if selected_date not in ["-- Chọn ngày --", "Chưa có lịch"]:
                    # Lọc danh sách giờ dựa trên ngày
                    # Khởi tạo mảng rỗng và dùng vòng lặp for duyệt tuần tự
                    date_shows = []
                    for s in movie_shows:
                        if showtime_controller.extract_date(s) == selected_date:
                            date_shows += [s]
                    available_times = showtime_controller.get_unique_sorted_times(date_shows)
                    
                    with qb3:
                        selected_time = st.selectbox("3. Khung Giờ", ["-- Chọn giờ --"] + available_times if available_times else ["Chưa có giờ"], key="luong1_time_sel")
                else:
                    with qb3:
                        st.selectbox("3. Khung Giờ", ["-- Chọn giờ --"], key="luong1_time_empty")
            else:
                with qb2:
                    st.selectbox("2. Ngày Chiếu", ["-- Chọn ngày --"], key="luong1_date_empty")
                with qb3:
                    st.selectbox("3. Khung Giờ", ["-- Chọn giờ --"], key="luong1_time_empty2")

        # --- LUỒNG TÌM KIẾM 2: LỌC THEO THỜI GIAN ---
        else: 
            with qb1:
                all_dates = showtime_controller.get_unique_sorted_dates(all_showtimes)
                selected_date = st.selectbox("1. Ngày Chiếu", ["-- Chọn ngày --"] + all_dates if all_dates else ["Chưa có lịch"], key="admin_date_sel_2")
                
            if selected_date != "-- Chọn ngày --" and selected_date != "Chưa có lịch":
                
                daily_schedule = showtime_controller.get_schedule_by_date(selected_date)
                
                # Lọc lấy danh sách tên phim 
                movie_titles = []
                for group in daily_schedule:
                    movie_titles += [group[0].get_title()]
                
                with qb2:
                    selected_title = st.selectbox("2. Chọn Cuộn Phim", ["-- Chọn phim --"] + movie_titles if movie_titles else ["Không có phim"], key="admin_movie_sel_2")
                    
                if selected_title != "-- Chọn phim --" and selected_title != "Không có phim":
                    selected_fast_movie = selected_title 
                    
                    # Dò tìm lại Gói dữ liệu bằng vòng lặp for (Không dùng hàm next() của Python)
                    selected_group = None
                    for g in daily_schedule:
                        if g[0].get_title() == selected_title:
                            selected_group = g
                            break
                    
                    if selected_group:
                        # Móc danh sách các suất chiếu từ trong Gói đó ra và lấy Giờ
                        available_times = showtime_controller.get_unique_sorted_times(selected_group[1])
                        with qb3:
                            selected_time = st.selectbox("3. Khung Giờ", ["-- Chọn giờ --"] + available_times if available_times else ["Chưa có giờ"], key="admin_time_sel_2")
                else:
                    with qb3:
                        st.selectbox("3. Khung Giờ", ["-- Chọn giờ --"], key="admin_time_sel_2_empty")
            else:
                with qb2:
                    st.selectbox("2. Chọn Cuộn Phim", ["-- Chọn phim --"], key="admin_movie_sel_2_empty")
                with qb3:
                    st.selectbox("3. Khung Giờ", ["-- Chọn giờ --"], key="admin_time_sel_2_empty2")
        
        # --- TIẾN HÀNH CHỐT SUẤT CHIẾU & ĐẶT GHẾ ---
        st.markdown("---")
        st.subheader("TIẾN HÀNH CHỌN GHẾ và IN VÉ")
        
        # Khởi tạo biến và dùng Tìm kiếm tuần tự để tìm phim
        movie_obj = None
        if all_movies:
            for m in all_movies:
                if m.get_title() == selected_fast_movie:
                    movie_obj = m
                    break
        
        showtime_obj = None
        if movie_obj and selected_date not in ["-- Chọn ngày --", "Chưa có lịch", None] and selected_time not in ["-- Chọn giờ --", "Chưa có giờ", None]:
            showtime_obj = showtime_controller.find_exact_showtime(
                movie_obj.get_movie_id(),
                selected_date,
                selected_time
            )

        # Nếu đã chọn xong Phim + Ngày + Giờ thì mới mở khóa bảng chọn ghế
        if movie_obj and showtime_obj:
            c_row, c_col, c_btn = st.columns([1, 1, 2])
            
            with c_row:
                # Ô nhập Hàng ghế
                seat_row = st.number_input("Hàng ghế", min_value=0, step=1, key="admin_seat_row")
                
            with c_col:
                # Ô nhập Số ghế
                seat_col = st.number_input("Số ghế", min_value=0, step=1, key="admin_seat_col")
                
            with c_btn:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                
                # Nút bấm in vé sẽ gọi trực tiếp xuống admin_controller của cậu
                if st.button("XUẤT VÉ CHO KHÁCH", type="primary", use_container_width=True, key="admin_btn_issue_ticket"):
                    
                    ticket_id = admin_controller.sell_ticket_at_counter(
                        movie=movie_obj,
                        showtime=showtime_obj,
                        row=seat_row,
                        col=seat_col
                    )
                    
                    if ticket_id:
                        # Lôi hàm in vé từ backend ra xài để không phí code
                        ticket_info = booking_controller.generate_ticket_info(ticket_id)
                        st.success("Giao dịch thành công!")
                        st.info(f"ĐÃ IN VÉ:\n{ticket_info}")

                        st.session_state.admin_selected_seats = []
                    else:
                        st.error("Lỗi: Ghế này đã được bán hoặc hệ thống đang bận. Vui lòng đổi ghế khác!")
                
            st.info("Vui lòng hoàn tất việc chọn Phim, Ngày và Giờ ở phía trên để hệ thống hiển thị khoang ghế.")
    
    # ==========================================
    # TAB 7: QUẢN LÝ & HỦY VÉ KHÁCH HÀNG
    # ==========================================
    with tab_tickets:
        st.subheader("HỦY VÉ và GIẢI PHÓNG GHẾ")
        st.info("Chọn vé từ danh sách bên dưới để hệ thống hoàn trống ghế.")
        
        # Gọi trực tiếp Controller để lấy danh sách vé đang hoạt động
        active_tickets = admin_controller.get_active_tickets()
                
        if not active_tickets:
            st.success("Hiện không có vé nào đang hoạt động hoặc cần hủy.")
        else:
            ticket_options = ["-- Chọn vé cần hủy --"]
            ticket_mapping_list = [] # Sử dụng mảng cặp thay thế cho Dictionary
            
            for t in active_tickets:
                t_id = t.get_ticket_id()
                st_id = t.get_showtime_id()
                
                display_str = f"Mã vé: {t_id} (Suất chiếu: {st_id})"
                
                ticket_options = ticket_options + [display_str]
                ticket_mapping_list = ticket_mapping_list + [[display_str, t_id]]
                
            c1, c2 = st.columns([2, 1])
            with c1:
                selected_ticket_str = st.selectbox("Danh sách vé đã bán:", ticket_options, key="admin_cancel_sel")
                
            with c2:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                if st.button("XÁC NHẬN HỦY VÉ", type="primary", use_container_width=True):
                    
                    if selected_ticket_str == "-- Chọn vé cần hủy --":
                        st.warning("Vui lòng chọn một vé từ danh sách!")
                    else:
                        # Thuật toán tìm kiếm tuần tự thủ công để lấy ra mã vé cần hủy
                        cancel_ticket_id = None
                        for pair in ticket_mapping_list:
                            if pair[0] == selected_ticket_str:
                                cancel_ticket_id = pair[1]
                                break
                        
                        # Gọi hàm hủy vé 
                        success = booking_controller.admin_cancel_ticket(cancel_ticket_id)
                        
                        if success:
                            st.success(f"Đã hủy vé {cancel_ticket_id} và giải phóng ghế thành công!")
                            time.sleep(1)
                            st.rerun() 
                        else:
                            st.error("Hủy vé thất bại! Hệ thống không thể giải phóng ghế.")

# ------------------------------------------
# B. GIAO DIỆN KHÁCH HÀNG - TRANG CHỦ
# ------------------------------------------
elif st.session_state.current_page == 'home':
    
    # 1. ĐỌC DỮ LIỆU CẤU HÌNH GIAO DIỆN
    all_movies = movie_controller.get_movie_data()
    try:
        ui_config = movie_controller.load_ui_config()
        st.session_state.config_slider = ui_config["SLIDER"]
        st.session_state.config_list = ui_config["LIST"]
    except Exception:
        st.session_state.config_slider = []
        st.session_state.config_list = []

    # Phân loại dữ liệu hiển thị bằng vòng lặp tìm kiếm tiêu chuẩn
    slider_movies = []
    display_movies = []
    
    if all_movies:
        # Lọc phim cho Bảng trượt động
        for m in all_movies:
            for title in st.session_state.config_slider:
                if m.get_title() == title:
                    slider_movies += [m]
                    break
        
        # Lọc phim cho Danh sách hiển thị
        for m in all_movies:
            for title in st.session_state.config_list:
                if m.get_title() == title:
                    display_movies += [m]
                    break

        # Nếu danh sách Slider rỗng, lấy 3 phim đầu tiên
        count_slider = 0
        for _ in slider_movies: count_slider += 1
        if count_slider == 0:
            count_all = 0
            for m in all_movies:
                if count_all < 3:
                    slider_movies += [m]
                count_all += 1
                
        # Nếu danh sách Hiển thị rỗng, lấy 8 phim đầu tiên
        count_display = 0
        for _ in display_movies: count_display += 1
        if count_display == 0:
            count_all = 0
            for m in all_movies:
                if count_all < 8:
                    display_movies += [m]
                count_all += 1

    # 2. BẢNG TRƯỢT ĐỘNG
    st.markdown("<h2 style='text-align: center; color: #5C161B; margin-bottom: 20px; z-index:10; position:relative;'>— TÂM ĐIỂM TUẦN NÀY —</h2>", unsafe_allow_html=True)
    
    if not slider_movies:
        st.info("Hệ thống chưa thiết lập tác phẩm Tâm Điểm.")
    else:
        slides_html_content = ""
        i = 0
        for m in slider_movies:
            active_class = "active" if i == 0 else "" 
            img_url = m.get_poster_path() if m.get_poster_path() else "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1000&q=80"
            desc = m.get_description() if m.get_description() else "Siêu phẩm điện ảnh kinh điển không thể bỏ lỡ tại Sunnyx Vintage Cinema."
            
            slides_html_content += f"""
            <div class="slide {active_class}">
                <div class="poster" style="background-image: url('{img_url}');"></div>
                <div class="content">
                    <h1>{m.get_title()}</h1>
                    <p>{desc}</p>
                    <div>
                        <span class="tag">{m.get_genre()}</span>
                        <span class="tag">⏳ {m.get_duration()} phút</span>
                    </div>
                </div>
            </div>
            """
            i += 1

        slider_html = f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Courier+Prime:wght@400;700&display=swap');
        body {{ margin: 0; background-color: transparent; font-family: 'Playfair Display', serif;}}
        .slider-container {{ width: 100%; height: 350px; position: relative; overflow: hidden; border: 4px double #D4AF37; border-radius: 10px; background: #2A080A; box-shadow: 0 10px 20px rgba(0,0,0,0.3);}}
        .slide {{ position: absolute; width: 100%; height: 100%; display: flex; transition: opacity 1s ease-in-out; opacity: 0; }}
        .slide.active {{ opacity: 1; z-index: 10; }}
        .poster {{ width: 35%; height: 100%; background-size: cover; background-position: center; border-right: 2px dashed #D4AF37; }}
        .content {{ width: 65%; padding: 30px; color: #FFF2C8; display: flex; flex-direction: column; justify-content: center; }}
        h1 {{ color: #D4AF37; font-size: 32px; margin: 0 0 10px 0; text-transform: uppercase; letter-spacing: 1px; line-height: 1.2; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;}}
        p {{ font-family: 'Courier Prime', monospace; font-size: 15px; line-height: 1.6; color: #E8DCC4; margin-bottom: 15px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;}}
        .tag {{ display: inline-block; border: 1px solid #D4AF37; padding: 5px 12px; font-size: 13px; margin-right: 10px; color: #D4AF37; font-family: 'Courier Prime', monospace;}}
        .nav-btn {{ position: absolute; top: 50%; transform: translateY(-50%); background: rgba(0,0,0,0.5); color: #D4AF37; border: 1px solid #D4AF37; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; font-size: 20px; font-weight: bold; z-index: 20; transition: 0.3s;}}
        .nav-btn:hover {{ background: #D4AF37; color: #2A080A;}}
        .prev {{ left: 10px; }} .next {{ right: 10px; }}
        </style>

        <div class="slider-container">
        {slides_html_content}
        <button class="nav-btn prev" onclick="moveSlide(-1)">&#10094;</button>
        <button class="nav-btn next" onclick="moveSlide(1)">&#10095;</button>
        </div>

        <script>
        let currentSlide = 0; 
        const slides = document.querySelectorAll('.slide');
        let slideInterval;

        function showSlide(index) {{ 
            slides.forEach(s => s.classList.remove('active')); 
            if(index >= slides.length) currentSlide = 0; 
            else if(index < 0) currentSlide = slides.length - 1; 
            else currentSlide = index; 
            slides[currentSlide].classList.add('active');
        }}

        function moveSlide(step) {{ 
            showSlide(currentSlide + step); 
            resetInterval();
        }}
        
        function resetInterval() {{
            clearInterval(slideInterval);
            slideInterval = setInterval(() => moveSlide(1), 4000);
        }}
        resetInterval();
        </script>
        """
        components.html(slider_html, height=360)

    # 3. ĐẶT VÉ NHANH ĐỘNG
    # Lấy toàn bộ dữ liệu từ kho lên để chuẩn bị lọc
    all_movies = movie_controller.get_movie_data()
    all_showtimes = showtime_controller.get_showtime_data()

    with st.container():
        st.markdown('<div class="vintage-ticket"><div class="ticket-title">QUẦY BÁN VÉ NHANH</div>', unsafe_allow_html=True)
        
        # --- LỰA CHỌN LUỒNG ĐẶT VÉ ---
        booking_mode = st.radio(
            "Bạn muốn tìm lịch chiếu theo cách nào?", 
            ["Chọn Phim", "Chọn Lịch chiếu"], 
            horizontal=True,
            key="cust_booking_mode" # Thêm key để Streamlit không nhầm với form Admin
        )

        qb1, qb2, qb3, qb4 = st.columns([2, 1, 1, 1])
        selected_fast_movie = None 

        # --- LUỒNG ĐẶT VÉ 1: TÌM KIẾM THEO TÁC PHẨM ---
        if booking_mode == "Chọn Phim":
            with qb1:
                movie_titles = ["-- Chọn phim --"]
                if all_movies:
                    for m in all_movies:
                        movie_titles += [m.get_title()]
                else:
                    movie_titles = ["Hiện chưa có phim"]
                    
                selected_title = st.selectbox("1. Chọn Cuộn Phim", movie_titles, key="cust_movie_sel_1")
                
            if selected_title not in ["-- Chọn phim --", "Hiện chưa có phim"]:
                selected_fast_movie = selected_title 
                
                movie_node = movie_controller.search_by_title(selected_title)
                if movie_node:
                    selected_movie_id = movie_node.get_data().get_movie_id()
                    movie_shows = showtime_controller.get_showtimes_by_movie(selected_movie_id)
                else:
                    movie_shows = []
                        
                available_dates = showtime_controller.get_unique_sorted_dates(movie_shows)
                
                with qb2:
                    selected_date = st.selectbox("2. Ngày Chiếu", ["-- Chọn ngày --"] + available_dates if available_dates else ["Chưa có lịch"], key="cust_date_sel_1")
                    
                if selected_date not in ["-- Chọn ngày --", "Chưa có lịch"]:
                    # Khởi tạo mảng rỗng và dùng vòng lặp for duyệt tuần tự
                    date_shows = []
                    for s in movie_shows:
                        if showtime_controller.extract_date(s) == selected_date:
                            date_shows += [s]
                    available_times = showtime_controller.get_unique_sorted_times(date_shows)
                    
                    with qb3:
                        selected_time = st.selectbox("3. Khung Giờ", ["-- Chọn giờ --"] + available_times if available_times else ["Chưa có giờ"], key="cust_time_sel_1")
                else:
                    with qb3:
                        st.selectbox("3. Khung Giờ", ["-- Chọn giờ --"], key="cust_time_sel_1_empty")
            else:
                with qb2:
                    st.selectbox("2. Ngày Chiếu", ["-- Chọn ngày --"], key="cust_date_sel_1_empty")
                with qb3:
                    st.selectbox("3. Khung Giờ", ["-- Chọn giờ --"], key="cust_time_sel_1_empty2")

        # --- LUỒNG ĐẶT VÉ 2: TRUY VẤN THEO THỜI GIAN ---
        else: 
            with qb1:
                all_dates = showtime_controller.get_unique_sorted_dates(all_showtimes)
                selected_date = st.selectbox("1. Ngày Chiếu", ["-- Chọn ngày --"] + all_dates if all_dates else ["Chưa có lịch"], key="admin_date_sel_2")
                
            if selected_date != "-- Chọn ngày --" and selected_date != "Chưa có lịch":
                
                daily_schedule = showtime_controller.get_schedule_by_date(selected_date)
                
                movie_titles = []
                for group in daily_schedule:
                    movie_titles += [group[0].get_title()]
                
                with qb2:
                    selected_title = st.selectbox("2. Chọn Cuộn Phim", ["-- Chọn phim --"] + movie_titles if movie_titles else ["Không có phim"], key="admin_movie_sel_2")
                    
                if selected_title != "-- Chọn phim --" and selected_title != "Không có phim":
                    selected_fast_movie = selected_title 
                    
                    selected_group = None
                    for g in daily_schedule:
                        if g[0].get_title() == selected_title:
                            selected_group = g
                            break
                    
                    if selected_group:
                        available_times = showtime_controller.get_unique_sorted_times(selected_group[1])
                        with qb3:
                            selected_time = st.selectbox("3. Khung Giờ", ["-- Chọn giờ --"] + available_times if available_times else ["Chưa có giờ"], key="admin_time_sel_2")
                else:
                    with qb3:
                        st.selectbox("3. Khung Giờ", ["-- Chọn giờ --"], key="admin_time_sel_2_empty")
            else:
                with qb2:
                    st.selectbox("2. Chọn Cuộn Phim", ["-- Chọn phim --"], key="admin_movie_sel_2_empty")
                with qb3:
                    st.selectbox("3. Khung Giờ", ["-- Chọn giờ --"], key="admin_time_sel_2_empty2")

        # --- KIỂM DUYỆT TRẠNG THÁI TIẾN HÀNH ĐẶT VÉ ---
        with qb4: 
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button("XUẤT VÉ", type="primary", use_container_width=True, key="cust_btn_book"):
                if not st.session_state.is_logged_in:
                    st.error("Xuất trình thẻ thành viên (Đăng nhập)!")
                elif not selected_fast_movie or selected_fast_movie in ["-- Chọn phim --", "Hiện chưa có phim"]:
                    st.warning("Vui lòng chọn phim!")
                elif selected_date in ["-- Chọn ngày --", "Chưa có lịch", None]:
                    st.warning("Vui lòng chọn ngày chiếu!")
                elif selected_time in ["-- Chọn giờ --", "Chưa có giờ", None]:
                    st.warning("Vui lòng chọn khung giờ chiếu!")
                else:
                    # Lưu Ngày & Giờ khách vừa chọn vào bộ nhớ tạm để sang phòng vé lôi ra dùng
                    st.session_state.target_date = selected_date
                    st.session_state.target_time = selected_time
                    st.session_state.selected_seats = []
                    navigate_to("booking", selected_fast_movie)
                    
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 4. XUẤT BẢN DANH MỤC PHIM TRÌNH CHIẾU DẠNG LƯỚI ---
    st.markdown("<h2 style='text-align: center; color: #5C161B; margin-top: 40px; margin-bottom: 30px; position:relative; z-index:10;'>— CÁC TÁC PHẨM TRÌNH CHIẾU —</h2>", unsafe_allow_html=True)
    st.markdown('<div class="movie-card-container">', unsafe_allow_html=True)
    

    if not display_movies:
        st.info("Hiện hệ thống chưa thiết lập phim hiển thị tại sảnh. Vui lòng liên hệ Admin.")
    else:
        # Đếm tổng số phim hiển thị
        total_display = 0
        for _ in display_movies:
            total_display += 1
        
        cols = st.columns(4)
        i = 0
        for movie in display_movies:
            col = cols[i % 4]
            create_premium_movie_card(
                col, 
                movie.get_title(), 
                movie.get_genre(), 
                movie.get_duration(), 
                movie.get_base_price(), 
                movie.get_poster_path()
            )
            
            # Xuống dòng sau mỗi 4 phim
            if (i + 1) % 4 == 0 and i != (total_display - 1):
                st.write("") 
                cols = st.columns(4)
            i += 1
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------
# C. GIAO DIỆN KHÁCH HÀNG - ĐẶT GHẾ (BOOKING)
# ------------------------------------------
elif st.session_state.current_page == 'booking':

    if st.button("TRỞ VỀ SẢNH CHÍNH", type="secondary"): navigate_to("home")
    
    if st.session_state.get('booking_success', False):
        st.success("🎉 Giao dịch thành công! Chúc quý khách xem phim vui vẻ.")
            
        # -----------  IN RA TẤT CẢ VÉ KHÁCH VỪA MUA -----------
        recent = st.session_state.get('recent_tickets', [])
        if recent:
            st.write("**VÉ ĐIỆN TỬ CỦA BẠN:**")
            for t_id in recent:
                ticket_info = booking_controller.generate_ticket_info(t_id)
                st.info(ticket_info)
        # ------------------------------------------------------

        show_popcorn_effect()
        st.session_state.booking_success = False 
        st.session_state.recent_tickets = [] # Xóa bộ nhớ tạm sau khi đã in xong

    selected_movie_title = st.session_state.selected_movie
    st.markdown(f"<h2 style='color:#5C161B;'>XUẤT VÉ: {selected_movie_title}</h2>", unsafe_allow_html=True)

    # Tìm phim tương ứng
    movie_node = movie_controller.search_by_title(selected_movie_title)
    if movie_node is None:
        st.error("Không tìm thấy dữ liệu của phim này trong kho!")
    else:
        m_data = movie_node.get_data()
        
        # HIỂN THỊ THÔNG TIN PHIM 
        st.markdown("---")
        col_poster, col_info = st.columns([1, 3]) # Chia tỷ lệ 1 phần ảnh, 3 phần chữ
        
        with col_poster:
            # Hiển thị ảnh, nếu không có link thì dùng ảnh nền điện ảnh mặc định
            poster_url = m_data.get_poster_path() if m_data.get_poster_path() else "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&q=80"
            st.image(poster_url, use_container_width=True)
            
        with col_info:
            st.markdown(f"<h3 style='color:#5C161B; margin-top: 0;'>{m_data.get_title()}</h3>", unsafe_allow_html=True)
            st.markdown(f"**Thể loại:** {m_data.get_genre()}")
            st.markdown(f"**Thời lượng:** {m_data.get_duration()} phút")
            st.markdown(f"**Giá vé cơ bản:** <span style='color:#D4AF37; font-weight:bold;'>{m_data.get_base_price():,.0f} VNĐ</span>", unsafe_allow_html=True)
            st.markdown(f"**Nội dung:** {m_data.get_description()}")
        st.markdown("---")
        
        # --- LẤY CHÍNH XÁC SUẤT CHIẾU THEO NGÀY GIỜ Ở SẢNH ---
        target_date = st.session_state.get('target_date')
        target_time = st.session_state.get('target_time')
        
        st_data = None
        if target_date and target_time:
            st_data = showtime_controller.find_exact_showtime(
                m_data.get_movie_id(), target_date, target_time
            )
        else:
            showtimes = showtime_controller.get_showtime_data()
            # Tự duyệt mảng để tìm suất chiếu đầu tiên khớp mã phim
            st_data = None
            if showtimes:
                for s in showtimes:
                    if s.get_movie_id() == m_data.get_movie_id():
                        st_data = s
                        break
        
        if st_data is None:
            st.warning("Rạp chưa mở khung giờ chiếu nào cho tác phẩm này. Vui lòng quay lại sau!")
        else:
            st.info(f"Địa điểm: Sunnyx Cinema | Phòng: {st_data.get_room_id()} | Giờ chiếu: {st_data.get_start_time()}")
            
            col_ref1, col_ref2 = st.columns([3, 1])
            with col_ref2:
                if st.button("Cập nhật ghế mới", use_container_width=True, key="sync_seats_btn"):
                    booking_controller.refresh_booking_data()
                    st.rerun()
            
            st.markdown('<div class="seat-screen">MÀN CHIẾU</div>', unsafe_allow_html=True)
            st.write("")
            
            # Load ma trận ghế thực tế từ hệ thống
            seat_matrix = st_data.get_seat_matrix()
            rows = seat_matrix.get_rows()
            cols = seat_matrix.get_cols()
            
            for r in range(rows):
                cols_st = st.columns(cols)
                row_char = chr(65 + r)
                for c in range(cols):
                    seat_name = f"{row_char}{c+1}"
                    
                    # --- ĐIỀU KHIỂN TÌNH TRẠNG GHẾ ---
                    status = seat_matrix.check_status(r, c)
                    is_selected = seat_name in st.session_state.selected_seats
                    
                    # Ghế chuyển xám khi: Đã mua (BOOKED) HOẶC Đang bị NGƯỜI KHÁC giữ chỗ (RESERVED)
                    is_unavailable = (status == SeatStatus.BOOKED) or (status == SeatStatus.RESERVED and not is_selected)
                    
                    with cols_st[c]:
                        if is_unavailable:
                            st.button(seat_name, key=f"seat_{seat_name}", disabled=True, use_container_width=True)
                        else:
                            btn_type = "primary" if is_selected else "secondary"
                            # Không gán disabled lúc đang thanh toán để ghế không bị chuyển xám 
                            if st.button(seat_name, key=f"seat_{seat_name}", type=btn_type, use_container_width=True):
                                
                                if st.session_state.get('payment_step', False):
                                    # Không đổi ghế lúc đang có mã QR
                                    st.toast("Đang trong quá trình thanh toán, không thể đổi ghế!")
                                else:
                                    if is_selected:
                                        updated_seats = []
                                        for s in st.session_state.selected_seats:
                                            if s != seat_name:
                                                updated_seats = updated_seats + [s]
                                        st.session_state.selected_seats = updated_seats
                                    else: st.session_state.selected_seats = st.session_state.selected_seats + [seat_name]
                                    st.rerun() 
                                
            st.divider()

            num_selected = 0
            for _ in st.session_state.selected_seats:
                num_selected += 1

            base_price = m_data.get_base_price()
            total_price = num_selected * base_price
            
            col_sum1, col_sum2 = st.columns([3, 1])
            with col_sum1:
                seats_display = ""
                count = 0
                for s in st.session_state.selected_seats:
                    seats_display += s
                    count += 1
                    if count < num_selected:  # Nếu chưa phải ghế cuối cùng thì cộng thêm dấu phẩy
                        seats_display += ", "

                st.markdown(f"**Vị trí đã chọn:** {seats_display if num_selected > 0 else 'Chưa chọn'}")
                st.markdown(f"**Tổng Lệ phí:** <span style='color:#5C161B; font-size: 1.2rem; font-weight:bold;'>{total_price:,.0f} VNĐ</span>", unsafe_allow_html=True)
            
            # --- KHỞI TẠO BIẾN TRẠNG THÁI THANH TOÁN ---
            if "payment_step" not in st.session_state:
                st.session_state.payment_step = False
            
            # # --- XỬ LÝ GIAO DỊCH ---
            with col_sum2:
                if not st.session_state.payment_step:
                    if st.button("THANH TOÁN", type="primary", use_container_width=True, disabled=(num_selected==0), key="btn_thanh_toan"):
                        
                        seats_to_book = []
                        for seat in st.session_state.selected_seats:
                            r, c = booking_controller.parse_seat_id(seat)
                            seats_to_book += [(r, c)]
                        
                        try:
                            # Gọi hàm đặt vé 1 lần duy nhất cho cả cụm ghế
                            ticket_ids = booking_controller.process_booking(
                                st.session_state.user_obj,
                                m_data,
                                st_data,
                                seats_to_book
                            )

                            if ticket_ids: 
                                st.session_state.generated_ticket_ids = ticket_ids 
                                st.session_state.payment_step = True
                                st.session_state.payment_start_time = time.time()
                                #st.rerun()
                            else:
                                st.error("Thao tác thất bại! Một hoặc nhiều ghế bạn chọn vừa bị người khác mua mất cách đây vài giây. Vui lòng chọn ghế khác.")
                        
                        except Exception as e:
                            st.error(f"Lỗi hệ thống: {e}")
                        
            # --- QUY TRÌNH THANH TOÁN QR & BỘ ĐẾM NGƯỢC ---
            if st.session_state.payment_step:
                st.write("---")
                
                # Tính thời gian trôi qua (bằng giây)
                elapsed_time = time.time() - st.session_state.payment_start_time
                time_left = 300 - int(elapsed_time) 
                
                if time_left > 0:
                    st.markdown("<h4 style='text-align: center; color: #5C161B;'>Vui lòng quét mã QR dưới đây để hoàn tất thanh toán</h4>", unsafe_allow_html=True)
                    
                    countdown_html = f"""
                    <div id="countdown-box" style="text-align: center; padding: 12px; background-color: #fff3cd; color: #856404; border-radius: 8px; border: 1px solid #ffeeba; font-family: monospace;">
                        <h3 id="timer-title" style="margin: 0; font-size: 22px;">Thời gian giữ ghế: <span id="timer" style="color:#dc3545; font-weight:bold;">{time_left // 60}:{time_left % 60:02d}</span></h3>
                        <p id="timer-desc" style="margin: 0; font-size: 14px; margin-top: 5px;">Quá 5 phút, hệ thống sẽ tự động hủy giao dịch và giải phóng ghế!</p>
                    </div>
                    
                    <script>
                        let secondsLeft = {time_left};
                        const timerDisplay = document.getElementById('timer');
                        const boxDisplay = document.getElementById('countdown-box');
                        const titleDisplay = document.getElementById('timer-title');
                        const descDisplay = document.getElementById('timer-desc');
                        
                        const countdownInterval = setInterval(function() {{
                            secondsLeft--;
                            if (secondsLeft <= 0) {{
                                clearInterval(countdownInterval);
                                // GIAO DIỆN BÁO LỖI THANH TOÁN KHÔNG THÀNH CÔNG
                                boxDisplay.style.backgroundColor = "#f8d7da";
                                boxDisplay.style.color = "#721c24";
                                boxDisplay.style.borderColor = "#f5c6cb";
                                titleDisplay.innerHTML = "THANH TOÁN KHÔNG THÀNH CÔNG!";
                                descDisplay.innerHTML = "Đã quá thời gian quy định. Vui lòng bấm nút Xác Nhận bên dưới để cập nhật.";
                            }} else {{
                                let minutes = Math.floor(secondsLeft / 60);
                                let seconds = secondsLeft % 60;
                                timerDisplay.innerHTML = minutes + ":" + (seconds < 10 ? "0" : "") + seconds;
                            }}
                        }}, 1000);
                    </script>
                    """
                    components.html(countdown_html, height=110)
                    
                    # Hiển thị ảnh QR
                    col_qr1, col_qr2, col_qr3 = st.columns([1, 1, 1]) 
                    with col_qr2:
                        st.image("https://i.postimg.cc/zXCdCsg3/image.png", use_container_width=True)
                        st.write("")
                        
                        # Nút xác nhận khi khách đã chuyển khoản thành công
                        if st.button("TÔI ĐÃ CHUYỂN KHOẢN XONG", type="primary", use_container_width=True):
                            # Nếu ấn nút TRƯỚC 5 phút thì xuất vé
                            if time.time() - st.session_state.payment_start_time <= 300:
                                
                                booking_controller.confirm_bookings_bulk(st.session_state.get('generated_ticket_ids', []))
                                    
                                st.session_state.booking_success = True
                                
                                st.session_state.recent_tickets = st.session_state.get('generated_ticket_ids', [])

                                # Làm sạch giỏ hàng và đặt lại các biến trạng thái
                                st.session_state.selected_seats = []
                                st.session_state.generated_ticket_ids = []
                                st.session_state.payment_step = False
                                
                                booking_controller.refresh_booking_data()
                                st.rerun()
                            else:
                                st.rerun() 
                
                else:
                    # --- HỦY GIAO DỊCH KHI VƯỢT QUÁ THỜI GIAN ---
                    st.error("THANH TOÁN KHÔNG THÀNH CÔNG!")
                    
                    # Gọi hàm tự động quét và giải phóng vé quá hạn của Controller (Set timeout = 5 phút)
                    booking_controller.cleanup_unfinished_reservations(timeout_minutes=5)
                    
                    st.warning("Đã hết thời gian giữ ghế. Hệ thống đã tự động hủy giao dịch và hoàn trống ghế của bạn!")
                    
                    st.session_state.selected_seats = []
                    st.session_state.payment_step = False
                    
                    if st.button("Bắt đầu đặt lại", type="primary"):
                        st.session_state.selected_seats = [] # RESET GHẾ
                        st.rerun()

# ------------------------------------------
# D. GIAO DIỆN KHÁCH HÀNG - LỊCH SỬ VÉ
# ------------------------------------------
elif st.session_state.current_page == 'history':
    if st.button("TRỞ VỀ SẢNH CHÍNH", type="secondary"): navigate_to("home")
    st.markdown("<h2 style='color:#5C161B;'>BỘ SƯU TẬP VÉ</h2>", unsafe_allow_html=True)
    
    # Trích xuất dữ liệu mảng bằng Tìm kiếm tuần tự
    history_list = booking_controller.get_booking_history(st.session_state.user_obj.get_user_id())
    
    if not history_list:
        st.info("Quý khách chưa sở hữu vé nào trong kho lưu trữ.")
    else:
        data = []
        for ticket in history_list:
            m_node = movie_controller.search_by_id(ticket.get_movie_id())
            m_title = m_node.get_data().get_title() if m_node else "Phim không xác định"
            
            data += [{
                "Mã Vé": ticket.get_ticket_id(),
                "Tên Phim": m_title,
                "Ghế": ticket.get_seat_id(),
                "Lệ phí": f"{ticket.get_price():,.0f} đ",
                "Trạng thái": ticket.get_status()
            }]
            
        df_history = pd.DataFrame(data)
        st.dataframe(df_history, use_container_width=True, hide_index=True)

# ==========================================
# 8. QUẢNG CÁO
# ==========================================
if not st.session_state.ad_closed and st.session_state.current_page == 'home' and st.session_state.user_role != 'admin':
    show_advertisement()
