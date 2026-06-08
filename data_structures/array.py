# data_structures/custom_array.py

class Array2D:
    def __init__(self, rows, cols, default_value=0):
        self.rows = rows
        self.cols = cols
        self.data = []
     
        total_elements = rows * cols
        count = 0
        while count < total_elements:
            self.data += [default_value]
            count += 1

    def get_val(self, r, c):  
        return self.data[r * self.cols + c]

    def set_val(self, r, c, value):
        self.data[r * self.cols + c] = value