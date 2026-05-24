class SeatMatrix:
    def __init__(self, rows: int, cols: int) -> None:
        self.rows = rows
        self.cols = cols
        self.seats = [[0 for _ in range(cols)] for _ in range(rows)]

    def check_status(self, r: int, c: int) -> int:
        return self.seats[r][c]

    def book_seat(self, r: int, c: int) -> bool:
        if self.seats[r][c] == 0:
            self.seats[r][c] = 1
            return True
        return False

    def release_seat(self, r: int, c: int) -> None:
        self.seats[r][c] = 0


class BookingController:
    def __init__(self, ticket_db: TicketLinkedList, seat_matrix: SeatMatrix) -> None:
        self.ticket_db = ticket_db
        self.seat_matrix = seat_matrix

    def process_booking(self, user: UserData, movie: MovieData, r: int, c: int) -> bool:
        if self.seat_matrix.book_seat(r, c):
            ticket_id = f"T_{user.username}_{movie.movie_id}_{r}{c}"
            seat_id = f"{chr(65 + r)}{c + 1}"
            new_ticket = TicketData(ticket_id, user.username, movie.movie_id, seat_id, "Active", "ST_01")
            
            self.ticket_db.add_ticket(new_ticket)
            return True
        return False

    def cancel_booking(self, user_id: str, ticket_id: str) -> bool:
        current = self.ticket_db.head
        
        while current is not None:
            if current.data.ticket_id == ticket_id and current.data.user_id == user_id and current.data.status == "Active":
                current.data.status = "Cancelled"
                
                seat_str = current.data.seat_id
                r = ord(seat_str[0]) - 65
                c = int(seat_str[1:]) - 1
                
                self.seat_matrix.release_seat(r, c)
                return True
            current = current.get_next()
            
        return False