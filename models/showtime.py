class Showtime:

    def __init__(

        self,
        showtime_id,
        time,
        movie_id,
        rows,
        cols

    ):

        self.showtime_id = showtime_id

        self.time = time

        self.movie_id = movie_id

        self.rows = int(rows)

        self.cols = int(cols)

    def to_dict(self):

        return {

            "showtime_id":
            self.showtime_id,

            "time":
            self.time,

            "movie_id":
            self.movie_id,

            "rows":
            self.rows,

            "cols":
            self.cols

        }
