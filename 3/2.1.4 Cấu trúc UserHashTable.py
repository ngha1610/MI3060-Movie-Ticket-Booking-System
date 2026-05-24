class UserHashTable:
    def __init__(self, size: int) -> None:
        self.size = size
        self.table = [None] * self.size

    def hash_function(self, key: str) -> int:
        total_ascii = sum(ord(char) for char in key)
        return total_ascii % self.size

    def insert(self, key: str, value: UserData) -> None:
        index = self.hash_function(key)
        new_node = UserNode(value)
        
        new_node.set_next(self.table[index])
        self.table[index] = new_node

    def get(self, key: str) -> UserData:
        index = self.hash_function(key)
        current = self.table[index]
        
        while current is not None:
            if current.data.username == key:
                return current.data
            current = current.get_next()
            
        return None