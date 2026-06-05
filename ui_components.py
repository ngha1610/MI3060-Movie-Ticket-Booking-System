import streamlit as st

# ==========================================
# CÁC HÀM GIAO DIỆN PHỤ TRỢ CHO APP.PY
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
            if st.button(f"MUA VÉ", key=f"btn_{title}", use_container_width=True, type="primary"):
                if not st.session_state.is_logged_in:
                    st.error(f"Vui lòng đăng nhập để đặt vé!")
                else:
                    navigate_to("booking", title)