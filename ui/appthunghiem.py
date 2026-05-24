#NÀY LÀ ĐỂ THỬ WEB THOI CHƯA CÓ GÌ ĐÂU
import streamlit as st

# 1. CẤU HÌNH TRANG WEB
st.set_page_config(page_title="Rạp Chiếu Phim", layout="centered")
st.title("🍿 Hệ thống Đặt Vé Rạp Chiếu Phim")
st.markdown("---")

# 2. CHỌN PHIM VÀ SUẤT CHIẾU
st.header("1. Chọn phim đang chiếu")
# Danh sách phim được đưa vào menu thả xuống
phim_duoc_chon = st.selectbox(
    "Vui lòng chọn bộ phim bạn muốn xem:",
    ["Avatar: Lửa và Tro Tàn", "Tiểu Yêu Quái Núi Lãng Lãng", "Tee Yod: Quỷ Ăn Tạng 3", "Nụ Hôn Bạc Tỷ"]
)

st.write(f"**Phim đang chọn:** {phim_duoc_chon}")
# Menu chọn giờ chiếu nằm ngang
suat_chieu = st.radio("Chọn suất chiếu:", ["09:00", "14:30", "19:00", "22:00"], horizontal=True)

# 3. CHỌN GHẾ (Dùng checkbox để chọn nhiều ghế)
st.markdown("---")
st.header("2. Chọn vị trí ngồi")
st.markdown("<div style='text-align: center; background-color: #87CEEB; color: black; padding: 10px; border-radius: 5px;'>MÀN HÌNH HƯỚNG NÀY</div>", unsafe_allow_html=True)
st.write("") 

hang_ghe = ["A", "B", "C", "D"]
so_cot = 6
ghe_da_chon = [] # Danh sách lưu các ghế khách hàng click vào

# Vòng lặp vẽ ma trận ghế 4 hàng x 6 cột
for hang in hang_ghe:
    cols = st.columns(so_cot)
    for i in range(so_cot):
        ten_ghe = f"{hang}{i+1}"
        with cols[i]:
            # Dùng checkbox để tích chọn
            if st.checkbox(ten_ghe, key=ten_ghe):
                ghe_da_chon.append(ten_ghe)

# 4. THANH TOÁN VÀ XÁC NHẬN
st.markdown("---")
st.header("3. Xác nhận đặt vé")

# Nếu danh sách ghế đã chọn có dữ liệu
if len(ghe_da_chon) > 0:
    st.success(f"Bạn đã chọn các ghế: **{', '.join(ghe_da_chon)}**")
    
    # Giả sử giá vé là 50.000đ/ghế
    tong_tien = len(ghe_da_chon) * 50000
    st.info(f"Tổng tiền thanh toán: **{tong_tien:,} VNĐ**")
    
    # Nút bấm xác nhận đặt vé
    if st.button("Xác nhận & Thanh toán", type="primary"):
        st.balloons() # Hiệu ứng bóng bay chúc mừng
        st.success("🎉 Chúc mừng! Bạn đã đặt vé thành công!")
else:
    st.warning("Vui lòng chọn ít nhất 1 ghế ở sơ đồ phía trên để tiếp tục.")
