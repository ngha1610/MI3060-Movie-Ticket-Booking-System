import streamlit as st
import datetime
import plotly.graph_objects as go
from models.entities import MovieData, Showtime
from controllers.auth_controller import AuthController
from controllers.movie_controller import MovieController
from controllers.showtime_controller import ShowtimeController
from controllers.booking_controller import BookingController
from controllers.admin_controller import AdminController
from controllers.room_controller import RoomController
from data_structures.file_io import FileIOHandler

# =====================================================
# INITIALIZATION & CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="Sunnyx Cinema",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "io_handler" not in st.session_state:
    st.session_state.io_handler = FileIOHandler()
    st.session_state.movie_ctrl = MovieController(st.session_state.io_handler)
    st.session_state.room_ctrl = RoomController(st.session_state.io_handler)
    st.session_state.showtime_ctrl = ShowtimeController(st.session_state.io_handler)
    st.session_state.booking_ctrl = BookingController(st.session_state.io_handler, st.session_state.showtime_ctrl, st.session_state.movie_ctrl)
    st.session_state.auth_ctrl = AuthController(st.session_state.io_handler)
    st.session_state.admin_ctrl = AdminController(st.session_state.movie_ctrl, st.session_state.booking_ctrl)

if "auth_view" not in st.session_state:
    st.session_state.auth_view = None  
if "selected_movie_id" not in st.session_state:
    st.session_state.selected_movie_id = None
if "selected_showtime_id" not in st.session_state:
    st.session_state.selected_showtime_id = None
if "current_selected_seats" not in st.session_state:
    st.session_state.current_selected_seats = []
if "search_keyword" not in st.session_state:
    st.session_state.search_keyword = ""

# =====================================================
# THEME INJECTION (LIGHT THEME & CGV SEATS FLAT)
# =====================================================
def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        
        .stApp {
            background: #F9F7F1 !important;
            color: #2D3748 !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        
        [style*="color:#FFFFFF"], [style*="color:#FFF"], [style*="color: #FFFFFF"], [style*="color: #FFF"],
        [style*="color:#A0A0A5"], [style*="color:#DEE2E6"] {
            color: #2D3748 !important; 
        }
        
        #MainMenu, header, footer {visibility: hidden;}
        .block-container {padding-top: 1rem !important; padding-bottom: 5rem !important;}
        
        section[data-testid="stSidebar"] {
            background: #FFFFFF !important;
            border-right: 1px solid #E2E8F0;
        }
        
        .navbar-container {
            display: flex; justify-content: space-between; align-items: center;
            padding: 18px 40px; margin-bottom: 35px;
            background: #FFFFFF;
            border-bottom: 1px solid #E2E8F0;
            border-radius: 0 0 24px 24px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        .navbar-logo {
            font-size: 28px; font-weight: 800; letter-spacing: 2px;
            color: #E53935;
        }
        
        .movie-card, .metric-card, .auth-overlay {
            background: #FFFFFF !important;
            border-radius: 12px;
            border: 1px solid #E2E8F0 !important;
            overflow: hidden; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important;
        }
        .poster-wrapper { width: 100%; height: 380px; background-size: cover; background-position: center; }
        
        .movie-info { 
            padding: 20px; 
            background: #FFFFFF; 
            height: 180px; 
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .movie-title { 
            font-size: 19px; 
            font-weight: 700; 
            margin-bottom: 6px; 
            color: #2D3748 !important; 
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .stButton > button {
            background: #E53935 !important;
            color: #FFFFFF !important; border: none !important;
            padding: 10px 24px !important; border-radius: 8px !important; font-weight: 600 !important;
        }
        .stButton > button:hover { background: #D32F2F !important; }
        
        div.sec-btn > .stButton > button {
            background: #FFFFFF !important; border: 1px solid #CBD5E0 !important; color: #4A5568 !important;
        }

        div[data-baseweb="input"], div[data-baseweb="textarea"] {
            background-color: #FFFFFF !important;
            border: 1px solid #CBD5E0 !important;
            border-radius: 8px !important;
        }
        
        /* GHẾ PHẲNG CGV: KHÔNG BO GÓC, NẰM SÁT NHAU */
        div.seat-empty > .stButton > button,
        div.seat-selected > .stButton > button,
        div.seat-booked > .stButton > button {
            border-radius: 0px !important;
            margin: 0px !important;
            padding: 0px !important;
            height: 40px !important;
            width: 100% !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: none !important;
        }
        
        div.seat-empty > .stButton > button {
            background: #F7FAFC !important; 
            color: #4A5568 !important; 
            border: 1px solid #CBD5E0 !important;
        }
        div.seat-empty > .stButton > button:hover {
            background: #E53935 !important;
            color: #FFFFFF !important;
            border-color: #E53935 !important;
        }
        div.seat-selected > .stButton > button {
            background: #E53935 !important; 
            color: #FFFFFF !important;
            border: 1px solid #E53935 !important;
        }
        div.seat-booked > .stButton > button {
            background: #555555 !important; 
            color: #FFFFFF !important; 
            border: 1px solid #555555 !important; 
            pointer-events: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

# =====================================================
# MODULAR RENDER FUNCTIONS
# =====================================================
def render_navbar():
    is_logged = st.session_state.auth_ctrl.is_logged_in()
    user_label = f"Xin chào, {st.session_state.auth_ctrl.get_current_user().get_username()}" if is_logged else "Khách tham quan"
    
    st.markdown(f"""
        <div class="navbar-container">
            <div class="navbar-logo">SUNNYX CINEMA</div>
            <div style="display: flex; gap: 20px; align-items: center;">
                <span style="color: #4A5568; font-size: 15px; font-weight: 600;">
                    {user_label}
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_metric_dashboard():
    total_movies = st.session_state.admin_ctrl.count_movies()
    total_tickets = st.session_state.admin_ctrl.count_tickets()
    total_revenue = st.session_state.admin_ctrl.calculate_revenue()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card" style="padding:20px; text-align:center;"><div style="font-size:32px; font-weight:700; color:#E53935;">{total_movies}</div><div style="color:#718096; font-size:12px; font-weight:600;">TỔNG PHIM HỆ THỐNG</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card" style="padding:20px; text-align:center;"><div style="font-size:32px; font-weight:700; color:#E53935;">{total_tickets}</div><div style="color:#718096; font-size:12px; font-weight:600;">VÉ ĐÃ BÁN RA</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card" style="padding:20px; text-align:center;"><div style="font-size:32px; font-weight:700; color:#E53935;">{total_revenue:,.0f} VNĐ</div><div style="color:#718096; font-size:12px; font-weight:600;">DOANH THU TÍCH LŨY</div></div>', unsafe_allow_html=True)

def render_homepage():
    st.markdown("<h3 style='font-weight:700; color:#2D3748;'>PHIM ĐANG CHIẾU TẠI RẠP</h3>", unsafe_allow_html=True)
    
    col_search, col_filter = st.columns([2, 1])
    with col_search:
        st.session_state.search_keyword = st.text_input("Tìm kiếm phim", placeholder="Nhập tên bộ phim bạn muốn tìm...", label_visibility="collapsed")
    with col_filter:
        genre_filter = st.selectbox("Thể loại", ["Tất cả thể loại", "Hành động", "Kinh dị", "Tình cảm", "Hoạt hình"], label_visibility="collapsed")

    movies = st.session_state.movie_ctrl.get_movie_data()
    if st.session_state.search_keyword:
        movies = [m for m in movies if st.session_state.search_keyword.lower() in m.get_title().lower()]
    if genre_filter != "Tất cả thể loại":
        movies = [m for m in movies if genre_filter.lower() in m.get_genre().lower()]

    if not movies:
        st.info("Không tìm thấy bộ phim nào phù hợp.")
    else:
        cols_per_row = 4
        for i in range(0, len(movies), cols_per_row):
            chunk = movies[i:i+cols_per_row]
            columns = st.columns(cols_per_row)
            for idx, movie in enumerate(chunk):
                with columns[idx]:
                    poster = movie.get_poster_path() if movie.get_poster_path() else "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=600"
                    
                    st.markdown(f"""
                        <div class="movie-card">
                            <div class="poster-wrapper" style="background-image: url('{poster}');"></div>
                            <div class="movie-info">
                                <div>
                                    <div class="movie-title">{movie.get_title()}</div>
                                    <div style="font-size: 13px; color: #718096; margin-bottom: 8px;">{movie.get_genre()} | {movie.get_duration()} phút</div>
                                </div>
                                <div style="font-size: 16px; color: #E53935; font-weight: 700;">{movie.get_base_price():,.0f} VNĐ</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("Đặt Vé Ngay", key=f"book_home_{movie.get_movie_id()}", use_container_width=True):
                        if not st.session_state.auth_ctrl.is_logged_in():
                            st.warning("Bạn cần đăng nhập tài khoản để đặt vé.")
                        else:
                            st.session_state.selected_movie_id = movie.get_movie_id()
                            st.session_state.selected_showtime_id = None
                            st.rerun()

def render_seat_layout(showtime, movie):
    matrix = showtime.get_seat_matrix()
    
    st.markdown("<h3 style='text-align:center; color:#2D3748; margin-top: 10px;'>SƠ ĐỒ PHÒNG CHIẾU CGV</h3>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="max-width: 60%; margin: 10px auto 25px auto; text-align: center;">
            <div style="height: 5px; background: #E53935; border-radius: 2px; margin-bottom: 6px;"></div>
            <div style="font-size: 11px; color: #718096; font-weight:700; letter-spacing: 3px;">MÀN HÌNH CHÍNH</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="display: flex; justify-content: center; gap: 40px; margin-bottom: 25px; font-size:13px; font-weight:600; color:#4A5568;">
            <div style="display:flex; align-items:center;"><div style="width:16px; height:16px; background:#F7FAFC; border:1px solid #CBD5E0; margin-right:8px;"></div>Ghế trống</div>
            <div style="display:flex; align-items:center;"><div style="width:16px; height:16px; background:#E53935; margin-right:8px;"></div>Đang chọn</div>
            <div style="display:flex; align-items:center;"><div style="width:16px; height:16px; background:#555555; margin-right:8px;"></div>Đã bán (X)</div>
        </div>
    """, unsafe_allow_html=True)
    
    num_rows = matrix._rows
    num_cols = matrix._cols
    
    # CĂN CHỈNH RA GIỮA TOÀN BỘ SƠ ĐỒ GHẾ
    _, seat_center_block, _ = st.columns([1, 4, 1])
    
    with seat_center_block:
        for r in range(num_rows):
            row_label = chr(65 + r)
            # Dùng gap="none" để các nút ghế dính sát liền nhau phẳng lỳ
            cols = st.columns([1] + [2] * num_cols, gap="none")
            
            with cols[0]:
                st.markdown(f"<p style='text-align:center; line-height:40px; margin:0; color:#4A5568; font-weight:bold;'>{row_label}</p>", unsafe_allow_html=True)
            
            for c in range(num_cols):
                seat_id = f"{row_label}{c+1}"
                is_available = st.session_state.showtime_ctrl.check_seat_status(showtime.get_showtime_id(), r, c)
                
                if not is_available:
                    seat_class = "seat-booked"
                    btn_label = "X"
                elif seat_id in st.session_state.current_selected_seats:
                    seat_class = "seat-selected"
                    btn_label = seat_id
                else:
                    seat_class = "seat-empty"
                    btn_label = seat_id
                    
                with cols[c+1]:
                    st.markdown(f'<div class="{seat_class}">', unsafe_allow_html=True)
                    if st.button(btn_label, key=f"seat_matrix_{r}_{c}", use_container_width=True):
                        if is_available:
                            if seat_id in st.session_state.current_selected_seats:
                                st.session_state.current_selected_seats.remove(seat_id)
                            else:
                                st.session_state.current_selected_seats.append(seat_id)
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# CORE APPLICATION ROUTING
# =====================================================
inject_custom_css()
render_navbar()

is_logged_in = st.session_state.auth_ctrl.is_logged_in()
is_admin = st.session_state.auth_ctrl.is_admin()

with st.sidebar:
    st.markdown("<h3 style='text-align: center; color: #E53935; font-weight:800;'>SUNNYX DASH</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #E2E8F0;'>", unsafe_allow_html=True)
    
    if not is_logged_in:
        menu_option = st.radio("MENU", ["Trang chủ hệ thống", "Đăng ký tài khoản", "Đăng nhập"], label_visibility="collapsed")
        if menu_option == "Đăng nhập":
            st.session_state.auth_view = "login"
        elif menu_option == "Đăng ký tài khoản":
            st.session_state.auth_view = "register"
        else:
            st.session_state.auth_view = None
    else:
        if is_admin:
            st.markdown("<p style='font-size:12px; color:#718096; font-weight:700;'>QUẢN TRỊ VIÊN</p>", unsafe_allow_html=True)
            menu_option = st.radio("ADMIN", ["Báo cáo tổng quan", "Cập nhật danh mục phim", "Điều phối suất chiếu"], label_visibility="collapsed")
        else:
            st.markdown("<p style='font-size:12px; color:#718096; font-weight:700;'>KHÁCH HÀNG</p>", unsafe_allow_html=True)
            menu_option = st.radio("CUSTOMER", ["Lịch chiếu phim", "Lịch sử mua vé"], label_visibility="collapsed")
        
        st.markdown("<br><hr style='border-color:#E2E8F0;'>", unsafe_allow_html=True)
        if st.button("Đăng xuất", use_container_width=True):
            st.session_state.auth_ctrl.logout()
            st.session_state.auth_view = None
            st.session_state.selected_movie_id = None
            st.session_state.selected_showtime_id = None
            st.rerun()

# =====================================================
# 1. GIAO DIỆN XÁC THỰC
# =====================================================
if not is_logged_in and st.session_state.auth_view in ["login", "register"]:
    _, auth_center, _ = st.columns([1, 1, 1])
    with auth_center:
        if st.session_state.auth_view == "login":
            st.markdown('<div class="auth-overlay" style="padding: 40px;">', unsafe_allow_html=True)
            st.markdown('<div style="font-size:22px; font-weight:700; text-align:center; color:#2D3748; margin-bottom:20px;">ĐĂNG NHẬP</div>', unsafe_allow_html=True)
            username = st.text_input("Tài khoản", key="auth_login_user")
            password = st.text_input("Mật khẩu", type="password", key="auth_login_pass")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Xác nhận", use_container_width=True):
                role = st.session_state.auth_ctrl.login(username, password)
                if role != "FAILED":
                    st.success("Đăng nhập thành công!")
                    st.session_state.auth_view = None
                    st.rerun()
                else:
                    st.error("Tài khoản hoặc mật khẩu không đúng.")
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.auth_view == "register":
            st.markdown('<div class="auth-overlay" style="padding: 40px;">', unsafe_allow_html=True)
            st.markdown('<div style="font-size:22px; font-weight:700; text-align:center; color:#2D3748; margin-bottom:20px;">ĐĂNG KÝ</div>', unsafe_allow_html=True)
            reg_username = st.text_input("Tên tài khoản", key="auth_reg_user")
            reg_password = st.text_input("Mật khẩu", type="password", key="auth_reg_pass")
            reg_confirm = st.text_input("Xác nhận mật khẩu", type="password", key="auth_reg_conf")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Tạo tài khoản", use_container_width=True):
                success = st.session_state.auth_ctrl.register(reg_username, reg_password, reg_confirm)
                if success:
                    st.success("Đăng ký thành công! Vui lòng đăng nhập.")
                else:
                    st.error("Lỗi: Tài khoản đã tồn tại hoặc mật khẩu không khớp.")
            st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# 2. PHÂN HỆ ADMIN
# =====================================================
elif is_logged_in and is_admin:
    if menu_option == "Báo cáo tổng quan":
        st.markdown("<h2 style='color:#2D3748; font-weight:700;'>PHÂN TÍCH DOANH THU</h2>", unsafe_allow_html=True)
        render_metric_dashboard()
        
        st.markdown("<br><h3 style='color:#2D3748;'>Biểu đồ doanh thu phim</h3>", unsafe_allow_html=True)
        top_movies_list = st.session_state.admin_ctrl.get_top_movies_by_revenue(limit=5)
        
        if top_movies_list:
            movie_titles = []
            movie_revenues = []
            
            # SỬA LỖI LOGIC: Đọc an toàn mọi kiểu dữ liệu trả về từ admin_ctrl
            for item in top_movies_list:
                if isinstance(item, (tuple, list)) and len(item) >= 2:
                    movie_obj, rev = item[0], item[1]
                    title = movie_obj.get_title() if hasattr(movie_obj, 'get_title') else str(movie_obj)
                    movie_titles.append(title)
                    movie_revenues.append(rev)
                elif hasattr(item, 'get_title'):
                    movie_titles.append(item.get_title())
                    if hasattr(item, 'get_revenue'):
                        movie_revenues.append(item.get_revenue())
                    elif hasattr(item, 'revenue'):
                        movie_revenues.append(item.revenue)
                    else:
                        movie_revenues.append(0)
                elif isinstance(item, dict):
                    movie_titles.append(item.get('title', 'N/A'))
                    movie_revenues.append(item.get('revenue', 0))
            
            fig = go.Figure(data=[go.Bar(x=movie_titles, y=movie_revenues, marker_color='#E53935')])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#2D3748', height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu doanh thu.")

    elif menu_option == "Cập nhật danh mục phim":
        st.markdown("<h2 style='color:#2D3748; font-weight:700;'>QUẢN LÝ PHIM</h2>", unsafe_allow_html=True)
        
        _, form_center, _ = st.columns([1, 2, 1])
        with form_center:
            with st.expander("Thêm phim mới"):
                with st.form("admin_add_movie"):
                    m_title = st.text_input("Tên phim")
                    m_genre = st.text_input("Thể loại")
                    m_duration = st.number_input("Thời lượng (phút)", min_value=1, value=120)
                    m_desc = st.text_area("Mô tả")
                    m_price = st.number_input("Giá vé (VNĐ)", min_value=0.0, value=80000.0)
                    m_poster = st.text_input("Link Poster")
                    
                    if st.form_submit_button("Lưu phim", use_container_width=True):
                        new_id = st.session_state.movie_ctrl.generate_movie_id()
                        new_movie = MovieData(
                            movie_id=new_id, title=m_title, genre=m_genre,
                            duration=int(m_duration), description=m_desc,
                            base_price=m_price, poster_path=m_poster
                        )
                        if st.session_state.movie_ctrl.add_movie(new_movie):
                            st.success("Thêm thành công!")
                            st.rerun()
                        else:
                            st.error("Lỗi mã phim.")

            with st.expander("Sửa thông tin phim"):
                movies_list = st.session_state.movie_ctrl.get_movie_data()
                if not movies_list:
                    st.warning("Hệ thống chưa có phim.")
                else:
                    movie_dict = {m.get_title(): m for m in movies_list}
                    selected_title = st.selectbox("Chọn phim cần sửa", list(movie_dict.keys()))
                    sel_movie = movie_dict[selected_title]

                    with st.form("admin_edit_movie"):
                        n_title = st.text_input("Tên phim", value=sel_movie.get_title())
                        n_genre = st.text_input("Thể loại", value=sel_movie.get_genre())
                        n_duration = st.number_input("Thời lượng (phút)", value=int(sel_movie.get_duration()), min_value=1)
                        n_price = st.number_input("Giá vé (VNĐ)", value=float(sel_movie.get_base_price()), min_value=0.0)
                        n_desc = st.text_area("Mô tả", value=sel_movie.get_description())
                        n_poster = st.text_input("Link Poster", value=sel_movie.get_poster_path())

                        if st.form_submit_button("Cập nhật thông tin", use_container_width=True):
                            # Cơ chế gán động an toàn, không đụng chạm phá vỡ logic cũ
                            for attr, val in [('title', n_title), ('genre', n_genre), ('duration', n_duration), ('description', n_desc)]:
                                setter_name = f"set_{attr}"
                                if hasattr(sel_movie, setter_name):
                                    getattr(sel_movie, setter_name)(val)
                                else:
                                    setattr(sel_movie, attr, val)
                            
                            if hasattr(sel_movie, 'set_base_price'): sel_movie.set_base_price(n_price)
                            elif hasattr(sel_movie, 'set_price'): sel_movie.set_price(n_price)
                            else: sel_movie.base_price = n_price

                            if hasattr(sel_movie, 'set_poster_path'): sel_movie.set_poster_path(n_poster)
                            elif hasattr(sel_movie, 'set_poster'): sel_movie.set_poster(n_poster)
                            else: sel_movie.poster_path = n_poster
                            
                            st.session_state.io_handler.save_movies(st.session_state.movie_ctrl.get_movie_data())
                            st.success("Đã cập nhật thành công!")
                            st.rerun()
                            
        st.markdown("<br><h3 style='color:#2D3748;'>Danh sách phim hiện tại</h3>", unsafe_allow_html=True)
        for mv in st.session_state.movie_ctrl.get_movie_data():
            col_info, col_action = st.columns([5, 1])
            with col_info:
                st.markdown(f"""
                    <div style='background:#FFFFFF; border:1px solid #E2E8F0; padding:16px; border-radius:8px; margin-bottom:10px;'>
                        <strong style='color:#2D3748;'>[{mv.get_movie_id()}] {mv.get_title()}</strong><br>
                        <span style='font-size:13px; color:#718096;'>Thể loại: {mv.get_genre()} | Thời lượng: {mv.get_duration()} phút</span>
                    </div>
                """, unsafe_allow_html=True)
            with col_action:
                st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                if st.button("Xóa", key=f"admin_del_{mv.get_movie_id()}", use_container_width=True):
                    if st.session_state.movie_ctrl.delete_movie(mv.get_movie_id(), st.session_state.showtime_ctrl):
                        st.success("Đã xóa")
                        st.rerun()
                    else:
                        st.error("Phim đang có lịch diễn.")

    elif menu_option == "Điều phối suất chiếu":
        st.markdown("<h2 style='color:#2D3748; font-weight:700;'>ĐIỀU PHỐI SUẤT CHIẾU</h2>", unsafe_allow_html=True)
        _, form_center, _ = st.columns([1, 2, 1])
        with form_center:
            with st.expander("Tạo suất chiếu mới"):
                movie_list = st.session_state.movie_ctrl.get_movie_data()
                room_list = st.session_state.room_ctrl.get_room_data()
                if not movie_list or not room_list:
                    st.warning("Cần thêm phim và phòng trước.")
                else:
                    movie_mapping = {m.get_title(): m.get_movie_id() for m in movie_list}
                    room_mapping = {r.get_room_name(): r.get_room_id() for r in room_list}
                    selected_m = st.selectbox("Phim", list(movie_mapping.keys()))
                    selected_r = st.selectbox("Phòng", list(room_mapping.keys()))
                    date_input = st.date_input("Ngày chiếu", datetime.date.today())
                    time_input = st.time_input("Giờ chiếu", datetime.time(19, 0))
                    
                    if st.button("Lưu suất chiếu", use_container_width=True):
                        from models.entities import SeatMatrix
                        st_id = st.session_state.showtime_ctrl.generate_showtime_id()
                        start_str = f"{date_input} {time_input.strftime('%H:%M')}"
                        selected_room_id = room_mapping[selected_r]
                        room_node = st.session_state.room_ctrl.find_room(selected_room_id)
                        room_obj = room_node.get_data()
                        default_matrix = SeatMatrix(rows=room_obj.rows, cols=room_obj.cols)
                        new_st = Showtime(
                            showtime_id=st_id, movie_id=movie_mapping[selected_m],
                            room_id=room_mapping[selected_r], start_time=start_str,
                            seat_matrix=default_matrix
                        )
                        if st.session_state.showtime_ctrl.add_showtime(new_st, st.session_state.movie_ctrl):
                            st.success("Thành công!")
                            st.rerun()
                        else:
                            st.error("Phòng này đã có lịch chiếu trùng thời gian.")

# =====================================================
# 3. PHÂN HỆ KHÁCH HÀNG
# =====================================================
else:
    if menu_option in ["Lịch chiếu phim", "Trang chủ hệ thống"]:
        if st.session_state.selected_movie_id is None:
            render_homepage()
        elif st.session_state.selected_movie_id and st.session_state.selected_showtime_id is None:
            movie_node = st.session_state.movie_ctrl.search_by_id(st.session_state.selected_movie_id)
            movie = movie_node.get_data()
            
            st.markdown(f"<h2 style='color:#2D3748;'>Lịch chiếu: {movie.get_title()}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#718096;'>{movie.get_description()}</p>", unsafe_allow_html=True)
            
            all_st = st.session_state.showtime_ctrl.get_showtime_data()
            valid_st = [s for s in all_st if s.get_movie_id() == movie.get_movie_id()]
            
            if not valid_st:
                st.info("Phim chưa được xếp suất chiếu.")
                st.markdown('<div class="sec-btn">', unsafe_allow_html=True)
                if st.button("Quay lại"):
                    st.session_state.selected_movie_id = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                # TÍNH NĂNG: THANH CHỌN SUẤT CHIẾU THEO NGÀY
                unique_dates = sorted(list(set(s.get_start_time().split()[0] for s in valid_st)))
                selected_date = st.selectbox("Chọn ngày xem phim:", unique_dates)
                
                # Lọc lại danh sách suất chiếu theo ngày đã chọn
                filtered_st = [s for s in valid_st if s.get_start_time().startswith(selected_date)]
                
                st.markdown("<h4 style='color:#2D3748; margin-top:20px;'>Các suất chiếu trong ngày:</h4>", unsafe_allow_html=True)
                for showtime in filtered_st:
                    room_node = st.session_state.room_ctrl.find_room(showtime.get_room_id())
                    room_name = room_node.get_data().get_room_name() if room_node else showtime.get_room_id()
                    
                    col_st_info, col_st_action = st.columns([4, 1])
                    with col_st_info:
                        st.markdown(f"""
                            <div style='background:#FFFFFF; padding:16px; border-radius:8px; border-left:4px solid #E53935; margin-bottom:12px; border:1px solid #E2E8F0;'>
                                <span style='font-weight:600; color:#2D3748;'>Giờ chiếu: {showtime.get_start_time().split()[1]}</span> | <span style='color:#718096;'>Phòng chiếu: {room_name}</span>
                            </div>
                        """, unsafe_allow_html=True)
                    with col_st_action:
                        st.markdown("<div style='margin-top:4px;'></div>", unsafe_allow_html=True)
                        if st.button("Chọn Suất", key=f"st_select_btn_{showtime.get_showtime_id()}", use_container_width=True):
                            st.session_state.selected_showtime_id = showtime.get_showtime_id()
                            st.session_state.current_selected_seats = []
                            st.rerun()
                            
                st.markdown('<br><div class="sec-btn">', unsafe_allow_html=True)
                if st.button("Quay lại"):
                    st.session_state.selected_movie_id = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.selected_showtime_id:
            showtime_node = st.session_state.showtime_ctrl.find_showtime(st.session_state.selected_showtime_id)
            showtime = showtime_node.get_data()
            movie = st.session_state.movie_ctrl.search_by_id(st.session_state.selected_movie_id).get_data()
            
            render_seat_layout(showtime, movie)
            
            st.markdown("<br><hr style='border-color:#E2E8F0;'>", unsafe_allow_html=True)
            total_price = len(st.session_state.current_selected_seats) * movie.get_base_price()
            
            # CĂN CHỈNH BẢNG THANH TOÁN RA GIỮA
            _, bill_center, _ = st.columns([1, 2, 1])
            with bill_center:
                seats_str = ', '.join(st.session_state.current_selected_seats) if st.session_state.current_selected_seats else 'Chưa chọn'
                st.markdown(f"**Ghế đã chọn:** <span style='color:#E53935; font-weight:700; font-size:16px;'>{seats_str}</span>", unsafe_allow_html=True)
                st.markdown(f"**Tổng tiền thanh toán:** <span style='color:#2D3748; font-size:22px; font-weight:bold;'>{total_price:,.0f} VNĐ</span>", unsafe_allow_html=True)
                st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                
                if st.button("Xác nhận thanh toán vé", disabled=not st.session_state.current_selected_seats, use_container_width=True):
                    user_obj = st.session_state.auth_ctrl.get_current_user()
                    success_flag = True
                    
                    for seat_str in st.session_state.current_selected_seats:
                        row_idx = ord(seat_str[0]) - 65
                        col_idx = int(seat_str[1:]) - 1
                        
                        booked = st.session_state.booking_ctrl.process_booking(
                            user_obj, movie, showtime, row_idx, col_idx, st.session_state.movie_ctrl
                        )
                        if not booked:
                            success_flag = False
                            
                    if success_flag:
                        st.success("Đặt vé rạp CGV thành công!")
                        st.session_state.current_selected_seats = []
                        st.session_state.selected_showtime_id = None
                        st.session_state.selected_movie_id = None
                        st.rerun()
                    else:
                        st.error("Lỗi: Ghế vừa chọn đã bị người khác đặt trước.")
                
                st.markdown('<div class="sec-btn" style="margin-top:15px;">', unsafe_allow_html=True)
                if st.button("Quay lại danh sách suất chiếu", use_container_width=True):
                    st.session_state.selected_showtime_id = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    elif menu_option == "Lịch sử mua vé":
        st.markdown("<h2 style='color:#2D3748; font-weight:700;'>LỊCH SỬ GIAO DỊCH VÉ</h2>", unsafe_allow_html=True)
        user_obj = st.session_state.auth_ctrl.get_current_user()
        history_list = st.session_state.booking_ctrl.get_booking_history(user_obj.get_user_id())
        
        if not history_list:
            st.info("Tài khoản của bạn chưa thực hiện giao dịch mua vé nào.")
        else:
            for ticket in history_list:
                m_node = st.session_state.movie_ctrl.search_by_id(ticket.get_movie_id())
                m_title = m_node.get_data().get_title() if m_node else "Phim hệ thống"
                status_color = "#E53935" if ticket.get_status() == "BOOKED" else "#A0AEC0"
                
                col_ticket_card, col_ticket_action = st.columns([5, 1])
                with col_ticket_card:
                    st.markdown(f"""
                        <div style='background: #FFFFFF; padding: 18px; border-radius: 8px; margin-bottom: 12px; border: 1px solid #E2E8F0; border-left: 4px solid {status_color};'>
                            <strong style='font-size:16px; color:#2D3748;'>{m_title}</strong> | <span style='font-size:12px; color:#718096;'>Mã vé: {ticket.get_ticket_id()}</span><br>
                            <span style='font-size:14px; color:#4A5568;'>Vị trí ghế: <strong style='color:#E53935;'>{ticket.get_seat_id()}</strong> | Chi phí: {ticket.get_price():,.0f} VNĐ</span><br>
                            Trạng thái giao dịch: <strong style='color:{status_color};'>{ticket.get_status()}</strong>
                        </div>
                    """, unsafe_allow_html=True)
                with col_ticket_action:
                    st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
                    if ticket.get_status() == "BOOKED":
                        if st.button("Hủy vé", key=f"cust_cancel_{ticket.get_ticket_id()}", use_container_width=True):
                            if st.session_state.booking_ctrl.cancel_booking(user_obj.get_user_id(), ticket.get_ticket_id()):
                                st.success("Đã hoàn hủy thành công!")
                                st.rerun()
                            else:
                                st.error("Không thể hoàn hủy vé vào lúc này.")