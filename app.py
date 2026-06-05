# Import thư viện
import streamlit as st
import pandas as pd
import random
import streamlit.components.v1 as components

# Import các thành phần của hệ thống
from models.entities import SeatStatus, MovieData
from data_structures.file_io import FileIOHandler
from controllers.auth_controller import AuthController
from controllers.movie_controller import MovieController
from controllers.booking_controller import BookingController
from controllers.showtime_controller import ShowtimeController
from controllers.room_controller import RoomController
from controllers.admin_controller import AdminController

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN WEB
# ==========================================
# - page_title: tên hiển thị trên tab trình duyệt
# - page_icon: biểu tượng tab
# - layout="wide": giao diện sử dụng toàn bộ chiều ngang màn hình
# - initial_sidebar_state="expanded": thanh sidebar tự động mở khi mở web

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

# Trạng thái đóng quảng cáo
if 'ad_closed' not in st.session_state:
    st.session_state.ad_closed = False

# Trạng thái đăng nhập
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False

# Vai trò hiện tại
if 'user_role' not in st.session_state:
    st.session_state.user_role = 'guest'

# Tên đăng nhập
if 'username' not in st.session_state:
    st.session_state.username = ''

# Đối tượng User đang đăng nhập
if 'user_obj' not in st.session_state:
    st.session_state.user_obj = None # Lưu Object người dùng thật

# Trạng thái bước thanh toán
if 'payment_step' not in st.session_state:
    st.session_state.payment_step = False

# Trang hiện tại
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

#Phim đang được chọn
if 'selected_movie' not in st.session_state:
    st.session_state.selected_movie = ''

# Danh sách ghế đang chọn
if 'selected_seats' not in st.session_state:
    st.session_state.selected_seats = []

# Dữ liệu cấu hình slider
if 'config_slider' not in st.session_state:
    st.session_state.config_slider= []

#Dữ liệu cấu hình danh sách
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

        # Khởi tạo các Controller của hệ thống:
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

# Gọi lại các biến từ Session State ra để sử dụng xuyên suốt các hành động click của user
auth_controller = st.session_state.auth_ctrl
movie_controller = st.session_state.movie_ctrl
showtime_controller = st.session_state.showtime_ctrl
room_controller = st.session_state.room_ctrl
booking_controller = st.session_state.booking_ctrl
admin_controller = st.session_state.admin_ctrl

# ==========================================
# 3. CHUYỂN TRANG & POPUP QUẢNG CÁO
# ==========================================
# Import hàm phụ trợ giao diện từ file bên ngoài
from ui_components import navigate_to, show_advertisement, create_premium_movie_card, show_popcorn_effect

# ==========================================
# 4. CSS DÀNH CHO GIAO DIỆN (VINTAGE STYLE)
# ==========================================
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
/* --- VŨ KHÍ HỦY DIỆT (ĐÃ NÂNG CẤP): ĐỒNG BỘ KÍCH THƯỚC & MÀU SẮC GHẾ --- */
    
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

    /* 1. GHẾ TRỐNG (Secondary) */
    .stButton > button[kind="secondary"] {
        background-color: #E8DCC4; 
        color: #5C161B !important; 
        border: 1px solid #B89947;
    }

    /* 2. GHẾ ĐANG CHỌN (Primary) - Bỏ hiệu ứng bóng đổ và di chuyển để không bị giật khung */
    .stButton > button[kind="primary"] {
        background-color: #5C161B !important; 
        color: #D4AF37 !important; 
        border: 2px solid #D4AF37 !important;
        box-shadow: none !important; 
        transform: none !important;
    }

    /* 3. GHẾ ĐÃ BÁN (Disabled) - Chuyển sang màu Xám lạnh */
    .stButton > button:disabled {
        background-color: #9E9E9E !important; 
        color: #E0E0E0 !important; 
        border: 1px solid #757575 !important; 
        cursor: not-allowed !important; 
        opacity: 0.8 !important;
    } 

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="bg-decoration gear-1">⚙</div><div class="bg-decoration gear-2">⚙</div><div class="bg-decoration gear-3">⚙</div>', unsafe_allow_html=True)

# ==========================================
# 5. SIDEBAR: ĐĂNG NHẬP
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #5C161B; font-family: \"Playfair Display\", serif;'>PHÒNG VÉ</h2>", unsafe_allow_html=True)
    
    if not st.session_state.is_logged_in:
        st.info("Vui lòng Đăng nhập")
        tab_login, tab_register = st.tabs(["Đăng nhập", "Đăng Ký"])
        
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
                        role = auth_controller.login(username_input, password_input)
                        if role != "FAILED":
                            st.session_state.is_logged_in = True
                            st.session_state.username = username_input
                            st.session_state.user_obj = auth_controller.get_current_user() # Load User Data object
                            
                            if role == "ADMIN":
                                st.session_state.user_role = "admin"
                                st.session_state.current_page = "admin_dash"
                            else:
                                st.session_state.user_role = "customer"
                                st.session_state.current_page = "home"
                            st.rerun()
                        else:
                            st.error("Thông tin không chính xác!")
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
        st.success(f"Kính chào quý khách **{st.session_state.username}**.")
        st.caption(f"Hạng: {st.session_state.user_role.upper()}")
        if st.session_state.user_role == 'customer':
            if st.button("Sảnh Chính", use_container_width=True): navigate_to("home")
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

try:
    # ==========================================
    # 6. KHUNG GIAO DIỆN CHÍNH
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
        
        # Hiển thị Metric
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Tổng Doanh thu", f"{admin_controller.calculate_revenue():,.0f} đ")
        c2.metric("Vé xuất ra", f"{admin_controller.count_tickets()} vé")
        c3.metric("Phim trình chiếu", f"{admin_controller.count_movies()} cuộn")
        c4.metric("Thành viên hệ thống", f"{len(auth_controller.get_all_users())} người")
        st.divider()
        
        # Chia Tab cho Admin
        tab_manage, tab_showtime, tab_display, tab_top, tab_offline, tab_tickets = st.tabs(["Quản Lý Phim", "Quản Lý Suất Chiếu", "Cấu Hình Giao Diện", "Top Doanh Thu", "Bán Vé Tại Quầy", "Quản Lý Vé"])
        
        # TAB 1: QUẢN LÝ KHO PHIM (THÊM / SỬA / XÓA)
        with tab_manage:
            manage_action = st.radio("Chọn thao tác:", ["Thêm Phim Mới", "Cập Nhật Phim", "Xóa Phim"], horizontal=True)
            st.write("---")
            
            # Load danh sách phim hiện tại
            all_movies = movie_controller.get_movie_data()
            movie_dict = {m.get_title(): m for m in all_movies}
            
            # --- THÊM PHIM ---
            if manage_action == "Thêm Phim Mới":
                with st.form("add_movie_form"):
                    st.subheader("Thêm Tác Phẩm Mới")
                    new_title = st.text_input("Tên phim (*)")
                    new_genre = st.text_input("Thể loại (*)")
                    
                    col1, col2 = st.columns(2)
                    new_duration = col1.number_input("Thời lượng (phút)", min_value=1, value=120)
                    new_price = col2.number_input("Giá vé cơ bản (VNĐ)", min_value=0, value=85000, step=5000)
                    
                    new_poster = st.text_input("Link ảnh Poster (URL)")
                    new_desc = st.text_area("Mô tả tóm tắt nội dung")
                    
                    if st.form_submit_button("THÊM VÀO KHO", type="primary"):
                        if not new_title.strip() or not new_genre.strip():
                            st.error("Vui lòng điền đầy đủ Tên phim và Thể loại!")
                        else:
                            # CODE MỚI: Tạo object và gọi hàm trực tiếp, bọc trong try-except
                            new_id = movie_controller.generate_movie_id()
                            new_movie = MovieData(
                                movie_id=new_id,
                                title=new_title,
                                genre=new_genre,
                                duration=new_duration,
                                description=new_desc,
                                base_price=new_price,
                                poster_path=new_poster
                            )
                            
                            try:
                                if movie_controller.add_movie(new_movie):
                                    st.success(f"Đã thêm phim '{new_title}' thành công!")
                                    st.rerun()
                                else:
                                    st.error("Lỗi hệ thống khi lưu phim!")
                            except ValueError as e:
                                # Bắt đúng lỗi "Tên phim này đã tồn tại trong hệ thống!" từ MovieController ném lên
                                st.error(f"Lỗi: {e}")
            # --- CẬP NHẬT PHIM ---
            elif manage_action == "Cập Nhật Phim":
                if not movie_dict:
                    st.warning("Kho rỗng. Chưa có phim nào để cập nhật.")
                else:
                    selected_movie_title = st.selectbox("Chọn phim cần sửa:", list(movie_dict.keys()))
                    selected_movie = movie_dict[selected_movie_title]
                    
                    with st.form("update_movie_form"):
                        st.subheader(f"Chỉnh sửa: {selected_movie_title}")
                        upd_title = st.text_input("Tên phim", value=selected_movie.get_title())
                        upd_genre = st.text_input("Thể loại", value=selected_movie.get_genre())
                        
                        col1, col2 = st.columns(2)
                        upd_duration = col1.number_input("Thời lượng (phút)", min_value=1, value=selected_movie.get_duration())
                        upd_price = col2.number_input("Giá vé (VNĐ)", min_value=0, value=int(selected_movie.get_base_price()), step=5000)
                        
                        upd_poster = st.text_input("Link ảnh Poster", value=selected_movie.get_poster_path())
                        upd_desc = st.text_area("Mô tả", value=selected_movie.get_description())
                        
                        if st.form_submit_button("LƯU THAY ĐỔI", type="primary"):
                            if movie_controller.update_movie(
                                movie_id=selected_movie.get_movie_id(),
                                title=upd_title,
                                genre=upd_genre,
                                duration=upd_duration,
                                description=upd_desc,
                                base_price=upd_price,
                                poster_path=upd_poster
                            ):
                                st.success("Bản ghi đã được cập nhật thành công!")
                                st.rerun()
                            else:
                                st.error("Có lỗi xảy ra khi lưu.")

            # --- XÓA PHIM ---
            elif manage_action == "Xóa Phim":
                if not movie_dict:
                    st.warning("Kho rỗng. Không có phim để xóa.")
                else:
                    del_movie_title = st.selectbox("Chọn phim muốn xoá:", list(movie_dict.keys()))
                    del_movie = movie_dict[del_movie_title]
                    
                    st.error(f"Cảnh báo: Bạn sắp xóa cuộn phim **{del_movie_title}**. Thao tác này không thể hoàn tác.")
                    if st.button("XÁC NHẬN XÓA", type="primary"):
                        if movie_controller.delete_movie(del_movie.get_movie_id(), showtime_controller):
                            st.success(f"Đã dọn dẹp '{del_movie_title}' khỏi kho!")
                            st.rerun()
                        else:
                            st.error("Không thể xóa! Phim này đang có suất chiếu hoạt động hoặc khách đã mua vé.")

        # TAB 1.5: QUẢN LÝ SUẤT CHIẾU (THÊM / XÓA LỊCH CHIẾU)
        with tab_showtime:
            st_action = st.radio("Chọn thao tác:", ["Thêm Suất Chiếu Mới", "Xóa Suất Chiếu"], horizontal=True, key="st_action_radio")
            st.write("---")

            all_movies = movie_controller.get_movie_data()
            all_showtimes = showtime_controller.get_showtime_data()

            # ==========================================
            # CHỨC NĂNG 1: THÊM SUẤT CHIẾU
            # ==========================================
            if st_action == "Thêm Suất Chiếu Mới":
                if not all_movies:
                    st.warning("Kho rỗng. Vui lòng vào Tab 'Quản Lý Phim' để thêm phim trước khi tạo suất chiếu.")
                else:
                    # Dùng vòng lặp cơ bản để tạo list tên phim (Tránh dùng list comprehension)
                    movie_titles = ["-- Chọn phim --"]
                    for m in all_movies:
                        movie_titles.append(m.get_title())

                    with st.form("add_showtime_form"):
                        st.subheader("Lên Lịch Chiếu Mới")
                        sel_movie_title = st.selectbox("1. Chọn Tác Phẩm", movie_titles)

                        c1, c2 = st.columns(2)
                        with c1:
                            new_date = st.text_input("2. Ngày chiếu (Định dạng: YYYY-MM-DD)", placeholder="VD: 2026-06-01")
                            room_id = st.text_input("4. Mã Phòng Chiếu", value="R01")
                        with c2:
                            new_time = st.text_input("3. Giờ chiếu (Định dạng: HH:MM)", placeholder="VD: 19:30")
                            room_rows = st.number_input("Số hàng ghế của phòng", min_value=1, value=10)
                            room_cols = st.number_input("Số cột ghế của phòng", min_value=1, value=10)

                        if st.form_submit_button("TẠO SUẤT CHIẾU", type="primary"):
                            if sel_movie_title == "-- Chọn phim --":
                                st.error("Vui lòng chọn phim!")
                            elif not new_date.strip() or not new_time.strip():
                                st.error("Vui lòng nhập đầy đủ ngày và giờ chiếu!")
                            else:
                                # 1. Tìm ID phim bằng vòng lặp
                                selected_movie_id = None
                                for m in all_movies:
                                    if m.get_title() == sel_movie_title:
                                        selected_movie_id = m.get_movie_id()
                                        break

                                # 2. Nối chuỗi ngày giờ
                                start_time_str = f"{new_date.strip()} {new_time.strip()}"

                                # 3. Tạo ID suất chiếu mới tự động
                                new_st_id = showtime_controller.generate_showtime_id()

                                # 4. Khởi tạo đối tượng Showtime
                                from models.entities import Showtime
                                new_showtime = Showtime(
                                    showtime_id=new_st_id,
                                    movie_id=selected_movie_id,
                                    start_time=start_time_str,
                                    room_id=room_id.strip(),
                                    room_rows=room_rows,
                                    room_cols=room_cols
                                )

                                # 5. Gọi Controller để kiểm tra trùng giờ và lưu file
                                success = showtime_controller.add_showtime(new_showtime, movie_controller)
                                if success:
                                    st.success("Đã lên lịch suất chiếu thành công!")
                                    st.rerun()
                                else:
                                    st.error("Lỗi: Khung giờ này bị trùng lặp với suất chiếu khác trong cùng phòng! Vui lòng chọn giờ khác.")

            # ==========================================
            # CHỨC NĂNG 2: XÓA SUẤT CHIẾU
            # ==========================================
            elif st_action == "Xóa Suất Chiếu":
                if not all_showtimes:
                    st.warning("Hiện chưa có suất chiếu nào trên hệ thống.")
                else:
                    st_options = ["-- Chọn suất chiếu cần xóa --"]
                    st_mapping = {}

                    # Dùng vòng lặp dò thông tin chi tiết từng suất chiếu để Admin dễ chọn
                    for st_obj in all_showtimes:
                        # Tìm tên phim
                        m_title = "Phim không xác định"
                        for m in all_movies:
                            if m.get_movie_id() == st_obj.get_movie_id():
                                m_title = m.get_title()
                                break

                        # Gọi hàm code tay extract_date và extract_time
                        st_date = showtime_controller.extract_date(st_obj)
                        st_time = showtime_controller.extract_time(st_obj)
                        
                        # Tạo nhãn hiển thị cho Dropdown
                        display_str = f"{m_title} | {st_date} - {st_time} | Phòng: {st_obj.get_room_id()}"
                        
                        st_options.append(display_str)
                        st_mapping[display_str] = st_obj.get_showtime_id()

                    with st.form("del_showtime_form"):
                        st.subheader("Dọn Dẹp Lịch Chiếu")
                        sel_st_str = st.selectbox("Danh sách các suất chiếu hiện tại:", st_options)

                        st.error("Lưu ý: Chỉ có thể xóa suất chiếu khi chưa có khách hàng nào đặt vé!")
                        if st.form_submit_button("XÓA SUẤT CHIẾU NÀY", type="primary"):
                            if sel_st_str == "-- Chọn suất chiếu cần xóa --":
                                st.warning("Vui lòng chọn suất chiếu!")
                            else:
                                target_st_id = st_mapping[sel_st_str]
                                
                                # Gọi hàm xóa, truyền booking_controller vào để nó tự check xem có vé nào thuộc suất này chưa
                                success = showtime_controller.delete_showtime(target_st_id, booking_controller)

                                if success:
                                    st.success(f"Đã dọn dẹp thành công suất chiếu!")
                                    st.rerun()
                                else:
                                    st.error("Lỗi: Không thể xóa! Suất chiếu này đã có khách hàng mua vé.")

        # TAB 2: CẤU HÌNH HIỂN THỊ TRANG CHỦ
        with tab_display:
            st.subheader("Cấu Hình Phim Hiển Thị Ở Sảnh Chính")
            st.info("Tùy chọn những cuộn phim nào sẽ được phô diễn ra ngoài giao diện khách hàng.")
            
            all_movies = movie_controller.get_movie_data()
            all_titles = [m.get_title() for m in all_movies]
            
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
                        st.success("Đã lưu cấu hình! Bạn có thể về Sảnh Chính để xem thay đổi.")
        # TAB 3: TOP DOANH THU
        with tab_top: 
            top_movies = admin_controller.get_top_movies_by_revenue()
            if top_movies:
                for m in top_movies:
                    st.markdown(f"**{m.get_title()}** | Sinh lời: <span style='color:#5C161B; font-weight:bold;'>{m.get_revenue():,.0f} đ</span>", unsafe_allow_html=True)
                    st.caption(f"Thể loại: {m.get_genre()} | Thời lượng: {m.get_duration()} phút")
                    st.divider()
            else:
                st.write("Chưa có dữ liệu phim.")
        # TAB 4: BÁN VÉ TẠI QUẦY (OFFLINE DÀNH CHO ADMIN)
        with tab_offline:
            st.subheader("QUẦY BÁN VÉ TRỰC TIẾP (OFFLINE)")
            st.info("Nhân viên xuất vé cho khách mua trực tiếp tại rạp. Đi thẳng vào trang chọn ghế.")
            
            
            all_movies = movie_controller.get_movie_data()
            all_showtimes = showtime_controller.get_showtime_data()

            booking_mode = st.radio(
                "Bạn muốn tìm lịch chiếu theo cách nào?", 
                ["Chọn Phim trước", "Chọn Ngày trước"], 
                horizontal=True,
                key="admin_mode_radio"
            )

            qb1, qb2, qb3, qb4 = st.columns([2, 1, 1, 1])
            selected_fast_movie = None 

            # ==========================================
            # LUỒNG 1: CHỌN PHIM -> NGÀY -> GIỜ
            # ==========================================
            if booking_mode == "Chọn Phim trước":
                with qb1:
                    movie_titles = [m.get_title() for m in all_movies] if all_movies else ["Hiện chưa có phim"]
                    selected_title = st.selectbox("1. Chọn Cuộn Phim", ["-- Chọn phim --"] + movie_titles, key="admin_movie_sel_1")
                    
                if selected_title != "-- Chọn phim --" and selected_title != "Hiện chưa có phim":
                    selected_fast_movie = selected_title 
                    selected_movie_id = next((m.get_movie_id() for m in all_movies if m.get_title() == selected_title), None)
                    movie_shows = [s for s in all_showtimes if str(s.get_movie_id()).strip() == str(selected_movie_id).strip()]
                    available_dates = showtime_controller.get_unique_sorted_dates(movie_shows)
                    
                    with qb2:
                        selected_date = st.selectbox("2. Ngày Chiếu", ["-- Chọn ngày --"] + available_dates if available_dates else ["Chưa có lịch"], key="admin_date_sel_1")
                        
                    if selected_date != "-- Chọn ngày --" and selected_date != "Chưa có lịch":
                        date_shows = [s for s in movie_shows if showtime_controller.extract_date(s) == selected_date]
                        available_times = showtime_controller.get_unique_sorted_times(date_shows)
                        with qb3:
                            selected_time = st.selectbox("3. Khung Giờ", ["-- Chọn giờ --"] + available_times if available_times else ["Chưa có giờ"], key="admin_time_sel_1")
                    else:
                        with qb3:
                            st.selectbox("3. Khung Giờ", ["-- Chọn giờ --"], key="admin_time_sel_1_empty")
                else:
                    with qb2:
                        st.selectbox("2. Ngày Chiếu", ["-- Chọn ngày --"], key="admin_date_sel_1_empty")
                    with qb3:
                        st.selectbox("3. Khung Giờ", ["-- Chọn giờ --"], key="admin_time_sel_1_empty2")

            # ==========================================
            # LUỒNG 2: CHỌN NGÀY -> PHIM -> GIỜ (DÙNG HÀM MỚI TỪ CONTROLLER)
            # ==========================================
            else: 
                with qb1:
                    # Vẫn lấy toàn bộ ngày từ hệ thống để hiển thị cho Ô 1
                    all_dates = showtime_controller.get_unique_sorted_dates(all_showtimes)
                    selected_date = st.selectbox("1. Ngày Chiếu", ["-- Chọn ngày --"] + all_dates if all_dates else ["Chưa có lịch"], key="admin_date_sel_2")
                    
                if selected_date != "-- Chọn ngày --" and selected_date != "Chưa có lịch":
                    
                    # --- GỌI HÀM MỚI CỦA CẬU Ở ĐÂY ---
                    daily_schedule = showtime_controller.get_schedule_by_date(selected_date, movie_controller)
                    
                    # Lọc lấy danh sách tên phim từ dữ liệu Gói trả về
                    movie_titles = [group["movie"].get_title() for group in daily_schedule]
                    
                    with qb2:
                        selected_title = st.selectbox("2. Chọn Cuộn Phim", ["-- Chọn phim --"] + movie_titles if movie_titles else ["Không có phim"], key="admin_movie_sel_2")
                        
                    if selected_title != "-- Chọn phim --" and selected_title != "Không có phim":
                        selected_fast_movie = selected_title 
                        
                        # Dò tìm lại Gói dữ liệu của bộ phim vừa chọn
                        selected_group = next((g for g in daily_schedule if g["movie"].get_title() == selected_title), None)
                        
                        if selected_group:
                            # Móc danh sách các suất chiếu từ trong Gói đó ra và lấy Giờ
                            available_times = showtime_controller.get_unique_sorted_times(selected_group["showtimes"])
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

            # ==========================================
            # CHỐT SUẤT CHIẾU & CHỌN GHẾ TẠI CHỖ
            # ==========================================
            st.markdown("---")
            st.subheader("TIẾN HÀNH CHỌN GHẾ & IN VÉ")
            
            # 1. Dò lại đúng Object Phim và Object Suất Chiếu từ kho dữ liệu
            movie_obj = next((m for m in all_movies if m.get_title() == selected_fast_movie), None)
            
            showtime_obj = None
            if movie_obj and selected_date not in ["-- Chọn ngày --", "Chưa có lịch", None] and selected_time not in ["-- Chọn giờ --", "Chưa có giờ", None]:
                # Gọi trực tiếp Controller để bới đúng suất chiếu
                showtime_obj = showtime_controller.find_exact_showtime(
                    movie_obj.get_movie_id(),
                    selected_date,
                    selected_time
                )

            # 2. Nếu đã chọn xong Phim + Ngày + Giờ thì mới mở khóa bảng chọn ghế
            if movie_obj and showtime_obj:
                c_row, c_col, c_btn = st.columns([1, 1, 2])
                
                with c_row:
                    # Ô nhập Hàng ghế (Truyền vào biến row)
                    seat_row = st.number_input("Hàng ghế (Row Index)", min_value=0, step=1, key="admin_seat_row")
                    
                with c_col:
                    # Ô nhập Số ghế (Truyền vào biến col)
                    seat_col = st.number_input("Số ghế (Col Index)", min_value=0, step=1, key="admin_seat_col")
                    
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
                            st.success(f"Giao dịch thành công! Mã vé điện tử: **{ticket_id}**")
                        else:
                            st.error("Lỗi: Ghế này đã được bán hoặc hệ thống đang bận. Vui lòng đổi ghế khác!")
            else:
                st.info("Vui lòng hoàn tất việc chọn Phim, Ngày và Giờ ở phía trên để hệ thống hiển thị khoang ghế.")
        # TAB 5: QUẢN LÝ VÉ & HỦY VÉ
        with tab_tickets:
            st.subheader("HỦY VÉ & GIẢI PHÓNG GHẾ")
            st.info("Chọn vé từ danh sách bên dưới để hệ thống hoàn trống ghế.")
            
        # Gọi trực tiếp Controller để lấy danh sách vé đang hoạt động
            active_tickets = admin_controller.get_active_tickets()
                    
            if not active_tickets:
                st.success("Hiện không có vé nào đang hoạt động hoặc cần hủy.")
            else:
                # 3. Tạo danh sách hiển thị cho Dropdown
                ticket_options = ["-- Chọn vé cần hủy --"]
                ticket_mapping = {} # Dùng từ điển để giấu Ticket ID ở phía sau
                
                for t in active_tickets:
                    # Đóng gói thông tin vé cho dễ nhìn. 
                    # (Lưu ý: Thay đổi hàm lấy row/col cho khớp với class Ticket của nhóm nhé)
                    t_id = t.get_ticket_id()
                    st_id = t.get_showtime_id()
                    
                    # Hiển thị trực quan: Mã vé | Mã suất chiếu
                    display_str = f"Mã vé: {t_id} (Suất chiếu: {st_id})"
                    
                    ticket_options.append(display_str)
                    ticket_mapping[display_str] = t_id
                    
                c1, c2 = st.columns([2, 1])
                with c1:
                    # Ô chọn vé thay vì nhập tay
                    selected_ticket_str = st.selectbox("Danh sách vé đã bán:", ticket_options, key="admin_cancel_sel")
                    
                with c2:
                    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                    if st.button("XÁC NHẬN HỦY VÉ", type="primary", use_container_width=True):
                        
                        if selected_ticket_str == "-- Chọn vé cần hủy --":
                            st.warning("Vui lòng chọn một vé từ danh sách!")
                        else:
                            # Lấy lại cái ID thực sự ẩn giấu đằng sau chuỗi hiển thị
                            cancel_ticket_id = ticket_mapping[selected_ticket_str]
                            
                            # Gọi hàm hủy vé dưới tầng Admin Controller
                            success = booking_controller.admin_cancel_ticket(cancel_ticket_id)
                            
                            if success:
                                st.success(f"Đã hủy vé {cancel_ticket_id} và giải phóng ghế thành công!")
                                st.rerun() # Tải lại trang để vé biến mất khỏi danh sách
                            else:
                                st.error("Hủy vé thất bại! Hệ thống không thể giải phóng ghế.")
    # ------------------------------------------
    # B. GIAO DIỆN KHÁCH HÀNG - TRANG CHỦ
    # ------------------------------------------
    elif st.session_state.current_page == 'home':
        
         # 1. LẤY DỮ LIỆU TỪ KHO PHIM VÀ CẤU HÌNH ADMIN
        all_movies = movie_controller.get_movie_data()
        
        # Kiểm tra an toàn nếu cấu hình admin chưa được khởi tạo
        if 'config_slider' not in st.session_state: st.session_state.config_slider = []
        if 'config_list' not in st.session_state: st.session_state.config_list = []
        
        # Lọc phim theo đúng danh sách Admin đã chọn. Nếu Admin chưa chọn gì, lấy mặc định vài phim đầu tiên.
        slider_movies = [m for m in all_movies if m.get_title() in st.session_state.config_slider]
        if not slider_movies and all_movies: slider_movies = all_movies[:3]
            
        display_movies = [m for m in all_movies if m.get_title() in st.session_state.config_list]
        if not display_movies and all_movies: display_movies = all_movies[:8]

        # --- 2. TÍNH NĂNG MỚI: SLIDER ĐỘNG HOÀN TOÀN ---
        st.markdown("<h2 style='text-align: center; color: #5C161B; margin-bottom: 20px; z-index:10; position:relative;'>— TÂM ĐIỂM TUẦN NÀY —</h2>", unsafe_allow_html=True)
        
        if not slider_movies:
            st.info("Hệ thống chưa thiết lập tác phẩm Tâm Điểm.")
        else:
            # Tạo chuỗi HTML chứa nội dung các slide động
            slides_html_content = ""
            for i, m in enumerate(slider_movies):
                active_class = "active" if i == 0 else "" # Slide đầu tiên luôn hiển thị
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

            # Bọc CSS và JS vào chuỗi f-string (những chỗ có ngoặc nhọn {} của CSS/JS phải nhân đôi thành {{}} để không bị lỗi Python)
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

        # --- 3. ĐẶT VÉ NHANH ĐỘNG ---
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

            # Giữ nguyên tỷ lệ 4 cột tuyệt đẹp của cậu
            qb1, qb2, qb3, qb4 = st.columns([2, 1, 1, 1])
            selected_fast_movie = None 

            # ==========================================
            # LUỒNG 1: CHỌN PHIM -> NGÀY -> GIỜ
            # ==========================================
            if booking_mode == "Chọn Phim":
                with qb1:
                    movie_titles = [m.get_title() for m in all_movies] if all_movies else ["Hiện chưa có phim"]
                    selected_title = st.selectbox("1. Chọn Cuộn Phim", ["-- Chọn phim --"] + movie_titles, key="cust_movie_sel_1")
                    
                if selected_title != "-- Chọn phim --" and selected_title != "Hiện chưa có phim":
                    selected_fast_movie = selected_title 
                    selected_movie_id = next((m.get_movie_id() for m in all_movies if m.get_title() == selected_title), None)
                    
                    movie_shows = [s for s in all_showtimes if str(s.get_movie_id()).strip() == str(selected_movie_id).strip()]
                    available_dates = showtime_controller.get_unique_sorted_dates(movie_shows)
                    
                    with qb2:
                        selected_date = st.selectbox("2. Ngày Chiếu", ["-- Chọn ngày --"] + available_dates if available_dates else ["Chưa có lịch"], key="cust_date_sel_1")
                        
                    if selected_date != "-- Chọn ngày --" and selected_date != "Chưa có lịch":
                        date_shows = [s for s in movie_shows if showtime_controller.extract_date(s) == selected_date]
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

            # ==========================================
            # LUỒNG 2: CHỌN NGÀY -> PHIM -> GIỜ (DÙNG HÀM CONTROLLER MỚI)
            # ==========================================
            else: 
                with qb1:
                    all_dates = showtime_controller.get_unique_sorted_dates(all_showtimes)
                    selected_date = st.selectbox("1. Ngày Chiếu", ["-- Chọn ngày --"] + all_dates if all_dates else ["Chưa có lịch"], key="cust_date_sel_2")
                    
                if selected_date != "-- Chọn ngày --" and selected_date != "Chưa có lịch":
                    # Kéo Gói dữ liệu siêu xịn từ controller
                    daily_schedule = showtime_controller.get_schedule_by_date(selected_date, movie_controller)
                    movie_titles = [group["movie"].get_title() for group in daily_schedule]
                    
                    with qb2:
                        selected_title = st.selectbox("2. Chọn Cuộn Phim", ["-- Chọn phim --"] + movie_titles if movie_titles else ["Không có phim"], key="cust_movie_sel_2")
                        
                    if selected_title != "-- Chọn phim --" and selected_title != "Không có phim":
                        selected_fast_movie = selected_title 
                        
                        selected_group = next((g for g in daily_schedule if g["movie"].get_title() == selected_title), None)
                        if selected_group:
                            available_times = showtime_controller.get_unique_sorted_times(selected_group["showtimes"])
                            with qb3:
                                selected_time = st.selectbox("3. Khung Giờ", ["-- Chọn giờ --"] + available_times if available_times else ["Chưa có giờ"], key="cust_time_sel_2")
                    else:
                        with qb3:
                            st.selectbox("3. Khung Giờ", ["-- Chọn giờ --"], key="cust_time_sel_2_empty")
                else:
                    with qb2:
                        st.selectbox("2. Chọn Cuộn Phim", ["-- Chọn phim --"], key="cust_movie_sel_2_empty")
                    with qb3:
                        st.selectbox("3. Khung Giờ", ["-- Chọn giờ --"], key="cust_time_sel_2_empty2")

            # ==========================================
            # NÚT XUẤT VÉ (ĐÃ SỬA: ÉP CHỌN ĐỦ NGÀY GIỜ VÀ LƯU LẠI DỮ LIỆU)
            # ==========================================
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
                        # 👇 Lưu Ngày & Giờ khách vừa chọn vào bộ nhớ tạm để sang phòng vé lôi ra dùng
                        st.session_state.target_date = selected_date
                        st.session_state.target_time = selected_time
                        navigate_to("booking", selected_fast_movie)
                        
            st.markdown('</div>', unsafe_allow_html=True)

        # --- 4. RENDER CÁC CARD PHIM TRÌNH CHIẾU THEO LỰA CHỌN ADMIN ---
        st.markdown("<h2 style='text-align: center; color: #5C161B; margin-top: 40px; margin-bottom: 30px; position:relative; z-index:10;'>— CÁC TÁC PHẨM TRÌNH CHIẾU —</h2>", unsafe_allow_html=True)
        st.markdown('<div class="movie-card-container">', unsafe_allow_html=True)
        

        if not display_movies:
            st.info("Hiện hệ thống chưa thiết lập phim hiển thị tại sảnh. Vui lòng liên hệ Admin.")
        else:
            # Load phim từ danh sách display_movies do Admin cấu hình (chia làm các hàng 4 cột)
            cols = st.columns(4)
            for i, movie in enumerate(display_movies):
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
                if (i + 1) % 4 == 0 and i != (len(display_movies) - 1):
                    st.write("") 
                    cols = st.columns(4)

        st.markdown('</div>', unsafe_allow_html=True)

    # ------------------------------------------
    # C. GIAO DIỆN KHÁCH HÀNG - ĐẶT GHẾ (BOOKING)
    # ------------------------------------------
    elif st.session_state.current_page == 'booking':
        if st.button("TRỞ VỀ SẢNH CHÍNH", type="secondary"): navigate_to("home")
        
        # 👇 THÊM ĐOẠN NÀY VÀO ĐỂ BẮN HIỆU ỨNG KHI MUA XONG
        if st.session_state.get('booking_success', False):
            st.success("🎉 Giao dịch thành công! Chúc quý khách xem phim vui vẻ.")
            show_popcorn_effect()
            st.session_state.booking_success = False # Tắt cờ đi để F5 không bị bắn lại

        selected_movie_title = st.session_state.selected_movie
        st.markdown(f"<h2 style='color:#5C161B;'>XUẤT VÉ: {selected_movie_title}</h2>", unsafe_allow_html=True)
   
        # Tìm phim tương ứng
        movie_node = movie_controller.search_by_title(selected_movie_title)
        if movie_node is None:
            st.error("Không tìm thấy dữ liệu của phim này trong kho!")
        else:
            m_data = movie_node.get_data()
            
            # --- ĐÃ SỬA: LẤY CHÍNH XÁC SUẤT CHIẾU THEO NGÀY GIỜ Ở SẢNH ---
            target_date = st.session_state.get('target_date')
            target_time = st.session_state.get('target_time')
            
            st_data = None
            if target_date and target_time:
                # Gọi hàm tìm chính xác suất chiếu
                st_data = showtime_controller.find_exact_showtime(
                    m_data.get_movie_id(), target_date, target_time
                )
            else:
                # Đề phòng lỗi (khách F5 mất session), lôi tạm lịch đầu tiên ra
                showtimes = showtime_controller.get_showtime_data()
                st_data = next((s for s in showtimes if s.get_movie_id() == m_data.get_movie_id()), None)
            
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
                        
                        # ==========================================
                        # LOGIC ĐỔI MÀU GHẾ MỚI CỦA M NẰM Ở ĐÂY
                        # ==========================================
                        status = seat_matrix.check_status(r, c)
                        is_selected = seat_name in st.session_state.selected_seats
                        
                        # Ghế BỊ XÁM khi: Đã mua (BOOKED) HOẶC Đang bị NGƯỜI KHÁC giữ chỗ (RESERVED)
                        is_unavailable = (status == SeatStatus.BOOKED) or (status == SeatStatus.RESERVED and not is_selected)
                        
                        with cols_st[c]:
                            if is_unavailable:
                                st.button(seat_name, key=f"seat_{seat_name}", disabled=True, use_container_width=True)
                            else:
                                btn_type = "primary" if is_selected else "secondary"
                                # Không gán disabled lúc đang thanh toán để ghế không bị chuyển xám oan uổng
                                if st.button(seat_name, key=f"seat_{seat_name}", type=btn_type, use_container_width=True):
                                    
                                    if st.session_state.get('payment_step', False):
                                        # Bật khiên cấm đổi ghế lúc đang có mã QR
                                        st.toast("Đang trong quá trình thanh toán, không thể đổi ghế!", icon="⚠️")
                                    else:
                                        if is_selected: st.session_state.selected_seats.remove(seat_name)
                                        else: st.session_state.selected_seats.append(seat_name)
                                        st.rerun() 
                                    
                st.divider()

                num_selected = len(st.session_state.selected_seats)
                base_price = m_data.get_base_price()
                total_price = num_selected * base_price
                
                col_sum1, col_sum2 = st.columns([3, 1])
                with col_sum1:
                    st.markdown(f"**Vị trí đã chọn:** {', '.join(st.session_state.selected_seats) if num_selected > 0 else 'Chưa chọn'}")
                    st.markdown(f"**Tổng Lệ phí:** <span style='color:#5C161B; font-size: 1.2rem; font-weight:bold;'>{total_price:,.0f} VNĐ</span>", unsafe_allow_html=True)
                
                # --- KHỞI TẠO BIẾN TRẠNG THÁI THANH TOÁN ---
                if "payment_step" not in st.session_state:
                    st.session_state.payment_step = False

                import time # Import thư viện thời gian để đếm ngược
                
                # =========================================================
                # NÚT THANH TOÁN - ĐÃ SỬA LỖI VÉ MA (ATOMIC TRANSACTION)
                # =========================================================
                with col_sum2:
                    if not st.session_state.payment_step:
                        if st.button("THANH TOÁN", type="primary", use_container_width=True, disabled=(num_selected==0), key="btn_thanh_toan"):
                            
                            # 1. Gom tất cả ghế đang chọn thành tọa độ số
                            seats_to_book = []
                            for seat in st.session_state.selected_seats:
                                r = ord(seat[0].upper()) - 65
                                c = int(seat[1:]) - 1
                                seats_to_book.append((r, c))
                            
                            try:
                                # 2. Gọi hàm đặt vé 1 lần duy nhất cho cả cụm ghế
                                ticket_ids = booking_controller.process_booking(
                                    st.session_state.user_obj,
                                    m_data,
                                    st_data,
                                    seats_to_book
                                )

                                # 3. Xử lý kết quả trực tiếp bên trong khối try (Thay thế khối kiểm tra cũ)
                                if ticket_ids: # Nếu list mã vé không rỗng -> Thành công!
                                    st.session_state.generated_ticket_ids = ticket_ids 
                                    st.session_state.payment_step = True
                                    st.session_state.payment_start_time = time.time()
                                    st.rerun()
                                else:
                                    st.error("Thao tác thất bại! Một hoặc nhiều ghế bạn chọn vừa bị người khác mua mất cách đây vài giây. Vui lòng chọn ghế khác.")
                            
                            except Exception as e:
                                st.error(f"Lỗi hệ thống: {e}")
                            
                # =========================================================
                # 2. MÀN HÌNH MÃ QR & ĐẾM NGƯỢC 5 PHÚT (BẢN BẢO MẬT SVG ONLOAD)
                # =========================================================
                if st.session_state.payment_step:
                    st.write("---")
                    
                    # Tính thời gian trôi qua (bằng giây)
                    elapsed_time = time.time() - st.session_state.payment_start_time
                    time_left = 300 - int(elapsed_time) # 300 giây = 5 phút chuẩn chỉnh
                    
                    if time_left > 0:
                        st.markdown("<h4 style='text-align: center; color: #5C161B;'>Vui lòng quét mã QR dưới đây để hoàn tất thanh toán</h4>", unsafe_allow_html=True)
                        # Sử dụng SVG Onload để ép trình duyệt phải chạy bộ đếm ngược không bị chặn
                        # Sử dụng components.html để tạo iframe chạy độc lập, cam kết đếm ngược mượt mà 100%
                        countdown_html = f"""
                        <div id="countdown-box" style="text-align: center; padding: 12px; background-color: #fff3cd; color: #856404; border-radius: 8px; border: 1px solid #ffeeba; font-family: monospace;">
                            <h3 style="margin: 0; font-size: 22px;">⏳ Thời gian giữ ghế: <span id="timer" style="color:#dc3545; font-weight:bold;">{time_left // 60}:{time_left % 60:02d}</span></h3>
                            <p style="margin: 0; font-size: 14px; margin-top: 5px;">Quá 5 phút, hệ thống sẽ tự động hủy giao dịch và giải phóng ghế!</p>
                        </div>
                        
                        <script>
                            let secondsLeft = {time_left};
                            const timerDisplay = document.getElementById('timer');
                            const boxDisplay = document.getElementById('countdown-box');
                            
                            const countdownInterval = setInterval(function() {{
                                secondsLeft--;
                                if (secondsLeft <= 0) {{
                                    clearInterval(countdownInterval);
                                    timerDisplay.innerHTML = "0:00";
                                    boxDisplay.style.backgroundColor = "#f8d7da";
                                    boxDisplay.style.color = "#721c24";
                                    boxDisplay.style.borderColor = "#f5c6cb";
                                    // Ép trang chính tải lại để Python nhận diện hết hạn và giải phóng ghế lập tức
                                    window.parent.location.reload();
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
                                if time.time() - st.session_state.payment_start_time <= 300:
                                    
                                    # 👇 GỌI HÀM XỬ LÝ THEO CỤM SIÊU TỐC THAY CHO VÒNG LẶP CŨ:
                                    booking_controller.confirm_bookings_bulk(st.session_state.get('generated_ticket_ids', []))
                                        
                                    st.session_state.booking_success = True
                                    
                                    # Làm sạch giỏ hàng và đặt lại các biến trạng thái
                                    st.session_state.selected_seats = []
                                    st.session_state.generated_ticket_ids = []
                                    st.session_state.payment_step = False
                                    
                                    booking_controller.refresh_booking_data()
                                    st.rerun()
                    
                    else:
                        # =========================================================
                        # 3. QUÁ 5 PHÚT -> TỰ ĐỘNG HỦY VÉ KHÁCH HÀNG
                        # =========================================================
                        st.error("ĐÃ QUÁ THỜI GIAN THANH TOÁN!")
                        
                        # Gọi hàm tự động quét và giải phóng vé quá hạn của Controller (Set timeout = 5 phút)
                        booking_controller.cleanup_unfinished_reservations(timeout_minutes=5)
                        
                        st.warning("Hệ thống đã tự động Hủy giao dịch và hoàn trống ghế thành công!")
                        
                        st.session_state.selected_seats = []
                        st.session_state.payment_step = False
                        
                        if st.button("Bắt đầu đặt lại"):
                            st.rerun()

    # ------------------------------------------
    # D. GIAO DIỆN KHÁCH HÀNG - LỊCH SỬ VÉ
    # ------------------------------------------
    elif st.session_state.current_page == 'history':
        if st.button("TRỞ VỀ SẢNH CHÍNH", type="secondary"): navigate_to("home")
        st.markdown("<h2 style='color:#5C161B;'>BỘ SƯU TẬP VÉ</h2>", unsafe_allow_html=True)
        
        # Lấy dữ liệu lịch sử từ Linked List Ticket
        history_list = booking_controller.get_booking_history(st.session_state.user_obj.get_user_id())
        
        if not history_list:
            st.info("Quý khách chưa sở hữu vé nào trong kho lưu trữ.")
        else:
            data = []
            for ticket in history_list:
                m_node = movie_controller.search_by_id(ticket.get_movie_id())
                m_title = m_node.get_data().get_title() if m_node else "Phim không xác định"
                
                data.append({
                    "Mã Vé": ticket.get_ticket_id(),
                    "Tên Phim": m_title,
                    "Ghế": ticket.get_seat_id(),
                    "Lệ phí": f"{ticket.get_price():,.0f} đ",
                    "Trạng thái": ticket.get_status()
                })
                
            df_history = pd.DataFrame(data)
            st.dataframe(df_history, use_container_width=True, hide_index=True)

    # ==========================================
    # 7. QUẢNG CÁO POPUP
    # ==========================================
    if not st.session_state.ad_closed and st.session_state.current_page == 'home' and st.session_state.user_role != 'admin':
        show_advertisement()

except Exception as e:
    st.error(f"Lỗi: {type(e).__name__}")
    st.exception(e)