import time
from controllers.global_state import init_global_system
from models.entities import SeatStatus, TicketData

# Khởi tạo hệ thống core nạp dữ liệu từ RAM lên
(
    auth_ctrl,
    movie_ctrl,
    showtime_ctrl,
    room_ctrl,
    booking_ctrl,
    admin_ctrl
) = init_global_system()


# ==========================================================
# 1. SEARCH MOVIE (LINEAR SEARCH - SCALE TEST READY)
# ==========================================================
def benchmark_movie_search():
    movies = movie_ctrl.get_movie_data()
    if not movies:
        print("[Movie Search] Không có dữ liệu phim.")
        return

    times = []
    print("\n[-->] SCALE TEST: Movie Search (O(N) Linear Search)")

    for i in range(100):
        # Ép thuật toán chạy Worst Case duyệt đến node cuối cùng
        worst_case_title = f"Phim_Khong_Ton_Tai_{i}"

        start = time.perf_counter()
        movie_ctrl.search_by_title(worst_case_title)
        end = time.perf_counter()

        times.append(end - start)

    avg = sum(times) / len(times)
    print(f"--> Average Movie Search Time: {avg * 1000:.6f} ms")


# ==========================================================
# 2. SHOWTIME + SEAT MAP (O(N + R*C))
# ==========================================================
def benchmark_showtime_and_seats():
    showtimes = showtime_ctrl.get_showtime_data()
    if not showtimes:
        print("[Showtime] Không có dữ liệu.")
        return

    target = showtimes[-1]
    times = []
    print("\n[-->] SCALE TEST: Showtime + Seat Rendering")

    for _ in range(100):
        start = time.perf_counter()

        node = showtime_ctrl.find_showtime(target.get_showtime_id())
        if node:
            st = node.get_data()
            matrix = st.get_seat_matrix()
            rows = matrix.get_rows()
            cols = matrix.get_cols()

            for r in range(rows):
                for c in range(cols):
                    matrix._seats.get_val(r, c)

        end = time.perf_counter()
        times.append(end - start)

    avg = sum(times) / len(times)
    print(f"--> Average Showtime & Seats Time: {avg * 1000:.6f} ms")


# ==========================================================
# 3. BOOKING HISTORY (LINEAR FILTER OVER TICKETS)
# ==========================================================
def benchmark_booking_history():
    users = auth_ctrl.get_all_users()
    if not users:
        print("[Booking History] Không có dữ liệu user.")
        return

    user = users[-1]
    times = []
    print("\n[-->] SCALE TEST: Booking History Filter")

    for _ in range(100):
        start = time.perf_counter()
        booking_ctrl.get_booking_history(user.get_user_id())
        end = time.perf_counter()

        times.append(end - start)

    avg = sum(times) / len(times)
    print(f"--> Average Booking History Time: {avg * 1000:.6f} ms")


# ==========================================================
# 4. ONLINE BOOKING (FULL TRANSACTION FLOW SCALE TEST)
# ==========================================================
def benchmark_online_booking():
    showtimes = showtime_ctrl.get_showtime_data()
    if not showtimes:
        print("[Booking] Không có showtime.")
        return

    target = showtimes[-1]
    times = []
    print("\n[-->] SCALE TEST: Online Booking Transaction Flow")

    for i in range(100):
        seat_code = "A01"
        start = time.perf_counter()

        # 1. Tìm showtime qua ID (Duyệt cấu trúc Danh sách liên kết)
        node = showtime_ctrl.find_showtime(target.get_showtime_id())
        if not node:
            continue

        showtime = node.get_data()
        matrix = showtime.get_seat_matrix()

        # 2 + 3. Kiểm tra trạng thái ghế thô (Mã gốc dùng hệ số 0 và 0 tương ứng hàng A cột 1)
        # Sửa lỗi: Khớp đúng định dạng lưu trữ thô của mảng 2D Array2D hệ thống
        if matrix._seats.get_val(0, 0) != SeatStatus.EMPTY:
            end = time.perf_counter()
            times.append(end - start)
            continue

        # 4. Cập nhật trạng thái ghế trên ma trận RAM sang BOOKED
        matrix._seats.set_val(0, 0, SeatStatus.BOOKED)

        # 5. Khởi tạo thực thể dữ liệu Vé mới
        ticket = TicketData(
            ticket_id=f"BENCH_{i}",
            user_id="U_BENCH",
            movie_id=showtime.get_movie_id(),
            seat_id=seat_code,
            status=SeatStatus.BOOKED,
            showtime_id=target.get_showtime_id(),
            room_id=showtime.get_room_id(),
            price=60000
        )

        # 6. Chèn phần tử Vé mới vào đuôi TicketLinkedList qua con trỏ _tail (O(1))
        booking_ctrl._ticket_list.add_ticket(ticket)

        # 7. Tích lũy doanh thu cho phim (Mô phỏng hàm xử lý tăng biến cục bộ)
        m_node = movie_ctrl.search_by_id(showtime.get_movie_id())
        if m_node:
            movie_obj = m_node.get_data()
            if hasattr(movie_obj, '_revenue'):
                movie_obj._revenue += 60000

        end = time.perf_counter()
        times.append(end - start)

    avg = sum(times) / len(times)
    print(f"--> Average Online Booking Time: {avg * 1000:.6f} ms")


# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    print("==========================================")
    print("        SCALE TEST BENCHMARK SYSTEM       ")
    print("==========================================")

    benchmark_movie_search()
    benchmark_showtime_and_seats()
    benchmark_booking_history()
    benchmark_online_booking()

    print("\n==========================================")
    print("              DONE SCALE TEST             ")
    print("==========================================")