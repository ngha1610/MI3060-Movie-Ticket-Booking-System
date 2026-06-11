import threading

from models.entities import UserData
from data_structures.hash_table import UserHashTable
from models.file_io import FileIOHandler

# =====================================================
# AUTH CONTROLLER: BỘ ĐIỀU KHIỂN XÁC THỰC NGƯỜI DÙNG
# =====================================================


class AuthController:
    
    def __init__(
        self,
        io_handler: FileIOHandler
    ):
        self._io_handler = io_handler
        self._user_table = UserHashTable()
        self._io_handler.load_users(self._user_table)
        self._current_user = None

        self._auth_lock = threading.Lock()
    # =================================================
    # TẠO USER ID: DUYỆT BẢNG BĂM ĐỂ TÌM ID LỚN NHẤT
    # =================================================
    def _generate_user_id(self):
        all_users = self._user_table.get_all()
        
        if not all_users:
            return "U000000001"

        max_id_num = 0
        for user in all_users:
            user_id_str = user.get_user_id() 
            try:
                # Cắt chuỗi loại bỏ ký tự 'U' ở đầu
                id_str = ""
                idx = 0
                for char in user_id_str:
                    if idx > 0: id_str += char
                    idx += 1
                
                id_num = int(id_str)
                if id_num > max_id_num:
                    max_id_num = id_num
            except ValueError:
                continue

        return f"U{max_id_num + 1:09d}"

    # =================================================
    # ĐĂNG NHẬP
    # =================================================
    def login(self, username: str, password: str) -> str:
        # Chuẩn hóa dự liệu đầu vào
        username = username.strip() if username else ""
        password = password.strip() if password else ""

        user = self._user_table.get(username)

        if user is None:
            return "FAILED"

        if not user.check_password(password):
            return "FAILED"

        self._current_user = user
        return user.get_role()

    # =================================================
    # ĐĂNG KÝ
    # =================================================
    def register(self, username: str, password: str, confirm_password: str) -> bool:
        with self._auth_lock:
            # Chuẩn hóa dữ liệu đầu vào
            username = username.strip() if username else ""
            password = password.strip() if password else ""
            confirm_password = confirm_password.strip() if confirm_password else ""

            if not username:
                return False

            # Kiểm tra ràng buộc mật khẩu (tối thiểu 6 ký tự)
            if len(password) < 6:
                return False

            if password != confirm_password:
                return False

            # Tra cứu độ phức tạp O(1) qua bảng băm
            if self._user_table.contains(username):
                return False

            user = UserData(
                username=username,
                password=password,
                role="CUSTOMER",
                user_id=self._generate_user_id()
            )

            # Thêm vào cấu trúc dữ liệu và đồng bộ xuống tệp
            self._user_table.insert(username, user)
            self._io_handler.save_users(self._user_table)

            return True

    # =================================================
    # QUẢN LÝ PHIÊN HOẠT ĐỘNG
    # =================================================
    def logout(self):
        self._current_user = None

    def get_current_user(self):
        return self._current_user

    def is_logged_in(self):
        return self._current_user is not None

    def is_admin(self):
        if self._current_user is None: return False
        return self._current_user.get_role() == "ADMIN"

    def get_user_table(self):
        return self._user_table

    def get_all_users(self):
        return self._user_table.get_all()