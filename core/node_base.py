class Node:
    def __init__(self) -> None:
        self.next_node = None

    def set_next(self, next_node: 'Node') -> None:
        self.next_node = next_node

    def get_next(self) -> 'Node':
        return self.next_node


class UserData:
    def __init__(self, username: str, password: str, role: str) -> None:
        self.username = username
        self.password = password
        self.role = role

class UserNode(Node):
    def __init__(self, user_data: UserData) -> None:
        super().__init__()
        self.data = user_data

    def get_user_info(self) -> tuple:
        return (self.data.username, self.data.password, self.data.role)


class MovieData:
    def __init__(self, movie_id: str, title: str, genre: str, revenue: float = 0.0) -> None:
        self.movie_id = movie_id
        self.title = title
        self.genre = genre
        self.revenue = revenue

class MovieNode(Node):
    def __init__(self, movie_data: MovieData) -> None:
        super().__init__()
        self.data = movie_data


class TicketData:
    def __init__(self, ticket_id: str, user_id: str, movie_id: str, seat_id: str, status: str, showtime_id: str) -> None:
        self.ticket_id = ticket_id
        self.user_id = user_id
        self.movie_id = movie_id
        self.seat_id = seat_id
        self.status = status
        self.showtime_id = showtime_id

class TicketNode(Node):
    def __init__(self, ticket_data: TicketData) -> None:
        super().__init__()
        self.data = ticket_data