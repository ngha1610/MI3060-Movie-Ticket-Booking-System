import time
from controllers.global_state import init_global_system
from models.entities import SeatStatus, TicketData, MovieData, Showtime

(
    auth_ctrl,
    movie_ctrl,
    showtime_ctrl,
    room_ctrl,
    booking_ctrl,
    admin_ctrl
) = init_global_system()


# ==========================================================
# 1. ADD MOVIE (O(1) TAIL INSERT - LINKED LIST)
# ==========================================================
def benchmark_add_movie():
    print("\n[-->] SCALE TEST: Add Movie (O(1))")
    times = []

    for i in range(100):
        movie = MovieData(
            movie_id=f"M_BENCH_{i}",
            title=f"Movie {i}",
            genre="Action",
            duration=120,
            description="Benchmark",
            base_price=50000,
            poster_path=""
        )

        start = time.perf_counter()
        movie_ctrl._movie_list.add_movie(movie)  # O(1)
        end = time.perf_counter()

        times.append(end - start)

    print(f"Avg Add Movie: {sum(times)/len(times)*1000:.6f} ms")


# ==========================================================
# 2. ADD SHOWTIME (O(1))
# ==========================================================
def benchmark_add_showtime():
    print("\n[-->] SCALE TEST: Add Showtime (O(1))")
    times = []

    for i in range(100):
        showtime = Showtime(
            showtime_id=f"ST_{i}",
            movie_id="M001",
            start_time="19:30",
            room_id="R001",
            room_rows=8,
            room_cols=12
        )

        start = time.perf_counter()
        showtime_ctrl._showtime_list.add_showtime(showtime)  # O(1)
        end = time.perf_counter()

        times.append(end - start)

    print(f"Avg Add Showtime: {sum(times)/len(times)*1000:.6f} ms")


# ==========================================================
# 3. OFFLINE TICKET SALE
# O(N) search + O(1) seat update + O(1) insert + O(N) movie lookup
# ==========================================================
def benchmark_offline_ticket_sale():
    print("\n[-->] SCALE TEST: Offline Ticket Sale")

    showtimes = showtime_ctrl.get_showtime_data()
    if not showtimes:
        return

    target = showtimes[-1]
    times = []

    for i in range(100):
        start = time.perf_counter()

        # O(N) search showtime
        node = showtime_ctrl.find_showtime(target.get_showtime_id())
        if not node:
            continue

        st = node.get_data()
        matrix = st.get_seat_matrix()

        # ĐỘC LẬP TỌA ĐỘ: Phân bổ ghế động theo i để 100 lần chạy đều mua vé thành công
        # Phòng chiếu mẫu có 8 hàng, 12 cột -> i chạy từ 0-99 không lo vượt index
        r = (i // 12) % 8
        c = i % 12

        if matrix.check_status(r, c) != SeatStatus.EMPTY:
            end = time.perf_counter()
            times.append(end - start)
            continue

        matrix.set_seat_status(r, c, SeatStatus.BOOKED)

        ticket = TicketData(
            ticket_id=f"OFF_{i}",
            user_id="GUEST",
            movie_id=st.get_movie_id(),
            seat_id=f"SEAT_{r}_{c}",
            status=SeatStatus.BOOKED,
            showtime_id=target.get_showtime_id(),
            room_id=st.get_room_id(),
            price=70000
        )

        booking_ctrl._ticket_list.add_ticket(ticket)  # O(1)

        # O(N) nếu linked list search
        m_node = movie_ctrl.search_by_id(st.get_movie_id())
        if m_node:
            m_node.get_data().add_revenue(70000)

        end = time.perf_counter()
        times.append(end - start)

    print(f"Avg Offline Sale: {sum(times)/len(times)*1000:.6f} ms")


# ==========================================================
# 4. REVENUE (O(M))
# ==========================================================
def benchmark_revenue():
    print("\n[-->] SCALE TEST: Revenue Calculation")
    times = []

    for _ in range(100):
        start = time.perf_counter()
        _ = admin_ctrl.calculate_revenue()  # O(M)
        end = time.perf_counter()
        times.append(end - start)

    print(f"Avg Revenue: {sum(times)/len(times)*1000:.6f} ms")


# ==========================================================
# 5. TOP MOVIE REVENUE (O(M + K^2) IF BUBBLE SORT)
# ==========================================================
def benchmark_top_movie_revenue():
    print("\n[-->] SCALE TEST: Top Movie Revenue")
    times = []

    for _ in range(100):
        start = time.perf_counter()

        # WARNING: bubble sort => O(K^2)
        _ = admin_ctrl.get_top_movies_by_revenue(limit=10)

        end = time.perf_counter()
        times.append(end - start)

    print(f"Avg Top Revenue: {sum(times)/len(times)*1000:.6f} ms")


# ==========================================================
# 6. REPORT (O(M + N + K))
# ==========================================================
def benchmark_report():
    print("\n[-->] SCALE TEST: System Report")
    times = []

    for _ in range(100):
        start = time.perf_counter()
        _ = admin_ctrl.generate_report()
        end = time.perf_counter()
        times.append(end - start)

    print(f"Avg Report: {sum(times)/len(times)*1000:.6f} ms")


# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    print("==========================================")
    print("        ADMIN SCALE TEST BENCHMARK        ")
    print("==========================================")

    benchmark_add_movie()
    benchmark_add_showtime()
    benchmark_offline_ticket_sale()
    benchmark_revenue()
    benchmark_top_movie_revenue()
    benchmark_report()

    print("\n==========================================")
    print("              DONE SCALE TEST             ")
    print("==========================================")