CLASS DIAGRAM
TẦNG 1
package "Presentation Layer" {
    class MainMenu {
        + display_menu(): void
        + handle_login(): void
        + handle_register(): void
    }

    class AdminUI {
        + manage_movie(): void      
        + manage_showtime(): void   
        + manage_room(): void       
        + view_statistics(): void
        + handle_logout(): void     //  Để thoát trạng thái Admin, về MainMenu
    }

    class CustomerUI {
        - current_user: UserData    
        + view_movie_list(): void   
        + search_movie(): void
        + view_movie_detail(): void 
        
        + select_seat(): void
        + select_showtime(): void   
        
        + book_ticket(): void
        + cancel_ticket(): void
        
        + view_history(): void
        + view_showtimes(): void    
        + print_ticket(): void      
        + handle_logout(): void     //  Để thoát trạng thái Customer, về MainMenu
    }
}



TẦNG 2
package "Business Logic Layer" {
    class AuthController {    
        - user_table: UserHashTable  
        + login(user: String, pass: String): String  // Trả về "ADMIN", "CUSTOMER" hoặc "FAILED" để UI chuyển hướng
        + register(user: String, pass: String): bool    
        + logout(): void 
        + check_role(username: String): String       // Kiểm tra quyền của tài khoản
    }

    class AdminController {    
        + calculate_revenue(): double
        + count_movies(): int
        + count_tickets(): int
        + get_top_movie(): String
        + generate_report(): void     
    }

    class MovieController {
        - movie_list: MovieLinkedList 
        
        + add_movie(movie: MovieData): bool
        + update_movie(movie_id: String, new_data: MovieData): bool
        + delete_movie(movie_id: String): bool

        + search_by_title(title: String): MovieNode
        + sort_by_revenue(): void     
        + check_movie_booking_status(title: String): bool
        + get_movie_list(): MovieLinkedList }

    class RoomController { Lớp điều phối phòng chiếu bị thiếu
        - room_list: RoomLinkedList
        + add_room(room: Room): bool
        + delete_room(room_id: String): bool
        + get_room_list(): RoomLinkedList
        + find_room(room_id: String): RoomNode
    }

    class ShowtimeController {
        - showtime_list: ShowtimeLinkedList*
       
        + add_showtime(st: Showtime): bool
        + update_showtime(showtime_id: String, new_st: Showtime): bool
        + delete_showtime(showtime_id: String): bool
        + find_showtime(showtime_id: String): ShowtimeNode*
        
        + get_movie_showtime(movie_id: String): String   
        + check_seat_status(showtime_id: String, r: int, c: int): bool  
        + reserve_seat(showtime_id: String, r: int, c: int): bool   
        + release_seat(showtime_id: String, r: int, c: int): void   
    } 

    class BookingController {    
        - ticket_list: TicketLinkedList*
        - showtime_controller: ShowtimeController // Chuyển sang dạng con trỏ đối tượng điều phối
        
        + process_booking(user: UserData, movie: MovieData, row: int, col: int): bool
        + cancel_booking(user_id: String, ticket_id: String): bool
        + find_ticket(ticket_id: String): String  
        + get_booking_history(user_id: String): String  
        + generate_ticket_info(ticket_id: String): String  
    }
}




TẦNG 3
package "Data Access & Structures" {
    class FileIOHandler {   
        + load_users(table: UserHashTable&): void
        + save_users(table: UserHashTable&): void
        + load_movies(list: MovieLinkedList&): void
        + save_movies(list: MovieLinkedList&): void
        + load_tickets(list: TicketLinkedList&): void
        + save_tickets(list: TicketLinkedList&): void
        + load_showtimes(list: ShowtimeLinkedList&): void 
        + save_showtimes(list: ShowtimeLinkedList&): void 
        + load_rooms(list: RoomLinkedList&): void     // Đọc ghi dữ liệu phòng chiếu
        + save_rooms(list: RoomLinkedList&): void     //Đọc ghi dữ liệu phòng chiếu
    }

    class UserNode {
        - data: UserData
        - next: UserNode* 
        + get_data(): UserData
        + set_data(d: UserData): void
        + get_next(): UserNode*
        + set_next(nxt: UserNode*): void
    }
    
    class TicketNode {
        - data: TicketData  
        - next: TicketNode* 
        + get_data(): TicketData
        + get_next(): TicketNode*
    }

    class MovieNode {
        - data: MovieData  
        - next: MovieNode
        + get_data(): MovieData
        + get_next(): MovieNode*
    }

    class ShowtimeNode { 
         - data: Showtime 
         - next: ShowtimeNode*
         + get_data(): Showtime
         + get_next(): ShowtimeNode*
    } 

    class RoomNode { 
          - data: Room // Đồng bộ đặt tên thuộc tính là data cho giống các Node khác
          - next: RoomNode*
          + get_data(): Room
          + get_next(): RoomNode*
    }

    class UserHashTable {
        - table: UserNode*[ ] // Mảng các con trỏ đầu danh sách liên kết vòng (Chaining)
        - SIZE: int          //  Kích thước mảng băm

        + hash_function(key: String): int
        + insert(username: String, value: UserData): void    
        + get(username: String): UserData
        + contains(username: String): bool 
        + remove(username: String): bool  
        + display(): void
    }

    class TicketLinkedList {
        - head: TicketNode*
        + add_ticket(ticket: TicketData): void
        + traverse(): void
        + remove_ticket(ticket_id: String): bool
        + find_ticket(ticket_id: String): TicketNode* 
        + find_by_user(user_id: String): TicketLinkedList* }

    class MovieLinkedList {
        - head: MovieNode*
        + add_movie(movie: MovieData): void
        + remove_movie(movie_id: String): bool 
        + search_movie(title: String): MovieNode* + search_id(movie_id: String): MovieNode* 
        + sort_by_revenue_logic(): void
        + traverse(): void
    }

    class ShowtimeLinkedList { 
        - head: ShowtimeNode* + add_showtime(st: Showtime): void 
        + find_showtime(showtime_id: String): ShowtimeNode* + find_by_movie(movie_id: String): ShowtimeLinkedList* 
        + traverse(): void 
        + remove_showtime(showtime_id: String): bool // 
    } 

    class RoomLinkedList {
        - head: RoomNode* + add_room(room: Room): void 
        + remove_room(room_id: String): bool 
        + find_room(room_id: String): RoomNode* + traverse(): void 
    }
}


TẦNG 4:
package "Data Models" {
    class UserData {
        - username: String
        - password: String
        - role: String           
        - user_id: String
    }

    class TicketData {
        - ticket_id: String
        - user_id: String
        - movie_id: String
        - seat_id: String
        - status: String
        - showtime_id: String
        - room_id: String
        - price: double  //để customer xem được giá vé ở mục lịch sử
    }

    class MovieData {
        - movie_id: String
        - title: String
        - genre: String
        - duration: int        
        - description: String    
        - revenue: double  //doanh thu
        - base_price: double   //giá sàn của phim
    }

    class SeatMatrix {
        - seats: int[ ][ ]
        - rows: int         //Số hàng ghế của phòng
        - cols: int         // Số cột ghế của phòng
        
        + check_status(r: int, c: int): int
        + reserve_seat(r: int, c: int): bool  
        + book_seat(r: int, c: int): bool
        + release_seat(r: int, c: int): void
        + display_matrix(): void
    }

    class Showtime { 
        - showtime_id: String 
        - movie_id: String 
        - start_time: String 
        - room_id: String 
        - seat_matrix: SeatMatrix 
        + get_available_seats(): int 
        + display_showtime_info(): void 
    } 

    class Room {
        - room_id: String
        - room_name: String
        - capacity: int
    }
}


