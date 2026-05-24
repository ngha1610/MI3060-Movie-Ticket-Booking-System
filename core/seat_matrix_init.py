def initialize_seat_matrix(rows: int, cols: int) -> list:
    matrix = []
    
    for r in range(rows):
        row_list = []
        for c in range(cols):
            row_list.append(0)
        matrix.append(row_list)
        
    return matrix