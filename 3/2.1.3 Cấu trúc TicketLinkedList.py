class TicketLinkedList:
    def __init__(self) -> None:
        self.head = None

    def add_ticket(self, ticket: TicketData) -> None:
        new_node = TicketNode(ticket)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.get_next() is not None:
                current = current.get_next()
            current.set_next(new_node)

    def traverse(self) -> None:
        current = self.head
        while current is not None:
            print(f"Mã vé: {current.data.ticket_id} | Khách hàng: {current.data.user_id} | "
                  f"Phim: {current.data.movie_id} | Ghế: {current.data.seat_id} | Trạng thái: {current.data.status}")
            current = current.get_next()

    def remove_ticket(self, ticket_id: str) -> bool:
        current = self.head
        previous = None
        
        while current is not None:
            if current.data.ticket_id == ticket_id:
                if previous is None:
                    self.head = current.get_next()
                else:
                    previous.set_next(current.get_next())
                return True
            previous = current
            current = current.get_next()
            
        return False