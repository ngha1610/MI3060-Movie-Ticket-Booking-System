from models.entities import (MovieData)
from data_structures.linked_lists import (MovieLinkedList)
from models.file_io import FileIOHandler


# =====================================================
# MOVIE CONTROLLER
# =====================================================

class MovieController:

    def __init__(
        self,
        io_handler: FileIOHandler
    ):

        self._io_handler = io_handler

        self._movie_list = MovieLinkedList()

        self._io_handler.load_movies(
            self._movie_list
        )
    
    def generate_movie_id(self):
        import time
        # Lấy thời gian thực tính bằng giây (Ví dụ: 1717568320)
        unique_timestamp = int(time.time())
        
        # Ghép chữ M với chuỗi thời gian -> Đảm bảo 100% ID độc nhất
        return f"M{unique_timestamp}"
    # =================================================
    # THÊM PHIM
    # =================================================

    def add_movie(self, movie: MovieData) -> bool:
        
        # Kiểm tra trùng tên phim (Ném lỗi thay vì print)
        if self.search_by_title(movie.get_title()) is not None:
            raise ValueError("Tên phim này đã tồn tại trong hệ thống!")

        # Kiểm tra trùng ID
        existed = self._movie_list.search_id(movie.get_movie_id())
        if existed is not None:
            return False

        # Thêm phim
        self._movie_list.add_movie(movie)
        self._io_handler.save_movies(self._movie_list)

        return True

    # =================================================
    # CẬP NHẬT PHIM
    # =================================================

    def update_movie(
        self,
        movie_id: str,
        title: str,
        genre: str,
        duration: int,
        description: str,
        base_price: float,
        poster_path: str
    ) -> bool:

        node = (
            self._movie_list
            .search_id(movie_id)
        )

        if node is None:
            return False
        
        existing_node = self.search_by_title(title)
        if existing_node is not None:
            existing_movie = existing_node.get_data()
            # Chỉ báo lỗi nếu tìm thấy phim KHÁC trùng tên
            # (không phải chính bộ phim đang được sửa)
            if existing_movie.get_movie_id() != movie_id:
                raise ValueError("Tên phim này đã tồn tại trong hệ thống!")

        movie = node.get_data()

        # cập nhật dữ liệu
        movie.set_title(title)

        movie.set_genre(genre)

        movie.set_duration(duration)

        movie.set_description(
            description
        )

        movie.set_base_price(
            base_price
        )

        movie.set_poster_path(
            poster_path
        )

        # lưu file
        self._io_handler.save_movies(
            self._movie_list
        )

        return True

    # =================================================
    # XÓA PHIM
    # =================================================

    def delete_movie(self, movie_id: str) -> bool:
        success = self._movie_list.remove_movie(movie_id)
        if success:
            self._io_handler.save_movies(self._movie_list)
        return success

    # =================================================
    # TÌM KIẾM
    # =================================================

    def search_by_title(
        self,
        title: str
    ):

        return (
            self._movie_list
            .search_movie(title)
        )

    def search_by_id(
        self,
        movie_id: str
    ):

        return (
            self._movie_list
            .search_id(movie_id)
        )

    # =================================================
    # LẤY DỮ LIỆU
    # =================================================

    def get_movie_list(self):

        return self._movie_list

    def get_movie_data(self):

        result = []

        current = (
            self._movie_list
            .get_head()
        )

        while current is not None:

            result += [current.get_data()]

            current = (
                current.get_next()
            )

        return result

    # =================================================
    # KIỂM TRA TỒN TẠI
    # =================================================

    def movie_exists(
        self,
        movie_id: str
    ) -> bool:

        return (
            self._movie_list
            .search_id(movie_id)
            is not None
        )
    
    def save_data(self):
        """Cho phép các controller khác yêu cầu lưu file phim"""
        self._io_handler.save_movies(self._movie_list)

    # =================================================
    # QUẢN LÝ CẤU HÌNH GIAO DIỆN
    # =================================================

    def load_ui_config(self):
        """Gọi xuống tầng IO để tải cấu hình hiển thị sảnh chính"""
        return self._io_handler.load_ui_config()
        
    def save_ui_config(self, slider_titles, list_titles):
        """Gọi xuống tầng IO để lưu cấu hình hiển thị sảnh chính"""
        self._io_handler.save_ui_config(slider_titles, list_titles)


