import streamlit as st
import pandas as pd
import random
import streamlit.components.v1 as components

# Import các Controllers và Models của bạn
from models.entities import SeatStatus, MovieData
from data_structures.file_io import FileIOHandler
from controllers.auth_controller import AuthController
from controllers.movie_controller import MovieController
from controllers.booking_controller import BookingController
from controllers.showtime_controller import ShowtimeController
from controllers.room_controller import RoomController
from controllers.admin_controller import AdminController

# ==========================================
# 1. CẤU HÌNH TRANG
# ==========================================
st.set_page_config(
    page_title="Sunnyx Cinema | Classic & Modern",
    page_icon="🎞️",
    layout="wide",
    initial_sidebar_state="expanded" 
)

# ==========================================
# 2. KHỞI TẠO TRẠNG THÁI (SESSION STATE) & CONTROLLERS
# ==========================================
if 'ad_closed' not in st.session_state: st.session_state.ad_closed = False
if 'is_logged_in' not in st.session_state: st.session_state.is_logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = 'guest'
if 'username' not in st.session_state: st.session_state.username = ''
if 'user_obj' not in st.session_state: st.session_state.user_obj = None # Lưu Object người dùng thật
if 'current_page' not in st.session_state: st.session_state.current_page = 'home'
if 'selected_movie' not in st.session_state: st.session_state.selected_movie = ''
if 'selected_seats' not in st.session_state: st.session_state.selected_seats = []
if 'config_slider' not in st.session_state: st.session_state.config_slider= []
if 'config_list' not in st.session_state: st.session_state.config_list = []

# Khởi tạo Controllers một lần duy nhất lưu vào Session State
if 'io_handler' not in st.session_state:
    io_handler = FileIOHandler()
    st.session_state.io_handler = io_handler
    
    st.session_state.auth_ctrl = AuthController(io_handler)
    st.session_state.movie_ctrl = MovieController(io_handler)
    st.session_state.showtime_ctrl = ShowtimeController(io_handler)
    st.session_state.room_ctrl = RoomController(io_handler)
    st.session_state.booking_ctrl = BookingController(io_handler, st.session_state.showtime_ctrl, st.session_state.movie_ctrl)
    st.session_state.admin_ctrl = AdminController(st.session_state.movie_ctrl, st.session_state.booking_ctrl)

# Gán biến để gõ cho ngắn gọn trong file này
auth_controller = st.session_state.auth_ctrl
movie_controller = st.session_state.movie_ctrl
showtime_controller = st.session_state.showtime_ctrl
room_controller = st.session_state.room_ctrl
booking_controller = st.session_state.booking_ctrl
admin_controller = st.session_state.admin_ctrl

# ==========================================
# 3. HÀM CHUYỂN TRANG & POPUP QUẢNG CÁO
# ==========================================
def navigate_to(page, movie=""):
    st.session_state.current_page = page
    if movie: 
        st.session_state.selected_movie = movie
        st.session_state.selected_seats = [] 
    st.rerun()

@st.dialog("SIÊU PHẨM MÙA HÈ TẠI SUNNYX", width="large")
def show_advertisement():
    st.markdown("<h3 style='text-align: center; color: #73171F; margin-top:0; font-family: \"Playfair Display\", serif;'>BOM TẤN ĐÃ ĐỔ BỘ</h3>", unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?q=80&w=2070", use_column_width=True)
    st.markdown("<p style='text-align:center; color:#555; margin-top: 15px; font-style: italic;'>Mua vé liền tay, nhận ngay bắp nước miễn phí!</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✖ ĐÓNG QUẢNG CÁO", type="primary", use_container_width=True):
            st.session_state.ad_closed = True
            st.rerun()

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
/* --- VŨ KHÍ HỦY DIỆT: ÉP PHÔNG CHỮ NHỎ LẠI VÀ XÓA LỀ --- */
    
    /* Ép tất cả các nút phụ (ghế) phải mỏng dính */
    button[kind="secondary"] {
        padding: 0px !important;
        min-height: 35px !important;
    }
    
    /* Xuyên thủng vào lớp thẻ <p> bên trong nút */
    button[kind="secondary"] p {
        white-space: nowrap !important;
        word-break: keep-all !important;
        font-size: 0.65rem !important; /* Thu nhỏ cỡ chữ mức tối đa để vừa cột */
        letter-spacing: -0.5px !important; /* Kéo các chữ cái sát lại nhau */
        margin: 0 !important;
    }   

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="bg-decoration gear-1">⚙</div><div class="bg-decoration gear-2">⚙</div><div class="bg-decoration gear-3">⚙</div>', unsafe_allow_html=True)

# ==========================================
# 5. SIDEBAR: ĐĂNG NHẬP
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #5C161B; font-family: \"Playfair Display\", serif;'>🗝️ PHÒNG VÉ</h2>", unsafe_allow_html=True)
    
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
            if st.button("🏠 Sảnh Chính", use_container_width=True): navigate_to("home")
            if st.button("🎫 Vé Của Tôi", use_container_width=True): navigate_to("history")
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
if st.session_state.user_role == 'admin':
    st.markdown("<h2 style='color:#5C161B;'>⚙️ PHÒNG ĐIỀU HÀNH KỸ THUẬT</h2>", unsafe_allow_html=True)
    st.info("Khu vực dành riêng cho Quản đốc rạp (Admin).")
    
    # Hiển thị Metric
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tổng Doanh thu", f"{admin_controller.calculate_revenue():,.0f} đ")
    c2.metric("Vé xuất ra", f"{admin_controller.count_tickets()} vé")
    c3.metric("Phim trình chiếu", f"{admin_controller.count_movies()} cuộn")
    c4.metric("Thành viên hệ thống", f"{len(auth_controller.get_all_users())} người")
    st.divider()
    
    # Chia Tab cho Admin
    tab_manage, tab_display, tab_top = st.tabs(["Quản Lý Phim", "Cấu Hình Giao Diện", "Top Doanh Thu"])
    
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
                        if movie_controller.add_movie(new_movie):
                            st.success(f"Đã thêm siêu phẩm '{new_title}' thành công!")
                            st.rerun()
                        else:
                            st.error("Lỗi: Phim đã tồn tại trong kho!")

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
                
                st.error(f"⚠️ Cảnh báo: Bạn sắp xóa cuộn phim **{del_movie_title}**. Thao tác này không thể hoàn tác.")
                if st.button("XÁC NHẬN XÓA", type="primary"):
                    if movie_controller.delete_movie(del_movie.get_movie_id(), showtime_controller):
                        st.success(f"Đã dọn dẹp '{del_movie_title}' khỏi kho!")
                        st.rerun()
                    else:
                        st.error("Không thể xóa! Phim này đang có suất chiếu hoạt động hoặc khách đã mua vé.")

    # TAB: CẤU HÌNH HIỂN THỊ TRANG CHỦ
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
    # TAB 2: TOP DOANH THU
    with tab_top: 
        top_movies = admin_controller.get_top_movies_by_revenue()
        if top_movies:
            for m in top_movies:
                st.markdown(f"**🎞️ {m.get_title()}** | Sinh lời: <span style='color:#5C161B; font-weight:bold;'>{m.get_revenue():,.0f} đ</span>", unsafe_allow_html=True)
                st.caption(f"Thể loại: {m.get_genre()} | Thời lượng: {m.get_duration()} phút")
                st.divider()
        else:
            st.write("Chưa có dữ liệu phim.")



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
    # Lấy toàn bộ tên phim để khách có thể mua bất kỳ phim nào trong kho (không chỉ những phim đang hiển thị)
    movie_titles = [m.get_title() for m in all_movies] if all_movies else ["Hiện chưa có phim"]
    
    with st.container():
        st.markdown('<div class="vintage-ticket"><div class="ticket-title">🎟️ QUẦY BÁN VÉ NHANH</div>', unsafe_allow_html=True)
        qb1, qb2, qb3, qb4 = st.columns([2, 1, 1, 1])
        
        # 1. Khách hàng chọn phim
        with qb1: 
            selected_fast_movie = st.selectbox("Chọn Cuộn Phim", movie_titles)
            
        # --- BƯỚC MỚI: TÌM MÃ ID TỪ TÊN PHIM ---
        selected_movie_id = None
        movies_list = movie_controller.get_movie_data() # Kéo danh sách phim về
        
        for m in movies_list:
            # (Lưu ý: Nếu class Movie của nhóm bạn dùng hàm get_name() thay vì get_title() thì bạn sửa lại nhé)
            if m.get_title() == selected_fast_movie: 
                selected_movie_id = m.get_movie_id()
                break
                
        # 2. Gọi Controller để lấy lịch chiếu thô (Truyền ID vào thay vì truyền Tên)
        movie_showtimes = showtime_controller.get_showtimes_by_movie(selected_movie_id)
        
        # 3. Bóc tách và "làm sạch" dữ liệu Ngày/Giờ từ start_time
        available_dates = []
        available_times = []
        
        if movie_showtimes:
            for s in movie_showtimes:
                # Gọi đúng tên hàm get_start_time() và chém bay mọi loại ngoặc, nháy
                raw_data = str(s.get_start_time()).replace("[", "").replace("]", "").replace("'", "").replace('"', "")
                
                # Tách ra nếu có nhiều lịch bị dính chùm bằng dấu phẩy
                show_items = [item.strip() for item in raw_data.split(",") if item.strip()]
                
                for item in show_items:
                    # item lúc này sẽ có dạng "2024-05-20 09:30"
                    if " " in item:
                        # Cắt đôi chuỗi tại vị trí khoảng trắng đầu tiên
                        parts = item.split(" ", 1) 
                        available_dates.append(parts[0]) # Nửa đầu là Ngày
                        available_times.append(parts[1]) # Nửa sau là Giờ
                    else:
                        # Đề phòng dữ liệu bị lỗi thiếu khoảng trắng
                        available_dates.append(item)
                        available_times.append(item)
                
            # Lọc trùng lặp và sắp xếp lại cho đẹp
            available_dates = sorted(list(set(available_dates)))
            available_times = sorted(list(set(available_times)))
        else:
            available_dates = ["Chưa có lịch chiếu"]
            available_times = ["Chưa có khung giờ"]

        # 4. Hiển thị lên giao diện
        with qb2: 
            st.selectbox("Ngày Chiếu", available_dates) 
        with qb3: 
            st.selectbox("Khung Giờ", available_times)
        with qb4: 
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button("XUẤT VÉ", type="primary", use_container_width=True):
                if not st.session_state.is_logged_in:
                    st.error("⚠️ Xuất trình thẻ thành viên (Đăng nhập)!")
                elif selected_fast_movie == "Hiện chưa có phim":
                    st.error("Rạp đang bảo trì phim!")
                else:
                    navigate_to("booking", selected_fast_movie)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 4. RENDER CÁC CARD PHIM TRÌNH CHIẾU THEO LỰA CHỌN ADMIN ---
    st.markdown("<h2 style='text-align: center; color: #5C161B; margin-top: 40px; margin-bottom: 30px; position:relative; z-index:10;'>— CÁC TÁC PHẨM TRÌNH CHIẾU —</h2>", unsafe_allow_html=True)
    st.markdown('<div class="movie-card-container">', unsafe_allow_html=True)
    
    def create_premium_movie_card(col, title, genre, duration, price, img_url):
        with col:
            with st.container():
                st.markdown(f"""
                <div class="img-wrapper"><img src="{img_url if img_url else 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&q=80'}"></div>
                <div class="content-container">
                    <p class="movie-title">{title}</p>
                    <p class="movie-info-text"><b>Thể loại:</b> {genre}</p>
                    <p class="movie-info-text"><b>Độ dài:</b> {duration} phút</p>
                    <p class="movie-info-text" style="color: #D4AF37; font-weight: bold;">Lệ phí: {price:,.0f} đ</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🎟️ MUA VÉ", key=f"btn_{title}", use_container_width=True, type="primary"):
                    if not st.session_state.is_logged_in:
                        st.error(f"⚠️ Vui lòng đăng nhập để đặt vé!")
                    else:
                        navigate_to("booking", title)

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
    if st.button("⬅TRỞ VỀ SẢNH CHÍNH", type="secondary"): navigate_to("home")
    
    selected_movie_title = st.session_state.selected_movie
    st.markdown(f"<h2 style='color:#5C161B;'>🎫 XUẤT VÉ: {selected_movie_title}</h2>", unsafe_allow_html=True)
    
    # Tìm phim tương ứng
    movie_node = movie_controller.search_by_title(selected_movie_title)
    if movie_node is None:
        st.error("Không tìm thấy dữ liệu của phim này trong kho!")
    else:
        m_data = movie_node.get_data()
        
        # Tìm lịch chiếu (Lấy lịch chiếu đầu tiên khớp với movie_id)
        showtimes = showtime_controller.get_showtime_data()
        st_data = next((s for s in showtimes if s.get_movie_id() == m_data.get_movie_id()), None)
        
        if st_data is None:
            st.warning("⚠️ Rạp chưa mở khung giờ chiếu nào cho tác phẩm này. Vui lòng quay lại sau!")
        else:
            st.info(f"📍 Địa điểm: Sunnyx Vintage Cinema | 🎬 Phòng: {st_data.get_room_id()} | ⏰ Giờ chiếu: {st_data.get_start_time()}")
            st.markdown('<div class="seat-screen">MÀN CHIẾU BẠC</div>', unsafe_allow_html=True)
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
                    # Check status (0 là EMPTY theo Entities)
                    is_booked = (seat_matrix.check_status(r, c) != SeatStatus.EMPTY)
                    
                    with cols_st[c]:
                        if is_booked:
                            st.button(seat_name, key=f"seat_{seat_name}", disabled=True, use_container_width=True)
                        else:
                            is_selected = seat_name in st.session_state.selected_seats
                            btn_type = "primary" if is_selected else "secondary"
                            if st.button(seat_name, key=f"seat_{seat_name}", type=btn_type, use_container_width=True):
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
            
            # 1. TRONG CỘT BÊN PHẢI: Chỉ tạo nút bấm và gán vào một biến
            with col_sum2:
                # Lưu ý: gán nút bấm vào biến dat_ve_xong
                dat_ve_xong = st.button("TRẢ TIỀN & NHẬN VÉ", type="primary", use_container_width=True, disabled=(num_selected==0))

            # =========================================================
            # 2. LÙI LỀ RA NGOÀI CÙNG (Thẳng hàng với chữ `with col_sum2:`)
            # =========================================================
            if dat_ve_xong:
                success_count = 0
                for seat in st.session_state.selected_seats:
                    # (Đoạn code tách r, c và process_booking của bạn giữ nguyên ở đây)
                    r = ord(seat[0]) - 65
                    c = int(seat[1:]) - 1
                    
                    if booking_controller.process_booking(st.session_state.user_obj, m_data, st_data, r, c, movie_controller):
                        success_count += 1
                        
                if success_count == len(st.session_state.selected_seats):
                    st.success("🎉 Giao dịch thành công! Chúc quý khách xem phim vui vẻ.")
                    
                    # --- BẮT ĐẦU ĐOẠN HIỂN THỊ MÃ QR TRÀN MÀN HÌNH ---
                    st.write("---")
                    st.markdown("<h4 style='text-align: center; color: #5C161B;'>Vui lòng quét mã QR dưới đây để hoàn tất thanh toán</h4>", unsafe_allow_html=True)
                    
                    # Chia 3 cột đều nhau trên toàn màn hình, nhét ảnh vào cột giữa
                    col_qr1, col_qr2, col_qr3 = st.columns([1, 1, 1]) 
                    with col_qr2:
                        st.image("https://i.postimg.cc/zXCdCsg3/image.png", use_container_width=True)
                    # --- KẾT THÚC ĐOẠN HIỂN THỊ MÃ QR ---

                    st.session_state.selected_seats = []           
                else:
                    st.error("⚠️ Có lỗi xảy ra hoặc ghế đã bị người khác giành mất!")
# ------------------------------------------
# D. GIAO DIỆN KHÁCH HÀNG - LỊCH SỬ VÉ
# ------------------------------------------
elif st.session_state.current_page == 'history':
    if st.button("⬅TRỞ VỀ SẢNH CHÍNH", type="secondary"): navigate_to("home")
    st.markdown("<h2 style='color:#5C161B;'>🎫 BỘ SƯU TẬP VÉ</h2>", unsafe_allow_html=True)
    
    # Lấy dữ liệu lịch sử từ Linked List Ticket
    history_list = booking_controller.get_booking_history(st.session_state.user_obj.get_user_id())
    
    if not history_list:
        st.info("Quý khách chưa sở hữu vé nào trong kho lưu trữ.")
    else:
        data = []
        for ticket in history_list:
            # Truy vấn tên phim dựa trên movie_id
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