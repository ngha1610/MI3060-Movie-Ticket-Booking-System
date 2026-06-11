import streamlit as st
import random

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
    st.image("https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?q=80&w=2070", use_container_width=True)
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

# ==========================================
# HÀM TUNG BỎNG NGÔ
# ==========================================

def show_popcorn_effect():
    # SVG Đã được vẽ lại: 4 lớp màu (bóng đổ, bơ đậm, bơ nhạt, và hạt ngô cháy ở đáy)
    popcorn_html = """
    <style>
    .popcorn-container {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        pointer-events: none; 
        z-index: 99999; 
        overflow: hidden;
    }
    .popcorn-kernel {
        position: absolute;
        left: 50%; /* Xuất phát từ giữa màn hình dưới cùng */
        bottom: -15%;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path fill="%23C1851A" d="M40 85c-15 0-25-10-25-25 0-10 5-18 12-22-2-8 3-20 15-20 10 0 18 5 22 12 5-6 15-8 23-2 8 6 10 18 5 26 8 5 12 15 10 25-3 15-18 20-30 18-5 8-18 10-32-12z"/><path fill="%23F2C347" d="M42 80c-13 0-22-9-22-22 0-9 4-16 10-20-2-7 3-18 13-18 9 0 16 5 20 11 4-5 13-7 20-2 7 5 9 16 4 23 7 4 11 13 9 22-3 13-16 18-26 16-4 7-16 9-28-10z"/><path fill="%23FFE38F" d="M45 74c-9 0-15-7-15-15 0-7 3-12 8-15-1-5 2-12 9-12 7 0 12 4 15 9 3-4 10-5 15-1 5 4 6 12 3 17 5 3 8 10 6 16-2 10-12 13-20 11-3 5-12 7-21-7z"/><path fill="%238B4513" d="M50 82c-5 8-15 8-15 2 0-8 5-15 15-15 10 0 15 7 15 15 0 6-10 6-15-2z"/></svg>');
        background-size: contain;
        background-repeat: no-repeat;
        animation: explode ease-out forwards;
    }
    
    @keyframes explode {
        0% { transform: translate(-50%, 0) scale(0) rotate(0deg); opacity: 1; }
        50% { opacity: 1; }
        100% { transform: translate(calc(-50% + var(--tx)), var(--ty)) scale(1) rotate(var(--rot)); opacity: 0; }
    }
    </style>
    <div class="popcorn-container">
    """
    
    # Ép bùng nổ 90 hạt bỏng ngô
    for _ in range(90):
        # Trục X: Văng cực mạnh sang mép trái (-90vw) và mép phải (90vw)
        tx = random.uniform(-90, 90) 
        # Trục Y: Văng thẳng qua nóc màn hình
        ty = random.uniform(-90, -140) 
        # Độ xoáy ngẫu nhiên (xoay nhiều vòng)
        rot = random.uniform(360, 1440) 
        
        # Kích thước đa dạng tạo chiều sâu (hạt to nhìn như bay sát vào mặt)
        size = random.randint(45, 120) 
        duration = random.uniform(1.2, 2.8) 
        delay = random.uniform(0, 0.3) # Độ trễ ngắn để tạo cảm giác nổ rào rào
        
        popcorn_html += f'<div class="popcorn-kernel" style="width: {size}px; height: {size}px; --tx: {tx}vw; --ty: {ty}vh; --rot: {rot}deg; animation-duration: {duration}s; animation-delay: {delay}s;"></div>'
    
    popcorn_html += "</div>"
    st.markdown(popcorn_html, unsafe_allow_html=True)