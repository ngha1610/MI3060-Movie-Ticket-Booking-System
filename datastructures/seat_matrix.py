class SeatMatrix:

    def __init__(self, rows, cols):

        self.rows = rows

        self.cols = cols

        self.matrix = []

        for _ in range(rows):

            row = []

            for _ in range(cols):

                row.append("O")

            self.matrix.append(row)

    def book(self, seat_id):

        row = ord(seat_id[0]) - 65

        col = int(seat_id[1:]) - 1

        if self.matrix[row][col] == "X":

            return False

        self.matrix[row][col] = "X"

        return True

    def cancel(self, seat_id):

        row = ord(seat_id[0]) - 65

        col = int(seat_id[1:]) - 1

        self.matrix[row][col] = "O"

    def get_matrix(self):

        return self.matrix

    def available_count(self):

        count = 0

        for row in self.matrix:

            for seat in row:

                if seat == "O":

                    count += 1

        return count
