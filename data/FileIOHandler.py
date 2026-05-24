import os

# ---------------------------------------------------------
# TẦNG 3: DATA ACCESS & STRUCTURES LAYER - FileIOHandler
# ---------------------------------------------------------
class FileIOHandler:
    def __init__(self, data_dir="data"):
        """
        Khởi tạo bộ xử lý file, tự động tạo thư mục chứa dữ liệu nếu chưa có.
        """
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        # Đã đổi thành đuôi .csv theo yêu cầu
        self.users_file = os.path.join(self.data_dir, "users.csv")
        self.movies_file = os.path.join(self.data_dir, "movies.csv")
        self.tickets_file = os.path.join(self.data_dir, "tickets.csv")

    # ==========================================
    # 1. QUẢN LÝ TÀI KHOẢN (USERS)
    # ==========================================
    def load_users(self, user_hash_table) -> None:
        if not os.path.exists(self.users_file):
            return
            
        with open(self.users_file, 'r', encoding='utf-8') as f:
            next(f, None)  # Bỏ qua dòng header đầu tiên
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(',')
                if len(parts) == 3:
                    username, password, role = parts
                    # Giả định UserData đã được định nghĩa ở Tầng 4
                    user_data = UserData(username, password, role) 
                    user_hash_table.insert(username, user_data)

    def save_users(self, user_hash_table) -> None:
        with open(self.users_file, 'w', encoding='utf-8') as f:
            f.write("username,password,role\n")  # Ghi lại header trước
            for i in range(user_hash_table.size):
                current_node = user_hash_table.table[i]
                while current_node is not None:
                    user = current_node.data
                    f.write(f"{user.username},{user.password},{user.role}\n")
                    current_node = current_node.next_node

    # ==========================================
    # 2. QUẢN LÝ DANH MỤC PHIM (MOVIES)
    # ==========================================
    def load_movies(self, movie_linked_list) -> None:
        if not os.path.exists(self.movies_file):
            return
            
        with open(self.movies_file, 'r', encoding='utf-8') as f:
            next(f, None)  # Bỏ qua dòng header đầu tiên
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(',')
                if len(parts) == 4:
                    movie_id, title, genre, revenue = parts
                    movie_data = MovieData(movie_id, title, genre, revenue)
                    movie_linked_list.add_movie(movie_data)

    def save_movies(self, movie_linked_list) -> None:
        with open(self.movies_file, 'w', encoding='utf-8') as f:
            f.write("movie_id,title,genre,revenue\n")  # Ghi lại header trước
            current_node = movie_linked_list.head
            while current_node is not None:
                movie = current_node.data
                f.write(f"{movie.movie_id},{movie.title},{movie.genre},{movie.revenue}\n")
                current_node = current_node.next_node

    # ==========================================
    # 3. QUẢN LÝ VÉ GIAO DỊCH (TICKETS)
    # ==========================================
    def load_tickets(self, ticket_linked_list) -> None:
        if not os.path.exists(self.tickets_file):
            return
            
        with open(self.tickets_file, 'r', encoding='utf-8') as f:
            next(f, None)  # Bỏ qua dòng header đầu tiên
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(',')
                if len(parts) == 6:
                    ticket_id, user_id, movie_id, seat_id, status, showtime_id = parts
                    ticket_data = TicketData(ticket_id, user_id, movie_id, seat_id, status, showtime_id)
                    ticket_linked_list.add_ticket(ticket_data)

    def save_tickets(self, ticket_linked_list) -> None:
        with open(self.tickets_file, 'w', encoding='utf-8') as f:
            f.write("ticket_id,user_id,movie_id,seat_id,status,showtime_id\n")  # Ghi lại header trước
            current_node = ticket_linked_list.head
            while current_node is not None:
                ticket = current_node.data
                f.write(f"{ticket.ticket_id},{ticket.user_id},{ticket.movie_id},{ticket.seat_id},{ticket.status},{ticket.showtime_id}\n")
                current_node = current_node.next_node