from models.entities import UserData
from data_structures.nodes import UserNode

class UserHashTable:

    def __init__(self, size=101):

        self._SIZE = size
        self._table = [None] * self._SIZE

    def hash_function(self, key: str) -> int:

        hash_val = 0

        for char in key:

            hash_val = (
                hash_val * 31 + ord(char)
            ) % self._SIZE

        return hash_val

    def insert(self, username: str, value: UserData) -> None:

        index = self.hash_function(username)

        new_node = UserNode(value)

        # bucket trống
        if self._table[index] is None:

            self._table[index] = new_node

            new_node.set_next(new_node)

            return

        head = self._table[index]

        current = head

        while True:

            if (
                current.get_data().get_username()
                == username
            ):

                current.set_data(value)

                return

            current = current.get_next()

            if current == head:
                break
            
        new_node.set_next(head.get_next())

        head.set_next(new_node)

    def get(self, username: str):

        index = self.hash_function(username)

        head = self._table[index]

        if head is None:
            return None

        current = head

        while True:

            if (
                current.get_data().get_username()
                == username
            ):

                return current.get_data()

            current = current.get_next()

            if current == head:
                break

        return None

    def contains(self, username: str) -> bool:

        return self.get(username) is not None

    def remove(self, username: str) -> bool:

        index = self.hash_function(username)

        head = self._table[index]

        if head is None:
            return False

        if (
            head.get_data().get_username()
            == username
        ):
            if head.get_next() == head:

                self._table[index] = None

            else:

                prev = head

                while prev.get_next() != head:

                    prev = prev.get_next()

                prev.set_next(head.get_next())

                self._table[index] = head.get_next()

            return True

        prev = head

        current = head.get_next()

        while current != head:

            if (
                current.get_data().get_username()
                == username
            ):

                prev.set_next(current.get_next())

                return True

            prev = current

            current = current.get_next()

        return False

    def display(self):

        print("\n========== USER HASH TABLE ==========")

        for i in range(self._SIZE):

            print(f"Bucket {i}: ", end="")

            head = self._table[i]

            if head is None:

                print("Empty")

            else:

                current = head

                while True:

                    username = (
                        current
                        .get_data()
                        .get_username()
                    )

                    print(f"[{username}] -> ", end="")

                    current = current.get_next()

                    if current == head:
                        break

                print("(loop)")

        print("=====================================\n")
        
    def get_table(self):
        return self._table
    
    def get_all(self):

        result = []

        for bucket in self._table:

            if bucket is None:
               continue

            current = bucket
            visited = False

            while True:

                if current == bucket and visited:
                   break

                visited = True

                result.append(current.get_data())

                current = current.get_next()

        return result

