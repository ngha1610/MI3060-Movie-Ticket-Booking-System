import time

from controllers.global_state import (
    init_global_system
)

auth_ctrl, movie_ctrl, showtime_ctrl, room_ctrl, booking_ctrl, admin_ctrl = (
    init_global_system()
)

# User benchmark không được tồn tại trong dataset gốc
username = "benchmark_user"

start = time.perf_counter()

auth_ctrl.register(
    username,
    "123456",
    "123456"
)

end = time.perf_counter()

print(
    f"Register Time: {(end - start) * 1000:.6f} ms"
)