from models.entities import (MovieData)
from data_structures.linked_lists import (MovieLinkedList)
from data_structures.file_io import FileIOHandler


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

        current = self._movie_list.get_head()
        
        # Nếu chưa có bộ phim nào trong danh sách liên kết
        if current is None:
            return "M001"

        max_id_num = 0

        # Duyệt dọc Linked List để bóc tách tìm số ID lớn nhất hiện tại
        while current is not None:
            movie = current.get_data()
            movie_id_str = movie.get_movie_id()  # Ví dụ: "M000000005"
            
            try:
                # Cắt bỏ chữ 'M' ở đầu và chuyển phần còn lại thành số int
                id_num = int(movie_id_str[1:])
                if id_num > max_id_num:
                    max_id_num = id_num
            except ValueError:
                pass
                
            current = current.get_next()

        # Tăng giá trị lớn nhất lên 1 và format chuỗi 9 chữ số đi kèm chữ M
        return f"M{max_id_num + 1:03d}"

    # =================================================
    # THÊM PHIM
    # =================================================

    def add_movie(
        self,
        movie: MovieData
    ) -> bool:

        existed = (
            self._movie_list
            .search_id(
                movie.get_movie_id()
            )
        )

        if existed is not None:
            return False

        self._movie_list.add_movie(movie)

        self._io_handler.save_movies(
            self._movie_list
        )

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

    def delete_movie(
        self,
        movie_id: str,
        showtime_controller
    ) -> bool:

        # không cho xóa nếu còn suất chiếu
        showtimes = (
            showtime_controller
            .get_showtime_data()
        )

        for st in showtimes:

            if (
                st.get_movie_id()
                == movie_id
            ):
                return False

        success = (
            self._movie_list
            .remove_movie(movie_id)
        )

        if success:

            self._io_handler.save_movies(
                self._movie_list
            )

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

            result.append(
                current.get_data()
            )

            current = (
                current.get_next()
            )

        return result

    # =================================================
    # SẮP XẾP DOANH THU
    # =================================================

    def sort_movies_by_revenue(self):

        self._movie_list.sort_by_revenue_logic()

        self._io_handler.save_movies(
            self._movie_list
        )

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

