class Node:
    def __init__(self, data):
        self.data = data  
        self.next = None  

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def get_next(self):
        return self.next

    def set_next(self, next_node):
        self.next = next_node

class UserNode(Node):
    pass

class TicketNode(Node):
    pass

class MovieNode(Node):
    pass

class ShowtimeNode(Node):
    pass

class RoomNode(Node):
    pass