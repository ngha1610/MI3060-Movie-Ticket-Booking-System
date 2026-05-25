# datastructures/seat_matrix.py

class SeatMatrix:

    def __init__(self,rows=5,cols=8):

        self.rows=rows
        self.cols=cols

        self.seats=[["O" for _ in range(cols)]
                    for _ in range(rows)]

    def book_seat(self,row,col):

        if self.seats[row][col]=="O":

            self.seats[row][col]="X"
            return True

        return False


    def get_layout(self):

        return self.seats
