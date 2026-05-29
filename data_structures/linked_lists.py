from models.entities import TicketData, MovieData, Showtime, Room
from data_structures.nodes import TicketNode, MovieNode, ShowtimeNode, RoomNode

class TicketLinkedList:

    def __init__(self):

        self._head = None

    def add_ticket(self, ticket: TicketData):

        new_node = TicketNode(ticket)

        if self._head is None:

            self._head = new_node

            return

        current = self._head

        while current.get_next() is not None:

            current = current.get_next()

        current.set_next(new_node)

    def find_ticket(self, ticket_id):

        current = self._head

        while current is not None:

            ticket = current.get_data()

            if (
                ticket.get_ticket_id()
                == ticket_id
            ):

                return current

            current = current.get_next()

        return None

    def remove_ticket(self, ticket_id):

        current = self._head

        prev = None

        while current is not None:

            ticket = current.get_data()

            if (
                ticket.get_ticket_id()
                == ticket_id
            ):

                if prev is None:

                    self._head = current.get_next()

                else:

                    prev.set_next(current.get_next())

                return True

            prev = current

            current = current.get_next()

        return False

    def find_by_user(self, user_id):

        result = []

        current = self._head

        while current is not None:

            ticket = current.get_data()

            if ticket.get_user_id() == user_id:

                result.append(ticket)

            current = current.get_next()

        return result
            
    def get_head(self):
        return self._head

class MovieLinkedList:

    def __init__(self):

        self._head = None

    def add_movie(self, movie: MovieData):

        new_node = MovieNode(movie)

        if self._head is None:

            self._head = new_node

            return

        current = self._head

        while current.get_next() is not None:

            current = current.get_next()

        current.set_next(new_node)

    def search_movie(self, title):

        current = self._head

        while current is not None:

            movie = current.get_data()

            if movie.get_title().lower() == title.lower():

                return current

            current = current.get_next()

        return None

    def search_id(self, movie_id):

        current = self._head

        while current is not None:

            movie = current.get_data()

            if (
                movie.get_movie_id()
                == movie_id
            ):

                return current

            current = current.get_next()

        return None
    
    def remove_movie(self, movie_id):

        current = self._head

        prev = None

        while current is not None:

            movie = current.get_data()

            if (
                movie.get_movie_id()
                == movie_id
            ):

                if prev is None:

                    self._head = current.get_next()

                else:

                    prev.set_next(current.get_next())

                return True

            prev = current

            current = current.get_next()

        return False
    
    def sort_by_revenue_logic(self):

        if (
            self._head is None
            or self._head.get_next() is None
        ):
            return

        swapped = True

        while swapped:

            swapped = False

            current = self._head

            while current.get_next() is not None:

                next_node = current.get_next()

                current_movie = current.get_data()

                next_movie = next_node.get_data()

                if (
                    current_movie.get_revenue()
                    < next_movie.get_revenue()
                ):

                    temp = current_movie

                    current.set_data(next_movie)

                    next_node.set_data(temp)

                    swapped = True

                current = current.get_next()
    
    def get_head(self):
        return self._head

class ShowtimeLinkedList:

    def __init__(self):

        self._head = None

    def add_showtime(self, st: Showtime):

        new_node = ShowtimeNode(st)

        if self._head is None:

            self._head = new_node

            return

        current = self._head

        while current.get_next() is not None:

            current = current.get_next()

        current.set_next(new_node)

    def find_showtime(self, showtime_id):

        current = self._head

        while current is not None:

            st = current.get_data()

            if (
                st.get_showtime_id()
                == showtime_id
            ):

                return current

            current = current.get_next()

        return None

    def find_by_movie(self, movie_id):

        result = []

        current = self._head

        while current is not None:

            st = current.get_data()

            if (
                st.get_movie_id()
                == movie_id
            ):

                result.append(st)

            current = current.get_next()

        return result

    def remove_showtime(self, showtime_id):

        current = self._head

        prev = None

        while current is not None:

            st = current.get_data()

            if (
                st.get_showtime_id()
                == showtime_id
            ):

                if prev is None:

                    self._head = current.get_next()

                else:

                    prev.set_next(current.get_next())

                return True

            prev = current

            current = current.get_next()

        return False
    
    def get_head(self):
        return self._head
    
class RoomLinkedList:

    def __init__(self):

        self._head = None

    def add_room(self, room: Room):

        new_node = RoomNode(room)

        if self._head is None:

            self._head = new_node

            return

        current = self._head

        while current.get_next() is not None:

            current = current.get_next()

        current.set_next(new_node)

    def find_room(self, room_id):

        current = self._head

        while current is not None:

            room = current.get_data()

            if (
                room.get_room_id()
                == room_id
            ):

                return current

            current = current.get_next()

        return None

    def remove_room(self, room_id):

        current = self._head

        prev = None

        while current is not None:

            room = current.get_data()

            if (
                room.get_room_id()
                == room_id
            ):

                if prev is None:

                    self._head = current.get_next()

                else:

                    prev.set_next(current.get_next())

                return True

            prev = current

            current = current.get_next()

        return False

    def get_head(self):
        return self._head
