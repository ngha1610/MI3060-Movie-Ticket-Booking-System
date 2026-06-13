import time

from controllers.global_state import (
    init_global_system
)

auth_ctrl, movie_ctrl, showtime_ctrl, room_ctrl, booking_ctrl, admin_ctrl = (
    init_global_system()
)

users = auth_ctrl._user_table.get_all()

times = []

for user in users:

    start = time.perf_counter()

    auth_ctrl.login(
        user.get_username(),
        user.get_password()
    )

    end = time.perf_counter()

    times.append(
        end - start
    )

avg = sum(times) / len(times)

print(
    f"Average Login Time: {avg*1000:.6f} ms"
)