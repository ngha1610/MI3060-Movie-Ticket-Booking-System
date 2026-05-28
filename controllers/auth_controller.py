from models.entities import (
    UserData
)

from data_structures.hash_table import (
    UserHashTable
)

from data_structures.file_io import (
    FileIOHandler
)

# =====================================================
# AUTH CONTROLLER
# =====================================================

class AuthController:

    def __init__(
        self,
        io_handler: FileIOHandler
    ):

        self._io_handler = io_handler

        self._user_table = (
            UserHashTable()
        )

        self._io_handler.load_users(
            self._user_table
        )

        self._current_user = None

    # =================================================
    # TẠO USER ID (ĐÃ SỬA: CHỐNG TRÙNG MÃ KHI XÓA)
    # =================================================

    def _generate_user_id(self):

        all_users = self._user_table.get_all()
        
        # Nếu hệ thống chưa có user nào, cấp mã đầu tiên
        if not all_users:
            return "U000000001"

        max_id_num = 0
        for user in all_users:
            user_id_str = user.get_user_id()  # Định dạng dạng "U000000005"
            try:
                # Cắt bỏ chữ 'U' ở đầu và chuyển phần còn lại thành số int
                id_num = int(user_id_str[1:])
                if id_num > max_id_num:
                    max_id_num = id_num
            except ValueError:
                continue

        # Tăng giá trị số lớn nhất lên 1 và format lại chuỗi 9 chữ số
        return f"U{max_id_num + 1:09d}"

    # =================================================
    # ĐĂNG NHẬP
    # =================================================

    def login(
        self,
        username: str,
        password: str
    ) -> str:

        # chuẩn hóa input
        username = username.strip()
        password = password.strip()

        # tìm user
        user = (
            self._user_table.get(username)
        )

        if user is None:
            return "FAILED"

        # kiểm tra password
        if not user.check_password(password):
            return "FAILED"

        # lưu user hiện tại
        self._current_user = user

        # trả role
        return user.get_role()

    # =================================================
    # ĐĂNG KÝ
    # =================================================

    def register(
        self,
        username: str,
        password: str,
        confirm_password: str
    ) -> bool:

        # chuẩn hóa dữ liệu
        username = username.strip()
        password = password.strip()
        confirm_password = (
            confirm_password.strip()
        )

        # username rỗng
        if not username:
            return False

        # password quá ngắn
        if len(password) < 6:
            return False

        # mật khẩu không khớp
        if password != confirm_password:
            return False

        # username đã tồn tại
        if self._user_table.contains(
            username
        ):
            return False

        # tạo user mới
        user = UserData(

            username=username,

            password=password,

            role="CUSTOMER",

            user_id=
            self._generate_user_id()
        )

        # insert vào hash table
        self._user_table.insert(
            username,
            user
        )

        # lưu file
        self._io_handler.save_users(
            self._user_table
        )

        return True

    # =================================================
    # ĐĂNG XUẤT
    # =================================================

    def logout(self):

        self._current_user = None

    # =================================================
    # GET CURRENT USER
    # =================================================

    def get_current_user(self):

        return self._current_user

    # =================================================
    # KIỂM TRA ĐĂNG NHẬP
    # =================================================

    def is_logged_in(self):

        return (
            self._current_user
            is not None
        )

    # =================================================
    # KIỂM TRA ADMIN
    # =================================================

    def is_admin(self):

        if self._current_user is None:
            return False

        return (
            self._current_user.get_role()
            == "ADMIN"
        )

    # =================================================
    # GET USER TABLE
    # =================================================

    def get_user_table(self):

        return self._user_table

    # =================================================
    # LẤY TOÀN BỘ USER
    # =================================================

    def get_all_users(self):

        return (
            self._user_table.get_all()
        )

