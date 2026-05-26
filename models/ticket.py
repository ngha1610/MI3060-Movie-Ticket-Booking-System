class Ticket:

    def __init__(

        self,
        ticket_id,
        user_id,
        movie_id,
        seat_id,
        status,
        showtime_id

    ):

        self.ticket_id = ticket_id

        self.user_id = user_id

        self.movie_id = movie_id

        self.seat_id = seat_id

        self.status = status

        self.showtime_id = showtime_id

    def to_dict(self):

        return {

            "ticket_id":
            self.ticket_id,

            "user_id":
            self.user_id,

            "movie_id":
            self.movie_id,

            "seat_id":
            self.seat_id,

            "status":
            self.status,

            "showtime_id":
            self.showtime_id

        }
