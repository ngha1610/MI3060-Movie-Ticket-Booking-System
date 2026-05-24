class MovieLinkedList:
    def __init__(self) -> None:
        self.head = None

    def add_movie(self, movie: MovieData) -> None:
        new_node = MovieNode(movie)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.get_next() is not None:
                current = current.get_next()
            current.set_next(new_node)

    def search_movie_by_title(self, target_title: str) -> MovieNode:
        current = self.head
        while current is not None:
            if current.data.title == target_title:
                return current
            current = current.get_next()
        return None

    def delete_movie(self, movie_id: str) -> bool:
        current = self.head
        previous = None
        
        while current is not None:
            if current.data.movie_id == movie_id:
                if previous is None:
                    self.head = current.get_next()
                else:
                    previous.set_next(current.get_next())
                return True
            previous = current
            current = current.get_next()
            
        return False

    def sort_by_revenue_logic(self) -> None:
        current = self.head
        while current is not None:
            node_max = current
            iterator = current.get_next()
            
            while iterator is not None:
                if iterator.data.revenue > node_max.data.revenue:
                    node_max = iterator
                iterator = iterator.get_next()
                
            if node_max != current:
                current.data, node_max.data = node_max.data, current.data
                
            current = current.get_next()